from flask import Flask, render_template, request, redirect, url_for
import os, sys, math, json
from model.job_match import process_files  # your existing function

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LATEST_RESULTS'] = []


def match_to_percent(raw):
    """
    Convert possible raw match (string, number, list, tuple, dict) to percent (0..100).
    If raw is numeric in 0..1, scale up to 0..100.
    """
    # If it's a dict/list/tuple, try to extract a numeric inside recursively
    if raw is None:
        return 0.0

    # If it's a list/tuple, try first numeric element
    if isinstance(raw, (list, tuple)):
        for item in raw:
            p = match_to_percent(item)
            if p is not None and p != 0.0:
                return p
        return 0.0

    # If it's a dict, try common numeric keys
    if isinstance(raw, dict):
        # try these keys in order
        keys_try = ['match', 'score', 'similarity', 'cosine', 'final_score', 'value', 'match_score', 'score_value']
        for k in keys_try:
            if k in raw:
                return match_to_percent(raw[k])
        # fallback: try any numeric value in dict
        for v in raw.values():
            p = match_to_percent(v)
            if p is not None and p != 0.0:
                return p
        return 0.0

    # If it's a string, try to extract a number
    if isinstance(raw, str):
        s = raw.strip()
        # empty
        if s == '':
            return 0.0
        # try to find first number pattern
        import re
        m = re.search(r'-?\d+(\.\d+)?', s)
        if m:
            try:
                val = float(m.group(0))
            except:
                return 0.0
        else:
            return 0.0
        # continue to numeric handling below with val
        n = val
    else:
        # assume it's numeric-like
        try:
            n = float(raw)
        except Exception:
            return 0.0

    # now n is numeric
    if math.isnan(n) or math.isinf(n):
        return 0.0

    # if in 0..1 range, scale up
    if 0 < n <= 1:
        n = n * 100.0

    # clamp and round
    n = max(0.0, min(100.0, n))
    return round(n, 2)


def extract_filename(raw_item):
    """
    Try to extract a filename or id string for display from the raw item.
    """
    if raw_item is None:
        return ""
    if isinstance(raw_item, dict):
        for k in ['filename', 'file', 'name', 'id', 'fname', 'file_name']:
            if k in raw_item and raw_item[k]:
                return str(raw_item[k])
        # fallback: try to use first string value
        for v in raw_item.values():
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    if isinstance(raw_item, (list, tuple)):
        # try first element which looks like filename
        for v in raw_item:
            if isinstance(v, str) and v.strip().lower().endswith(('.pdf', '.docx', '.txt')):
                return v
        # fallback to string of first element
        return str(raw_item[0]) if raw_item else ""
    if isinstance(raw_item, str):
        return raw_item
    # fallback to str()
    return str(raw_item)


def normalize_raw_results(raw_results):
    """
    Convert raw_results returned by process_files into a list of dicts
    with keys: filename, match (percent numeric)
    """
    normalized = []
    # If raw_results is not iterable/dict-like, wrap it
    if raw_results is None:
        return normalized

    # If process_files returned a dict with results inside, try common keys
    if isinstance(raw_results, dict) and not isinstance(raw_results, list):
        # look for common container keys
        for k in ['results', 'data', 'matches', 'items', 'resumes']:
            if k in raw_results and isinstance(raw_results[k], (list, tuple)):
                raw_results = raw_results[k]
                break

    # At this point we expect raw_results to be iterable
    try:
        iterator = iter(raw_results)
    except TypeError:
        # not iterable, wrap
        raw_results = [raw_results]

    # iterate and map
    for item in raw_results:
        # default filename guess
        filename = extract_filename(item)

        # try common shapes
        match_candidate = None
        if isinstance(item, dict):
            # direct match key
            for k in ['match', 'score', 'similarity', 'cosine', 'final_score', 'value', 'match_score', 'score_value']:
                if k in item:
                    match_candidate = item[k]
                    break
            # sometimes function returns {"file":"x", "meta":{"score":0.6}}
            # try to find numeric in nested dicts
            if match_candidate is None:
                # shallow search numeric values
                for v in item.values():
                    if isinstance(v, (int, float)):
                        match_candidate = v
                        break
                    if isinstance(v, str):
                        # check if string contains number
                        import re
                        if re.search(r'-?\d+(\.\d+)?', v):
                            match_candidate = v
                            break
                    # nested dict/list
                    if isinstance(v, (dict, list, tuple)):
                        # let match_to_percent dig in
                        cand = match_to_percent(v)
                        if cand and cand > 0:
                            match_candidate = v
                            break

        elif isinstance(item, (list, tuple)):
            # try to find numeric element or string filename
            for v in item:
                if isinstance(v, (int, float)):
                    match_candidate = v
                    break
                if isinstance(v, str) and v.lower().endswith(('.pdf', '.docx', '.txt')):
                    filename = v
                if isinstance(v, str):
                    import re
                    if re.search(r'-?\d+(\.\d+)?', v):
                        match_candidate = v
                        break

        elif isinstance(item, str):
            # maybe "filename|0.6" or "candidate.pdf:0.6"
            import re
            m = re.search(r'(-?\d+(\.\d+)?)', item)
            if m:
                match_candidate = m.group(1)
            # if it looks like a filename, keep
            if item.lower().endswith(('.pdf', '.docx', '.txt')):
                filename = item

        else:
            # other types
            match_candidate = item

        # compute percent
        percent = match_to_percent(match_candidate)
        normalized.append({
            "filename": filename or ("unknown_" + str(len(normalized)+1)),
            "match": percent,
            "_raw_match_candidate": match_candidate
        })

    return normalized


def categorize_resumes(resumes_raw, threshold_percent=70, partial_cutoff=40):
    """
    resumes_raw: list of dicts with keys at least: filename, match (raw numeric or percent)
    Returns annotated list and counts dict
    """
    annotated = []
    counts = {"total": 0, "strong": 0, "partial": 0}
    for r in resumes_raw:
        mp = match_to_percent(r.get("match", 0))
        if mp >= threshold_percent:
            cat = "strong"
            counts["strong"] += 1
        elif mp >= partial_cutoff:
            cat = "partial"
            counts["partial"] += 1
        else:
            cat = "notfit"
        counts["total"] += 1
        newr = dict(r)
        newr["match"] = mp
        newr["match_percent"] = mp
        newr["category"] = cat
        annotated.append(newr)
    return annotated, counts


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    jd_file = request.files.get('job_description')
    if jd_file:
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_file.filename)
        jd_file.save(jd_path)
    else:
        return "Missing job description file", 400

    resume_files = request.files.getlist('resumes')
    resume_paths = []
    for file in resume_files:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)
        resume_paths.append(path)

    # read threshold values
    try:
        threshold = int(request.form.get('threshold_percent', 70))
    except:
        threshold = 70
    try:
        partial_cutoff = int(request.form.get('partial_cutoff', 40))
    except:
        partial_cutoff = 40

    # Call your existing processing function
    raw_results = process_files(jd_path, resume_paths)

    # DEBUG: print the raw_results sample to console so we can see the exact shape
    try:
        print("DEBUG: raw_results sample (first 10):", file=sys.stderr)
        # try pretty print
        print(json.dumps(raw_results[:10], default=str, indent=2), file=sys.stderr)
    except Exception as e:
        print("DEBUG: raw_results (non-serializable) fallback:", str(raw_results)[:1000], file=sys.stderr)

    # Normalize into the expected shape
    normalized = normalize_raw_results(raw_results)

    # DEBUG: print normalized sample
    try:
        print("DEBUG: normalized sample (first 10):", file=sys.stderr)
        print(json.dumps(normalized[:10], default=str, indent=2), file=sys.stderr)
    except Exception:
        print("DEBUG: normalized (fallback):", normalized[:10], file=sys.stderr)

    # Cache raw_results for apply_threshold route
    app.config['LATEST_RESULTS'] = raw_results

    # categorize and render
    annotated, counts = categorize_resumes(normalized, threshold_percent=threshold, partial_cutoff=partial_cutoff)

    return render_template('result.html',
                           resumes=annotated,
                           counts=counts,
                           threshold_percent=threshold,
                           partial_cutoff=partial_cutoff)


@app.route('/apply_threshold', methods=['POST'])
def apply_threshold():
    try:
        threshold = int(request.form.get('threshold_percent', 70))
    except:
        threshold = 70
    try:
        partial_cutoff = int(request.form.get('partial_cutoff', 40))
    except:
        partial_cutoff = 40

    raw_results = app.config.get('LATEST_RESULTS', []) or []

    if not raw_results:
        return redirect(url_for('home'))

    # Normalize then annotate
    normalized = normalize_raw_results(raw_results)
    annotated, counts = categorize_resumes(normalized, threshold_percent=threshold, partial_cutoff=partial_cutoff)

    return render_template('result.html',
                           resumes=annotated,
                           counts=counts,
                           threshold_percent=threshold,
                           partial_cutoff=partial_cutoff)


if __name__ == '__main__':
    app.run(debug=True)
