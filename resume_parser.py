import spacy
from PyPDF2 import PdfReader
import docx
import re

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not downloaded yet, we might want to handle it or expect it to be handled during setup
    # For now, we assume it will be available when running
    print("Model 'en_core_web_sm' not found. Please download it using: python -m spacy download en_core_web_sm")
    nlp = None

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_contact_info(text):
    email = None
    phone = None

    # Email Regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    if email_match:
        email = email_match.group()

    # Phone Regex (Simple pattern, can be improved)
    # Matches formats like +91-9876543210, 9876543210, 123-456-7890
    phone_pattern = r'(\+?\d{1,4}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        phone = phone_match.group()

    return email, phone

def extract_name(text):
    # This is a heuristic based approach. 
    # Usually name is at the top. We can use spacy PERSON entity, 
    # but it might pick up other names.
    if not nlp:
        return "Unknown"
        
    doc = nlp(text[:200]) # Look at first 200 chars
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Unknown"

def extract_skills(text):
    # In a real app, we would have a predefined list of skills or use a more advanced NER.
    # Here we can look for noun chunks or specific keywords if we had a database.
    # For this MVP, we will rely on the matcher to find skills from the job description in the resume.
    # This function returns a raw list of potential skills based on NOUN/PROPN, 
    # but better logic is in the matching phase.
    if not nlp:
        return []
        
    doc = nlp(text)
    # Just return text for now, real extraction happens in matching or we can improve this
    # to return a list of noun phrases that look like skills.
    skills = []
    # Basic skill extraction - valid skills often are PROPN or NOUNs
    # This is very naive.
    for token in doc:
        if token.pos_ in ["PROPN", "NOUN"] and not token.is_stop:
            skills.append(token.text)
    
    return list(set(skills)) # Unique skills

def extract_experience(text):
    """
    Heuristic to extract years of experience.
    Looks for patterns like '5+ years', '10 years of experience'.
    """
    # Regex for "X years", "X+ years", "X.Y years"
    # We look for digits followed by 'year' or 'yrs'
    pattern = r'(\d+(\.\d+)?)\+?\s*(years?|yrs?)'
    matches = re.findall(pattern, text.lower())
    
    years = []
    for match in matches:
        try:
            val = float(match[0])
            years.append(val)
        except ValueError:
            pass
            
    if years:
        return max(years) # Return the highest number found as potential total experience
    if years:
        return max(years) # Return the highest number found as potential total experience
    return 0

def extract_education(text):
    """
    Extracts education degrees and universities.
    """
    education = []
    
    # Common degrees
    degrees = [
        r'B\.?Tech', r'M\.?Tech', r'B\.?Sc', r'M\.?Sc', r'B\.?E', r'M\.?E', 
        r'Ph\.?D', r'Bachelor', r'Master', r'Diploma', r'MBA', r'BCA', r'MCA'
    ]
    
    for degree in degrees:
        pattern = r'(?i)\b' + degree + r'\b.*?(?=\n|$)'
        matches = re.findall(pattern, text)
        for match in matches:
            education.append(match.strip())
            
    return list(set(education))

def extract_links(text):
    """
    Extracts URLs and specifically identifies LinkedIn and GitHub.
    """
    links = {
        "linkedin": None,
        "github": None,
        "portfolio": []
    }
    
    # Regex for URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    
    for url in urls:
        if "linkedin.com" in url:
            links["linkedin"] = url
        elif "github.com" in url:
            links["github"] = url
        else:
            links["portfolio"].append(url)
            
    return links

def parse_resume(file_path):
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        return None

    email, phone = extract_contact_info(text)
    name = extract_name(text)
    experience = extract_experience(text)
    education = extract_education(text)
    links = extract_links(text)
    
    # We clean the text for further processing
    clean_text = " ".join(text.split())
    
    return {
        "text": clean_text,
        "name": name,
        "email": email,
        "phone": phone,
        "experience": experience,
        "education": education,
        "links": links
    }
