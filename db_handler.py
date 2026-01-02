import json
import os
from datetime import datetime

DB_FILE = os.path.join("data", "database.json")

def init_db():
    """Initialize the database file if it doesn't exist."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"candidates": [], "jobs": []}, f)

def load_db():
    """Load the database content."""
    init_db()
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"candidates": [], "jobs": []}

def save_db(data):
    """Save data to the database."""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_candidate(candidate_data):
    """Add a new candidate entry."""
    db = load_db()
    # Create a unique ID (simple timestamp based)
    candidate_id = int(datetime.now().timestamp())
    candidate_data['id'] = candidate_id
    candidate_data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepend to list to show newest first
    db['candidates'].insert(0, candidate_data)
    save_db(db)
    return candidate_id

def get_candidates():
    """Get all candidates."""
    db = load_db()
    return db.get('candidates', [])

def get_candidate_by_id(c_id):
    """Get specific candidate by ID."""
    candidates = get_candidates()
    for c in candidates:
        if c.get('id') == c_id:
            return c
    return None

def add_job(title, description):
    """Save a job description."""
    db = load_db()
    job_id = int(datetime.now().timestamp())
    new_job = {
        "id": job_id,
        "title": title,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    db['jobs'].insert(0, new_job)
    save_db(db)
    return job_id

def get_jobs():
    """Get all saved jobs."""
    db = load_db()
    return db.get('jobs', [])

def clear_db():
    """Clear all data."""
    save_db({"candidates": [], "jobs": []})
