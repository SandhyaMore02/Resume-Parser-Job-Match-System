# TalentLens - Resume Parser & Job Match System

TalentLens is an AI-powered Resume Parser and Job Description Matcher built with Flask, spaCy, and Python. It provides a professional dashboard to analyze candidate resumes against job descriptions, identifying matched skills, missing requirements, and calculating an overall compatibility score.

![Dashboard Preview](https://via.placeholder.com/800x450.png?text=TalentLens+Dashboard+Preview)
> *Replace this with a real screenshot of your dashboard*

## 🚀 Features

*   **📄 Multi-Format Support**: Parses `.pdf` and `.docx` resumes.
*   **🧠 Smart Skill Extraction**: Uses NLP (spaCy) and a curated skills database to accurately identify technical and soft skills.
*   **📊 Experience Detection**: Automatically extracts years of experience from work history.
*   **🎯 Compatibility Scoring**: detailed breakdown of "Matched" vs "Missing" skills with a visual score.
*   **💼 Professional Dashboard**: Modern, responsive UI with real-time charts and analytics cards.
*   **📥 PDF Reporting**: One-click generation of a downloadable PDF analysis report.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SandhyaMore02/Resume-Parser-Job-Match-System.git
    cd Resume-Parser-Job-Match-System
    ```

2.  **Create a virtual environment** (Optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLP Model**:
    ```bash
    python -m spacy download en_core_web_sm
    ```

## 🏃‍♂️ Usage

1.  **Start the Server**:
    ```bash
    python app.py
    ```

2.  **Access the Dashboard**:
    Open your browser and navigate to: `http://127.0.0.1:5000`

3.  **Analyze a Candidate**:
    *   Upload a Resume (PDF or DOCX).
    *   Paste the Job Description (JD).
    *   Click **"Run Analysis"**.
    *   View the score, charts, and download the PDF report.

## 📂 Project Structure

```
├── app.py                  # Main Flask Application
├── job_matcher.py          # Logic for skills matching and scoring
├── resume_parser.py        # Logic for parsing PDF/DOCX and extracting entities
├── report_generator.py     # PDF Report generation module
├── requirements.txt        # Python dependencies
├── data/
│   └── skills_db.json      # Database of Technical and Soft skills
├── static/
│   ├── style.css           # Professional Dashboard styling
│   └── uploads/            # Temp storage for uploaded files and reports
└── templates/
    └── index.html          # Dashboard HTML template
```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
