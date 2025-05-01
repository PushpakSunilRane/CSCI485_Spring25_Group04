import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time

class JobDataCollector:
    def __init__(self):
        load_dotenv()
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        
        if not self.app_id or not self.app_key:
            raise ValueError("Missing Adzuna API credentials. Please check your .env file.")
            
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.country = "us"  # Default to US jobs
        print("Initialized Adzuna Jobs collector")
        
    def test_api_connection(self):
        """Test the API connection with a simple request"""
        try:
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': 1,
                'what': 'software'
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/{self.country}/search/1", params=params, headers=headers)
            
            if response.status_code == 200:
                return True
            else:
                print(f"API Error: {response.status_code}")
                print(f"Error message: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error testing API connection: {str(e)}")
            return False
        
    def fetch_jobs(self, job_title=None, location=None, max_results=100):
        """
        Fetch job postings from Adzuna
        """
        jobs = []
        page = 1
        results_per_page = min(50, max_results)  # Adzuna max per page is 50
        
        try:
            while len(jobs) < max_results:
                params = {
                    'app_id': self.app_id,
                    'app_key': self.app_key,
                    'results_per_page': results_per_page,
                    'page': page
                }
                
                if job_title:
                    params['what'] = job_title.lower()  # Convert to lowercase
                if location:
                    params['where'] = location.lower()  # Convert to lowercase
                    
                headers = {
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(f"{self.base_url}/{self.country}/search/{page}", 
                                     params=params, 
                                     headers=headers)
                
                if response.status_code != 200:
                    print(f"API Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                    
                for job in results:
                    if len(jobs) >= max_results:
                        break
                        
                    processed_job = {
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'description': job.get('description', ''),
                        'type': job.get('contract_type', ''),
                        'created_at': job.get('created', ''),
                        'url': job.get('redirect_url', ''),
                        'salary_min': job.get('salary_min', ''),
                        'salary_max': job.get('salary_max', ''),
                        'category': job.get('category', {}).get('label', '')
                    }
                    
                    jobs.append(processed_job)
                    
                page += 1
                time.sleep(1)  # Respect rate limits
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            
        return jobs[:max_results]
    
    def process_jobs(self, jobs):
        """
        Process raw job data into a structured DataFrame
        """
        if not jobs:
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description',
                'type', 'created_at', 'url', 'salary_min',
                'salary_max', 'category'
            ])
            
        return pd.DataFrame(jobs)
    
    def save_data(self, df, filename='job_data.csv'):
        """
        Save processed data to CSV
        """
        if df.empty:
            return
            
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
    def load_data(self, filename='job_data.csv'):
        """
        Load data from CSV
        """
        try:
            return pd.read_csv(filename)
        except FileNotFoundError:
            return pd.DataFrame()

if __name__ == "__main__":
    # Create an instance of the collector
    collector = JobDataCollector()
    
    # Test the API connection
    print("\nTesting API connection...")
    if collector.test_api_connection():
        # Fetch some jobs
        print("\nFetching jobs...")
        jobs = collector.fetch_jobs(job_title="Software Engineer", max_results=10)
        
        # Process and display the results
        if jobs:
            df = collector.process_jobs(jobs)
            print(f"\nFound {len(df)} jobs:")
            print(df[['title', 'company', 'location']].to_string())
        else:
            print("No jobs found.")
    else:
        print("API connection failed.") 