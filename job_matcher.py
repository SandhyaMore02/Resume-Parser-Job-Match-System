from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import json
import os

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Model 'en_core_web_sm' not found. Please download it using: python -m spacy download en_core_web_sm")
    nlp = None

# Load Skills Database
SKILLS_DB = {"technical_skills": [], "soft_skills": []}
try:
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_path, 'data', 'skills_db.json')
    with open(db_path, 'r') as f:
        SKILLS_DB = json.load(f)
except Exception as e:
    print(f"Warning: Could not load skills_db.json: {e}")

def get_match_score(resume_text, job_description):
    text = [resume_text, job_description]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(text)
    match_percentage = cosine_similarity(count_matrix)[0][1] * 100
    return round(match_percentage, 2)

def extract_keywords(text):
    if not nlp:
        return []
    
    doc = nlp(text.lower())
    keywords = []
    # Extract noun chunks and proper nouns as potential keywords
    for token in doc:
        if token.pos_ in ["pROPN", "NOUN"] and not token.is_stop and not token.is_punct:
            keywords.append(token.text)
            
    return list(set(keywords))

def normalize_skill(skill):
    return skill.lower().strip()

def find_matching_skills(resume_text, job_description):
    """
    Extracts skills from JD and Resume using the predefined Skills DB
    and finds matches/missing skills.
    """
    if not nlp:
        return [], []

    resume_text_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # Flatten skills list for easy checking
    all_known_skills = set(SKILLS_DB["technical_skills"] + SKILLS_DB["soft_skills"])
    
    # Find required skills in JD
    required_skills = set()
    for skill in all_known_skills:
        # Simple substring match (can be improved with regex word boundaries)
        if skill in jd_lower:
            required_skills.add(skill)
            
    # Find skills present in Resume
    resume_skills = set()
    for skill in all_known_skills:
        if skill in resume_text_lower:
            resume_skills.add(skill)
    
    # Calculate match
    matched_skills = list(required_skills.intersection(resume_skills))
    missing_skills = list(required_skills.difference(resume_skills))
    
    return matched_skills, missing_skills

