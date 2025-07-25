import streamlit as st
from utils.job_scraper import JobScraper
from utils.email_generator import EmailGenerator
import os
from dotenv import load_dotenv
import PyPDF2
import io

# Load environment variables
load_dotenv()


# Initialize components
scraper = JobScraper()
email_generator = EmailGenerator()

# Custom CSS for modern and colorful UI with Dark Mode support
st.set_page_config(
    page_title="Email Generator",
    page_icon="✉️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Light Mode Styles */
    .main {
        background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
        color: #2c3e50;
    }
    h1 {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8em;
        font-weight: 800;
        margin-bottom: 1.2em;
        text-align: center;
        letter-spacing: -0.5px;
        margin-top: 0;
    }
    h2 {
        color: #2c3e50;
        font-size: 2em;
        font-weight: 700;
        margin-top: 1.8em;
        border-left: 5px solid #4ECDC4;
        padding-left: 15px;
        transition: all 0.3s ease;
    }
    h2:hover {
        transform: translateX(5px);
    }
    .stMarkdown,
    .stFileUploader>div,
    .stAlert,
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.95);
        color: #2c3e50;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        padding: 12px;
        border: 2px solid #e0e0e0;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #4ECDC4;
        box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
        transform: translateY(-2px);
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border-radius: 25px;
        padding: 12px 30px;
        border: none;
        font-weight: 600;
        font-size: 1.1em;
        transition: all 0.3s ease;
        box-shadow: 0 8px 16px rgba(255, 107, 107, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #FF8E53, #FF6B6B);
        transform: translateY(-3px);
        box-shadow: 0 12px 20px rgba(255, 107, 107, 0.3);
    }
    .stSpinner>div {
        border-color: #4ECDC4;
    }
    .stAlert[data-baseweb="notification"].stError {
        border-left: 5px solid #FF6B6B;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe3e3 100%);
    }
    .stAlert[data-baseweb="notification"].stInfo {
        border-left: 5px solid #4ECDC4;
        background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
    }
    .stAlert[data-baseweb="notification"].stSuccess {
        border-left: 5px solid #2ecc71;
        background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
    }
    .tip-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        color: #2c3e50;
        border: 1px solid rgba(78, 205, 196, 0.2);
    }
    
    /* Dark Mode Styles */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1a1f2c 0%, #2d3748 100%);
            color: #e2e8f0;
        }
        h1 {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h2 {
            color: #e2e8f0;
            border-left-color: #4ECDC4;
        }
        .stMarkdown,
        .stFileUploader>div,
        .stAlert,
        .stTextInput>div>div>input,
        .stSelectbox>div>div>select,
        .stTextArea>div>div>textarea {
            background-color: rgba(45, 55, 72, 0.95);
            color: #e2e8f0;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        .stTextInput>div>div>input,
        .stSelectbox>div>div>select,
        .stTextArea>div>div>textarea {
            border: 2px solid #4a5568;
            background-color: rgba(45, 55, 72, 0.95);
        }
        .stTextInput>div>div>input:focus,
        .stSelectbox>div>div>select:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #4ECDC4;
            box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
        }
        .stButton>button {
            background: linear-gradient(45deg, #FF6B6B, #FF8E53);
            box-shadow: 0 8px 16px rgba(255, 107, 107, 0.3);
        }
        .stButton>button:hover {
            background: linear-gradient(45deg, #FF8E53, #FF6B6B);
            box-shadow: 0 12px 20px rgba(255, 107, 107, 0.4);
        }
        .stSpinner>div {
            border-color: #4ECDC4;
        }
        .stAlert[data-baseweb="notification"].stError {
            border-left-color: #FF6B6B;
            background: linear-gradient(135deg, #2d1a1a 0%, #3d2a2a 100%);
        }
        .stAlert[data-baseweb="notification"].stInfo {
            border-left-color: #4ECDC4;
            background: linear-gradient(135deg, #1a2d2a 0%, #2a3d3a 100%);
        }
        .stAlert[data-baseweb="notification"].stSuccess {
            border-left-color: #2ecc71;
            background: linear-gradient(135deg, #1a2d2a 0%, #2a3d3a 100%);
        }
        .tip-box {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            color: #e2e8f0;
            border: 1px solid rgba(78, 205, 196, 0.2);
        }
        .tip-box p {
            color: #e2e8f0 !important;
        }
    }
    
    /* General Styles */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stMarkdown, .stFileUploader, .stAlert, .stTextInput, .stSelectbox, .stTextArea {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)


def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def main():
    st.title("Smart Email Generator For Job Seekers")
    # Features Overview Section
    with st.expander("✨ Features Overview", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                ### 🎯 Smart Matching
                - AI-powered job matching
                - Resume analysis
                - Best-fit job selection
            """)
        with col2:
            st.markdown("""
                ### ✉️ Email Generation
                - Customizable tone
                - Professional templates
                - Personalized content
            """)
        with col3:
            st.markdown("""
                ### 🚀 Optimization
                - ATS-friendly format
                - Keyword optimization
                - Best practices included
            """)
    # Main Content
    
    # Step 1: Get listing page URL
    listing_url = st.text_input("Enter the job listing page URL (not individual job):")

    # Step 2: Upload resume
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=['pdf'])

    # Step 3: Tone selection
    tone = st.selectbox(
        "Select email tone",
        ["Professional", "Confident", "Creative"],
        help="Professional: Formal and traditional\nConfident: Bold and assertive\nCreative: Innovative and engaging"
    )

    # Tips Section
    with st.expander("💡 Pro Tips for Emailing", expanded=False):
        st.markdown("""
            ### Best Practices
            1. **Research the Company**
               - Visit their website
               - Check their social media
               - Understand their culture

            2. **Personalize Your Message**
               - Mention specific company projects
               - Reference recent news
               - Connect with company values

            3. **Keep it Concise**
               - Focus on key points
               - Use bullet points
               - Maintain clear structure
        """)

    # Common Mistakes Section
    with st.expander("⚠️ Common Mistakes to Avoid", expanded=False):
        st.markdown("""
            ### What Not to Do
            1. **Generic Templates**
               - Avoid one-size-fits-all approaches
               - Don't use obvious template language
               - Never forget to customize

            2. **Poor Timing**
               - Don't send during holidays
               - Avoid weekend emails
               - Consider time zones

            3. **Follow-up Faux Pas**
               - Don't be too aggressive
               - Avoid multiple emails in one day
               - Don't forget to thank them
        """)

    # Success Metrics Section
    with st.expander("📊 Success Metrics", expanded=False):
        st.markdown("""
            ### Track Your Progress
            1. **Response Rate**
               - Aim for 15-20% response rate
               - Track open rates
               - Monitor reply times

            2. **Quality of Responses**
               - Positive feedback
               - Interview requests
               - Connection building

            3. **Conversion Rate**
               - Job offers
               - Interview success
               - Network growth
        """)

    if listing_url and uploaded_file:
        if st.button("Generate Email for Best Matching Job"):
            try:
                with st.spinner("Scanning listings and generating email..."):
                    # Extract resume text
                    resume_text = extract_text_from_pdf(uploaded_file)

                    # Extract job links from the page
                    job_links = scraper.extract_job_links(listing_url)

                    if not job_links:
                        st.error("No job links found on the page. Please try a different listing URL.")
                        return

                    # Find best match
                    best_job = scraper.find_best_matching_job(job_links, resume_text)

                    if not best_job:
                        st.error("Could not find a matching job based on your resume.")
                        return

                    
                    email_content = email_generator.generate_email(
                        job_details=best_job,
                        resume_text=resume_text,
                        tone=tone.lower()
                    )

                    # Display result
                    st.subheader("Generated Email")
                    st.text_area("Email Content", email_content, height=300)
                    st.markdown(f"**Best Matching Job:** [{best_job['title']}]({best_job['url']}) at {best_job['company']}")

                    # Success Tips
                    st.markdown("""
                        ### 🎯 Next Steps
                        1. **Review and Customize**
                           - Personalize the generated email
                           - Add specific company details
                           - Adjust tone if needed

                        2. **Before Sending**
                           - Proofread carefully
                           - Check all links
                           - Verify contact information

                        3. **After Sending**
                           - Set a follow-up reminder
                           - Track the response
                           - Update your records
                    """)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please enter a job listing URL and upload your resume.")

if __name__ == "__main__":
    main()
