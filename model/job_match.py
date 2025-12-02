import os
import re
import numpy as np
import pandas as pd
from PyPDF2 import PdfReader
import docx
from numpy.linalg import norm

def read_text_from_file(filepath):
    if filepath.endswith('.pdf'):
        reader = PdfReader(filepath)
        text = ''.join([page.extract_text() for page in reader.pages])
    elif filepath.endswith('.docx'):
        doc = docx.Document(filepath)
        text = ' '.join([p.text for p in doc.paragraphs])
    elif filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = ''
    return clean_text(text)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return ' '.join(text.split())

def text_to_vector(text, vocab):
    vector = np.zeros(len(vocab))
    words = text.split()
    for w in words:
        if w in vocab:
            vector[vocab[w]] += 1
    return vector / norm(vector) if norm(vector) != 0 else vector

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1)*norm(vec2) + 1e-10)

def process_files(jd_path, resume_paths):
    jd_text = read_text_from_file(jd_path)
    resumes = [read_text_from_file(r) for r in resume_paths]
    names = [os.path.basename(r) for r in resume_paths]

    all_texts = [jd_text] + resumes
    unique_words = list(set(' '.join(all_texts).split()))
    vocab = {word: i for i, word in enumerate(unique_words)}

    jd_vec = text_to_vector(jd_text, vocab)
    results = []

    for name, text in zip(names, resumes):
        vec = text_to_vector(text, vocab)
        sim = cosine_similarity(jd_vec, vec)
        label = 'Fit ✅' if sim > 0.6 else 'Not Fit ❌'
        results.append({'Resume': name, 'Match Score': round(sim, 2), 'Result': label})

    df = pd.DataFrame(results)
    return df.to_dict(orient='records')
