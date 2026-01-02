from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from job_matcher import get_match_score, find_matching_skills
from report_generator import generate_report
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from job_matcher import get_match_score, find_matching_skills
from report_generator import generate_report
import db_handler
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Change this in production
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max size

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.form.get('job_description')
        files = request.files.getlist('resume')
        
        if not job_description:
            flash('Job description is required.')
            return redirect(request.url)

        if not files or all(f.filename == '' for f in files):
            flash('No files selected.')
            return redirect(request.url)

        results = []
        
        # Process each file
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Parse
                resume_data = parse_resume(filepath)
                
                if resume_data:
                    # Match
                    match_score = get_match_score(resume_data['text'], job_description)
                    matching_skills, missing_skills = find_matching_skills(resume_data['text'], job_description)

                    # Generate Report
                    report_filename = f"report_{os.path.splitext(filename)[0]}.pdf"
                    report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
                    generate_report(resume_data, match_score, matching_skills, missing_skills, report_path)
                    
                    # Save to DB
                    candidate_entry = {
                        "name": resume_data.get('name'),
                        "email": resume_data.get('email'),
                        "phone": resume_data.get('phone'),
                        "experience": resume_data.get('experience'),
                        "match_score": match_score,
                        "skills": matching_skills,
                        "education": resume_data.get('education'),
                        "links": resume_data.get('links'),
                        "report_file": report_filename,
                        "job_role": "Batch Analysis"
                    }
                    db_handler.add_candidate(candidate_entry)
                    
                    # Add to current batch results
                    candidate_entry['filename'] = filename
                    candidate_entry['missing_skills'] = missing_skills # Store for single view if needed
                    results.append(candidate_entry)
                else:
                    flash(f'Error parsing resume: {file.filename}')
            else:
                if file.filename != '': # Only flash if a file was actually attempted
                    flash(f'Invalid file type for {file.filename}. Allowed types are PDF, DOCX.')

        if not results:
            flash('No valid resumes were processed.')
            return redirect(request.url)

        # Sort results by match score (Descending)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # CSV Export Logic
        csv_filename = None
        if len(results) > 0:
            # Use a more robust naming for CSV, e.g., based on timestamp or job description hash
            csv_filename = f"ranking_{len(results)}_candidates_{os.urandom(4).hex()}.csv" 
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Rank', 'Name', 'Email', 'Match Score', 'Experience', 'Top Skills', 'Report File']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for idx, res in enumerate(results):
                    writer.writerow({
                        'Rank': idx + 1,
                        'Name': res.get('name', 'N/A'),
                        'Email': res.get('email', 'N/A'),
                        'Match Score': f"{res.get('match_score', 0)}%",
                        'Experience': res.get('experience', 'N/A'),
                        'Top Skills': ", ".join(res.get('skills', [])[:5]),
                        'Report File': res.get('report_file', 'N/A')
                    })

        # Logic for Single vs Bulk
        if len(results) == 1:
            # Revert to single view logic for backward compatibility/UX
            res = results[0]
            return render_template('index.html', 
                                   match_score=res['match_score'], 
                                   resume_data=res,
                                   matching_skills=res['skills'],
                                   missing_skills=res['missing_skills'],
                                   job_description=job_description,
                                   report_filename=res['report_file'])
        else:
            # For bulk, use the ranking list view
            return render_template('index.html', 
                                   job_description=job_description,
                                   ranking_list=results,
                                   csv_file=csv_filename)

    return render_template('index.html')

@app.route('/candidates')
def candidates():
    all_candidates = db_handler.get_candidates()
    return render_template('candidates.html', candidates=all_candidates)

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title and description:
            db_handler.add_job(title, description)
            flash('Job saved successfully!')
        return redirect(url_for('jobs'))
        
    all_jobs = db_handler.get_jobs()
    return render_template('jobs.html', jobs=all_jobs)

@app.route('/reports')
def reports():
    # List files in uploads directory
    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if f.endswith('.pdf') and f.startswith('report_'):
                files.append(f)
    return render_template('reports.html', files=files)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'clear_data':
            db_handler.clear_db()
            flash('All data has been cleared.')
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
