from flask import Flask, render_template, request
import os
from model.job_match import process_files

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Save job description
    jd_file = request.files['job_description']
    jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_file.filename)
    jd_file.save(jd_path)

    # Save resumes
    resume_files = request.files.getlist('resumes')
    resume_paths = []
    for file in resume_files:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)
        resume_paths.append(path)

    # Process and classify
    results = process_files(jd_path, resume_paths)

    return render_template('result.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
