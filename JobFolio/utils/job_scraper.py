import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import selenium
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from urllib.parse import urljoin


class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_job_links(self, listing_url: str) -> List[str]:


        job_links = []

        try:
            # Statik HTML (Nike gibi siteler)
            response = requests.get(listing_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/job/' in href:
                    full_url = requests.compat.urljoin(listing_url, href)
                    if full_url not in job_links:
                        job_links.append(full_url)

            # Eğer job link bulunamazsa → Selenium fallback
            if not job_links:
                print("Falling back to Selenium for dynamic content...")

                # 🧠 Proje dizinindeki chromedriver.exe yolunu al
                chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")

                options = Options()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')

                driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options)

                driver.get(listing_url)
                time.sleep(5)  # Sayfanın yüklenmesini bekle

                # Sayfayı aşağı kaydır (Baykar gibi dinamik yüklenen siteler için)
                last_height = driver.execute_script("return document.body.scrollHeight")
                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Tüm linkleri al
                elements = driver.find_elements(By.TAG_NAME, 'a')
                for a in elements:
                    href = a.get_attribute('href')
                    if href and any(keyword in href.lower() for keyword in ['job', 'jobs', 'career', 'details', 'recruit', 'ilan', 'position', 'jobdetail', 'jobads']):
                                full_url = urljoin(listing_url, href)
                                if full_url not in job_links:
                                    job_links.append(full_url)

                driver.quit()

        except Exception as e:
            print(f"Error extracting job links: {e}")

        return job_links


    def extract_job_details(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            job_details = {
                'title': self._extract_text(soup, 'h1'),
                'company': self._extract_company(soup),
                'location': self._extract_location(soup),
                'primary_skills': self._extract_skills(soup, primary=True),
                'secondary_skills': self._extract_skills(soup, primary=False),
                'experience': self._extract_experience(soup),
                'education': self._extract_education(soup)
            }

            return job_details

        except Exception as e:
            print(f"Error scraping job details: {str(e)}")
            return None

    def match_job_to_resume(self, job_details: Dict, resume_text: str) -> int:
        resume_lower = resume_text.lower()
        matched = 0
        for skill in job_details.get("primary_skills", []):
            skill_words = skill.lower().split()  # tek kelimeden eşleşme
            for word in skill_words:
                if word in resume_lower:
                    matched += 1
                    break
        return matched

    def find_best_matching_job(self, job_links: List[str], resume_text: str, target_keywords: List[str] = None) -> Optional[Dict]:
        best_job = None
        best_score = 0
        for link in job_links:
            job = self.extract_job_details(link)
            if not job:
                continue
            title = job.get('title', '').lower()
            if target_keywords and not any(keyword in title for keyword in target_keywords):
                continue
            score = self.match_job_to_resume(job, resume_text)  # 👈 self. kullanılmalı
            print(f"📝 Checking: {job.get('title')} | Score: {score} | URL: {link}")
            if score > best_score:
                best_score = score
                best_job = job
                best_job['url'] = link
        return best_job

    def _extract_text(self, soup, selector):
        element = soup.find(selector)
        return element.text.strip() if element else ""

    def _extract_company(self, soup):
        company_element = soup.find('meta', {'property': 'og:site_name'})
        return company_element['content'] if company_element else ""

    def _extract_location(self, soup):
        location_element = soup.find(class_=['location', 'job-location'])
        return location_element.text.strip() if location_element else ""

    def _extract_skills(self, soup, primary=True):
        skills = []

        # Öncelikle bilinen class'lara bak
        possible_sections = soup.find_all(class_=['requirements', 'qualifications', 'job-skills', 'skills-list', 'job-qualifications'])

        for section in possible_sections:
            items = section.find_all('li')
            skills.extend([item.text.strip() for item in items if item.text.strip()])

        # Eğer hiçbir şey bulamadıysak, fallback: sayfadaki tüm <li>'leri oku
        if not skills:
            fallback_items = soup.find_all('li')
            skills = [item.text.strip() for item in fallback_items if item.text.strip()]

        return skills



    def _extract_experience(self, soup):
        experience_section = soup.find(text=lambda t: t and 'experience' in t.lower())
        return experience_section.strip() if experience_section else ""

    def _extract_education(self, soup):
        education_section = soup.find(text=lambda t: t and 'education' in t.lower())
        return education_section.strip() if education_section else ""
