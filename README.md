# JobFolio ✨

JobFolio is a smart, CV-driven job recommendation and email generation platform built with Streamlit. Simply upload your resume and paste a job link (e.g., a Nike job listing), and JobFolio will intelligently analyze your CV and the job posting to help you find the best-suited role.

## 🚀 Features

- 🧠 Smart Job Matching: Automatically scrapes job details from a given job link and compares it with your uploaded CV.
- 📄 CV Analysis: Parses your resume (PDF format) and extracts relevant keywords and experience.
- ✉️ Email Generator: Generates a professional email tailored to the job you’re applying for, based on your CV and the job description.
- 🎨 Modern UI: A beautifully designed web interface powered by Streamlit.
- 🔐 Environment Variables: Uses `.env` for secure configuration management.

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/oykusedef/jobfolio.git
   cd jobfolio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Note: `chromedriver.exe` is included for automated web scraping. Make sure your Chrome browser version matches or update it accordingly.

## 🗂️ Project Structure

JobFolio/
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── chromedriver.exe           # Chrome driver for web scraping
├── .env                       # Environment variables (not included)
└── utils/
    ├── job_scraper.py         # Handles job listing scraping
    ├── db_manager.py          # (Optional) Database interactions
    └── email_generator.py     # Generates personalized emails

## 🛠️ Technologies Used

- Python 🐍
- Streamlit
- PyPDF2
- Selenium
- dotenv

## 📎 Example Use Case

1. Upload your CV (PDF).
2. Paste a job listing URL (e.g., from Nike Careers).
3. Get a tailored job match score and a customized email to apply with confidence.

## 🤖 Future Improvements

- Add support for more file formats (e.g., DOCX).
- Implement LinkedIn scraping integration.
- Email directly via SMTP integration.
- AI-based summary of your strongest skills.

## 🛡️ License

This project is licensed under the MIT License.
