import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time

class JobDataCollector:
    def __init__(self):
        self.base_url = "https://api.github.com/repos/awesome-jobs/vacancies/contents"
        print("Initialized GitHub Jobs collector")
        
    def test_api_connection(self):
        """Test the API connection with a simple request"""
        try:
            print(f"\nTesting API connection...")
            print(f"Request URL: {self.base_url}")
            
            response = requests.get(self.base_url)
            
            if response.status_code == 200:
                data = response.json()
                print("API connection successful!")
                print(f"Response status: {response.status_code}")
                print(f"Number of job files: {len(data)}")
            else:
                print(f"API Error: {response.status_code}")
                print(f"Error message: {response.text}")
                
        except Exception as e:
            print(f"Error testing API connection: {str(e)}")
        
    def fetch_jobs(self, job_title=None, location=None, max_results=100):
        """
        Fetch job postings from GitHub jobs repository
        If job_title or location is None, fetch all available jobs
        """
        jobs = []
        
        print(f"\nStarting job fetch with parameters:")
        print(f"Job Title: {job_title}")
        print(f"Location: {location}")
        print(f"Max Results: {max_results}")
        
        try:
            print(f"\nMaking API request to: {self.base_url}")
            
            response = requests.get(self.base_url)
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
            files = response.json()
            
            for file in files:
                if len(jobs) >= max_results:
                    break
                    
                if file['name'].endswith('.md'):
                    try:
                        # Get the content of the markdown file
                        content_url = file['download_url']
                        content_response = requests.get(content_url)
                        
                        if content_response.status_code == 200:
                            content = content_response.text
                            
                            # Extract job details from markdown
                            job = self._parse_markdown_job(content)
                            
                            # Filter by title and location if specified
                            if job_title and job_title.lower() not in job.get('title', '').lower():
                                continue
                            if location and location.lower() not in job.get('location', '').lower():
                                continue
                                
                            jobs.append(job)
                            print(f"Fetched {len(jobs)} jobs so far...")
                            
                    except Exception as e:
                        print(f"Error processing file {file['name']}: {str(e)}")
                        continue
                        
                # Respect API rate limits
                time.sleep(1)
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            
        print(f"\nTotal jobs fetched: {len(jobs)}")
        return jobs[:max_results]
    
    def _parse_markdown_job(self, content):
        """
        Parse job details from markdown content
        """
        job = {
            'title': '',
            'company': '',
            'location': '',
            'description': '',
            'type': '',
            'created_at': '',
            'url': '',
            'company_url': '',
            'company_logo': '',
            'how_to_apply': ''
        }
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                job['title'] = line[2:].strip()
            elif line.startswith('**Company:**'):
                job['company'] = line.replace('**Company:**', '').strip()
            elif line.startswith('**Location:**'):
                job['location'] = line.replace('**Location:**', '').strip()
            elif line.startswith('**Type:**'):
                job['type'] = line.replace('**Type:**', '').strip()
            elif line.startswith('**Description:**'):
                job['description'] = line.replace('**Description:**', '').strip()
            elif line.startswith('**How to apply:**'):
                job['how_to_apply'] = line.replace('**How to apply:**', '').strip()
            elif line.startswith('**URL:**'):
                job['url'] = line.replace('**URL:**', '').strip()
                
        return job
    
    def process_jobs(self, jobs):
        """
        Process raw job data into a structured DataFrame
        """
        if not jobs:
            print("No jobs to process")
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description',
                'type', 'created_at', 'url', 'company_url',
                'company_logo', 'how_to_apply'
            ])
            
        processed_jobs = []
        
        for job in jobs:
            processed_job = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'description': job.get('description', ''),
                'type': job.get('type', ''),
                'created_at': job.get('created_at', ''),
                'url': job.get('url', ''),
                'company_url': job.get('company_url', ''),
                'company_logo': job.get('company_logo', ''),
                'how_to_apply': job.get('how_to_apply', '')
            }
            processed_jobs.append(processed_job)
            
        return pd.DataFrame(processed_jobs)
    
    def save_data(self, df, filename='job_data.csv'):
        """
        Save processed data to CSV
        """
        if df.empty:
            print("No data to save")
            return
            
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
    def load_data(self, filename='job_data.csv'):
        """
        Load data from CSV
        """
        try:
            df = pd.read_csv(filename)
            if df.empty:
                print("Loaded empty DataFrame")
                return pd.DataFrame(columns=[
                    'title', 'company', 'location', 'description',
                    'type', 'created_at', 'url', 'company_url',
                    'company_logo', 'how_to_apply'
                ])
            return df
        except (pd.errors.EmptyDataError, FileNotFoundError):
            print(f"Could not load {filename}")
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description',
                'type', 'created_at', 'url', 'company_url',
                'company_logo', 'how_to_apply'
            ]) 