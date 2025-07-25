import chromadb
from chromadb.config import Settings
import os

class DBManager:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="data/chroma_db"
        ))
        self.collection = self.client.get_or_create_collection("job_applications")

    def store_job_details(self, job_details, email_content):
        self.collection.add(
            documents=[email_content],
            metadatas=[{
                "job_title": job_details['title'],
                "company": job_details['company'],
                "location": job_details['location']
            }],
            ids=[f"{job_details['company']}_{job_details['title']}".replace(" ", "_")]
        )

    def get_similar_emails(self, query, n_results=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results 
