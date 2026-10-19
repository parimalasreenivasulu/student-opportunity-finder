# Student Opportunity Finder

Beginner-friendly web app concept for discovering internships, scholarships, free courses, certifications, and fresher jobs.

## Demo data notice
The initial records are clearly labelled sample records. They are not verified vacancies or scholarship offers. Check official provider websites before relying on any listing.

## Technology
- Python
- Streamlit
- SQLite / SQL
- Git and GitHub (optional)

## Run on Windows
1. Install Python 3.10 or later.
2. Open PowerShell in this folder.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Start the app:
   ```powershell
   python -m streamlit run app.py
   ```
6. Open the local URL Streamlit prints, usually http://localhost:8501.

## Current features
- Browse sample opportunities
- Search by keyword
- Filter by category and location
- View eligibility, deadlines, source links, and listing status
- Store records in SQLite

## Planned features
- Admin form to add/edit listings
- Saved opportunities
- Secure user accounts
- Deadline notifications
- Reporting and link verification
- Optional AWS hosting and CloudWatch troubleshooting practice
