# https://youtu.be/z7Xjq4hCV_I - Project Demo Video
# 📌 Resume–Job Matching System  
### Automating Resume Screening using NLP and Cosine Similarity

The **Resume–Job Matching System** is a smart web-based application designed to automate the process of resume screening by comparing multiple resumes with a job description. It uses **Natural Language Processing (NLP)** techniques to compute text similarity and classify candidates based on their job relevance.

This project helps recruiters instantly identify **Strong**, **Partial**, and **Not Fit** candidates — improving hiring accuracy and reducing manual screening effort.

---

## 🚀 Features

✔ Upload **multiple resumes** and one job description  
✔ Supports **PDF**, **DOCX**, and **TXT** formats  
✔ Fully custom text similarity implementation (no ML libraries)  
✔ Dynamic **threshold control** for match classification  
✔ Lightweight & scalable **Flask backend**  
✔ Simple and clean **UI for fast screening**  

---

## 🧠 Tech Stack

| Component | Technology Used |
|----------|----------------|
| Programming Language | Python |
| Web Framework | Flask |
| NLP/Text Processing | Regex, Bag-of-Words |
| File Parsing | PyPDF2, python-docx |
| Data Handling | NumPy, pandas |
| UI | HTML, CSS, JavaScript |

---

## 📊 System Workflow

1️⃣ Upload JD + multiple resumes  
2️⃣ Extract text from documents  
3️⃣ Clean and preprocess text  
4️⃣ Convert into Bag-of-Words vectors  
5️⃣ Compute cosine similarity scores  
6️⃣ Categorize into match levels  
7️⃣ Display structured results on browser  

---

## 🖼️ UI Screenshots
<img width="740" height="846" alt="image" src="https://github.com/user-attachments/assets/b25f61b3-04a4-4e4b-bd7d-2812a775de00" />
<img width="1132" height="787" alt="image" src="https://github.com/user-attachments/assets/1369274a-058f-4d23-9eac-2aa9c331f60a" />


---

## ▶️ Installation & Run Instructions

### 📌 Clone this repository
git clone https://github.com/rishabhranjanishwar/resume-job-match-app.git
cd resume-job-match-app

📌 Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

📌 Install dependencies
pip install -r requirements.txt

📌 Run the application
python app.py

📌 Open in browser
http://127.0.0.1:5000/

---

🧪 Output Overview

After processing, the app:

✔ Displays similarity scores in percentage
✔ Groups resumes into:

🟢 Strong Match

🟡 Partial Match

🔴 Not Fit

✔ Allows threshold adjustment without re-uploading

---

📈 Performance Advantages

Metric	Manual Screening	Automated System

Time for 10 resumes	20–30 min	< 5 sec

Fairness	Low	High

Scalability	Poor	Excellent

Accuracy	Subjective	Objective

Fatigue / Bias	High	None

Automating resume screening enhances hiring speed and quality.

---

🔮 Future Enhancements

TF-IDF / semantic embeddings (Word2Vec, BERT, SBERT)

Resume structure-based scoring (skills, education, experience)

Cloud deployment (AWS / Heroku)

Multi-user login + role-based dashboard

ATS integration via REST API

Graphical analytics on results

Parsing enhancement for images & tables in PDFs

---

🤝 Contributions

Contributions are welcome! 🎯

Follow these steps:

Fork → Create Branch → Commit Changes → Pull Request

---

👨‍💻 Author

Rishabh Ranjan

🔗 GitHub: https://github.com/rishabhranjanishwar
