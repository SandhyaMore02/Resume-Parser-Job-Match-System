from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Resume Analysis Report', 0, 1, 'C')
        self.ln(5)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

def generate_report(resume_data, match_score, matching_skills, missing_skills, filepath):
    pdf = PDFReport()
    pdf.add_page()
    
    # Candidate Info
    pdf.chapter_title("Candidate Profile")
    info = f"Name: {resume_data.get('name', 'Unknown')}\n"
    info += f"Email: {resume_data.get('email', 'N/A')}\n"
    info += f"Phone: {resume_data.get('phone', 'N/A')}\n"
    info += f"Experience: {resume_data.get('experience', 0)} years detected"
    pdf.chapter_body(info)
    
    # Links
    links = resume_data.get('links', {})
    if links:
        link_text = ""
        if links.get('linkedin'): link_text += f"LinkedIn: {links['linkedin']}\n"
        if links.get('github'): link_text += f"GitHub: {links['github']}\n"
        for p in links.get('portfolio', []): link_text += f"Portfolio: {p}\n"
        
        if link_text:
            pdf.chapter_title("Online Presence")
            pdf.chapter_body(link_text)
            
    # Education
    education = resume_data.get('education', [])
    if education:
        pdf.chapter_title("Education")
        edu_text = ""
        for edu in education:
            edu_text += f"- {edu}\n"
        pdf.chapter_body(edu_text)
    
    # Match Score
    pdf.chapter_title("Match Score")
    pdf.set_font('Arial', 'B', 24)
    if match_score >= 70:
        pdf.set_text_color(0, 128, 0) # Green
    elif match_score >= 40:
        pdf.set_text_color(255, 165, 0) # Orange
    else:
        pdf.set_text_color(255, 0, 0) # Red
        
    pdf.cell(0, 15, f"{match_score}%", 0, 1, 'C')
    pdf.set_text_color(0, 0, 0) # Reset
    pdf.ln(5)
    
    # Skills
    pdf.chapter_title("Matched Skills")
    if matching_skills:
        pdf.chapter_body(", ".join(matching_skills))
    else:
        pdf.chapter_body("No specific skills matched.")
        
    pdf.chapter_title("Missing Skills")
    if missing_skills:
        pdf.set_text_color(200, 0, 0)
        pdf.chapter_body(", ".join(missing_skills))
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.chapter_body("No critical skills missing.")
        
    # Save
    pdf.output(filepath)
    return filepath
