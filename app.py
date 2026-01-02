from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from job_matcher import get_match_score, find_matching_skills
from report_generator import generate_report

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
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['resume']
        job_description = request.form.get('job_description')

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename) and job_description:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process Resume
            resume_data = parse_resume(filepath)
            
            if resume_data:
                match_score = get_match_score(resume_data['text'], job_description)
                matching_skills, missing_skills = find_matching_skills(resume_data['text'], job_description)

                # Generate PDF Report
                report_filename = f"report_{os.path.splitext(filename)[0]}.pdf"
                report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
                generate_report(resume_data, match_score, matching_skills, missing_skills, report_path)

                return render_template('index.html', 
                                       match_score=match_score, 
                                       resume_data=resume_data,
                                       matching_skills=matching_skills,
                                       missing_skills=missing_skills,
                                       job_description=job_description,
                                       report_filename=report_filename)
            else:
                flash('Error parsing resume')
                return redirect(request.url)
        else:
             flash('Invalid file type or missing job description')
             return redirect(request.url)

    return render_template('index.html')

@app.route('/candidates')
def candidates():
    return render_template('placeholder.html', title='Candidates')

@app.route('/jobs')
def jobs():
    return render_template('placeholder.html', title='Job Listings')

@app.route('/reports')
def reports():
    return render_template('placeholder.html', title='Reports')

@app.route('/settings')
def settings():
    return render_template('placeholder.html', title='Settings')

if __name__ == '__main__':
    app.run(debug=True)
