from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import re
import spacy
import subprocess

class EmailGenerator:
    """
    A class to generate personalized cold emails for job applications.
    Uses the Groq LLM to create human-like, contextually relevant emails
    based on job details and resume content.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-70b-8192"
        )
        
        # Load spaCy model with better error handling
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy English model...")
            try:
                # Try using pip to install the model
                subprocess.run(["pip", "install", "en-core-web-sm"], check=True)
                self.nlp = spacy.load("en_core_web_sm")
            except:
                try:
                    # If pip install fails, try using spacy download command
                    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                    self.nlp = spacy.load("en_core_web_sm")
                except:
                    print("Warning: Could not load spaCy model. Name extraction will use fallback methods.")
                    self.nlp = None
        
        # Updated template to use resume content and tone
        self.email_template = PromptTemplate(
            input_variables=["job_title", "company", "skills", "experience", "resume", "tone"],
            template="""
            Write a personalized cold email for a job application with the following details:
            Job Title: {job_title}
            Company: {company}
            Required Skills: {skills}
            Required Experience: {experience}

            # Candidate's Resume Summary:
            {resume}

            # Tone Guidelines:
            Tone: {tone}
            Professional Tone: Formal, traditional, and business-appropriate language
            Confident Tone: Bold, assertive language that emphasizes achievements
            Creative Tone: Innovative, engaging, and unique approach while maintaining professionalism

            # Guidelines for email structure:
            1. Analyze the resume and extract relevant experiences and skills that match the job requirements
            2. Highlight the most impressive and relevant achievements from the resume
            3. Focus on quantifiable results and specific technical skills that match the job
            4. Show enthusiasm for the role and company's mission
            5. Include a clear call to action for next steps
            6. Maintain the selected tone throughout the email
            7. Keep the email concise (200-300 words)

            # Required Email Structure:
            1. Start with an attention-grabbing subject line that includes the job title
            2. Opening paragraph: Hook and position mention
            3. Body: 2-3 paragraphs highlighting relevant experience and achievements
            4. Closing: Call to action and professional sign-off

            Write the complete email now, including the subject line:
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.email_template)

    def extract_name_from_resume(self, resume_text):
        """
        Extract the candidate's name from resume text using multiple methods
        """
        # Clean the text
        clean_text = resume_text.strip().replace('\n', ' ')
        first_line = clean_text.split('.')[0].strip()

        # Method 1: Using spaCy for Named Entity Recognition (if available)
        if self.nlp is not None:
            try:
                doc = self.nlp(first_line)
                person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
                if person_names:
                    return person_names[0]
            except Exception as e:
                print(f"spaCy name extraction failed: {e}")
        
        # Method 2: Common resume header patterns
        name_patterns = [
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",  # Standard name format
            r"Name:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",  # "Name: John Doe"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*(?:Resume|CV)",  # "John Doe Resume"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, clean_text)
            if match:
                return match.group(1)
        
        # Method 3: First line heuristic (if it looks like a name)
        words = first_line.split()
        if 2 <= len(words) <= 3:
            if all(word.strip() and word[0].isupper() for word in words):
                return first_line
        
        return "Job Applicant"  # Default fallback

    def extract_contact_details(self, resume_text):
        """
        Extract contact details including name, phone, email, and LinkedIn from resume
        """
        # Clean the text and split into lines for better processing
        lines = resume_text.strip().split('\n')
        clean_text = ' '.join(lines)  # Keep a full text version for backup search
        
        # Initialize contact details dictionary
        contact_details = {
            'name': None,
            'phone': None,
            'email': None,
            'linkedin': None,
            'location': None,
            'portfolio': None
        }
        
        # Patterns for contact information
        patterns = {
            'phone': [
                r'(?:Phone|Tel|Mobile|Cell):?\s*(\+?\d[\d\s.-]{8,})',
                r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
                r'\b\d{10}\b',
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            ],
            'email': [
                r'(?:Email|E-mail):?\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'linkedin': [
                r'(?:LinkedIn|Profile):?\s*((?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/[\w-]+)',
                r'\blinkedin\.com\/(?:in|profile)\/[\w-]+\b'
            ],
            'location': [
                r'(?:Location|Address):?\s*([\w\s,.-]+(?:\d{5})?)',
                r'\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s*\d{5}\b'
            ],
            'portfolio': [
                r'(?:Portfolio|Website|Blog):?\s*((?:https?:\/\/)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                r'\b(?:https?:\/\/)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ]
        }
        
        # Extract name first (using existing method)
        contact_details['name'] = self.extract_name_from_resume(clean_text)
        
        # Look for contact details in the first few lines (usually header section)
        header_text = ' '.join(lines[:10])  # Check first 10 lines for header info
        
        # Extract each type of contact detail
        for detail_type, detail_patterns in patterns.items():
            # Try header section first
            for pattern in detail_patterns:
                match = re.search(pattern, header_text, re.IGNORECASE)
                if match:
                    value = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    contact_details[detail_type] = value.strip()
                    break
            
            # If not found in header, try full text
            if not contact_details[detail_type]:
                for pattern in detail_patterns:
                    match = re.search(pattern, clean_text, re.IGNORECASE)
                    if match:
                        value = match.group(1) if len(match.groups()) > 0 else match.group(0)
                        contact_details[detail_type] = value.strip()
                        break
        
        # Clean up LinkedIn URL
        if contact_details['linkedin']:
            if not contact_details['linkedin'].startswith(('http://', 'https://', 'www.')):
                contact_details['linkedin'] = 'www.' + contact_details['linkedin']
        
        return contact_details

    def generate_email(self, job_details, resume_text, tone):
        """
        Generates a personalized cold email based on the job details and resume.
        """
        skills = ", ".join(job_details['primary_skills'])
        
        # Extract all contact details
        contact_details = self.extract_contact_details(resume_text)
        
        email = self.chain.run({
            "job_title": job_details['title'],
            "company": job_details['company'],
            "skills": skills,
            "experience": job_details['experience'],
            "resume": resume_text,
            "tone": tone
        })
        
        # Find the position of "sincerely" and replace everything after it
        sincerely_index = email.lower().rfind("sincerely")
        if sincerely_index != -1:
            email = email[:sincerely_index].strip()

        # Create a professional signature with all available contact details
        signature = "\n\nBest Regards,\n"
        
        # Add name
        if contact_details['name']:
            signature += f"{contact_details['name']}\n"
        
        # Add contact information in a structured way
        contact_lines = []
        
        if contact_details['email']:
            contact_lines.append(f"Email: {contact_details['email']}")
        if contact_details['phone']:
            contact_lines.append(f"Phone: {contact_details['phone']}")
        if contact_details['linkedin']:
            contact_lines.append(f"LinkedIn: {contact_details['linkedin']}")
        if contact_details['location']:
            contact_lines.append(f"Location: {contact_details['location']}")
        if contact_details['portfolio']:
            contact_lines.append(f"Portfolio: {contact_details['portfolio']}")
        
        signature += '\n'.join(contact_lines)
        
        email += signature
        return email 
