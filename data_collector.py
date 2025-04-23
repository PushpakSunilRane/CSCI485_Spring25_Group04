import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import re

class JobDataCollector:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://api.github.com/search/repositories"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f"token {os.getenv('GITHUB_TOKEN')}"
        }
        print("Initialized GitHub Jobs collector")
        
    def test_api_connection(self):
        """Test the API connection with a simple request"""
        try:
            params = {
                'q': 'hiring in:readme language:markdown',
                'sort': 'updated',
                'order': 'desc'
            }
            
            print(f"\nTesting API connection...")
            print(f"Request URL: {self.base_url}")
            print(f"Request Parameters: {params}")
            
            response = requests.get(self.base_url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print("API connection successful!")
                print(f"Response status: {response.status_code}")
                print(f"Number of repositories found: {data.get('total_count', 0)}")
            else:
                print(f"API Error: {response.status_code}")
                print(f"Error message: {response.text}")
                
        except Exception as e:
            print(f"Error testing API connection: {str(e)}")
        
    def fetch_jobs(self, job_title=None, location=None, max_results=100):
        """
        Fetch job postings from GitHub repositories
        If job_title or location is None, fetch all available jobs
        """
        jobs = []
        
        print(f"\nStarting job fetch with parameters:")
        print(f"Job Title: {job_title}")
        print(f"Location: {location}")
        print(f"Max Results: {max_results}")
        
        try:
            # Build search query
            query = 'hiring OR "we are hiring" OR "job opening" OR "careers" in:readme'
            if job_title:
                query += f' {job_title}'
            if location:
                query += f' {location}'
                
            params = {
                'q': query,
                'sort': 'updated',
                'order': 'desc',
                'per_page': min(100, max_results)  # GitHub API max per page is 100
            }
            
            print(f"\nMaking API request to: {self.base_url}")
            print(f"With parameters: {params}")
            
            response = requests.get(self.base_url, params=params, headers=self.headers)
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
            data = response.json()
            repositories = data.get('items', [])
            
            for repo in repositories:
                if len(jobs) >= max_results:
                    break
                    
                try:
                    # Get the README content
                    readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
                    readme_response = requests.get(readme_url, headers=self.headers)
                    
                    if readme_response.status_code == 200:
                        readme_content = readme_response.json().get('content', '')
                        # Decode base64 content
                        import base64
                        readme_text = base64.b64decode(readme_content).decode('utf-8')
                        
                        # Extract job information
                        job = self._extract_job_info(readme_text, repo)
                        
                        # Filter by title and location if specified
                        if job_title and job_title.lower() not in job.get('title', '').lower():
                            continue
                        if location and location.lower() not in job.get('location', '').lower():
                            continue
                            
                        jobs.append(job)
                        print(f"Fetched {len(jobs)} jobs so far...")
                        
                except Exception as e:
                    print(f"Error processing repository {repo['full_name']}: {str(e)}")
                    continue
                    
                # Respect API rate limits
                time.sleep(1)
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            
        print(f"\nTotal jobs fetched: {len(jobs)}")
        return jobs[:max_results]
    
    def _extract_job_info(self, content, repo):
        """
        Extract job information from README content
        """
        job = {
            'title': '',
            'company': repo['owner']['login'],
            'location': '',
            'description': '',
            'type': '',
            'created_at': repo['created_at'],
            'url': repo['html_url'],
            'company_url': repo['owner']['html_url'],
            'company_logo': repo['owner']['avatar_url'],
            'how_to_apply': ''
        }
        
        # Try to extract title from first line or repository name
        first_line = content.split('\n')[0].strip()
        if first_line.startswith('# '):
            job['title'] = first_line[2:].strip()
        else:
            job['title'] = repo['name'].replace('-', ' ').title()
            
        # Try to extract location using common patterns
        location_patterns = [
            r'location:?\s*([^\n]+)',
            r'based in:?\s*([^\n]+)',
            r'remote:?\s*([^\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job['location'] = match.group(1).strip()
                break
                
        if not job['location']:
            job['location'] = 'Remote'
            
        # Extract description
        description_pattern = r'description:?\s*([^\n]+)'
        match = re.search(description_pattern, content, re.IGNORECASE)
        if match:
            job['description'] = match.group(1).strip()
        else:
            job['description'] = repo['description'] or ''
            
        # Extract job type
        type_patterns = [
            r'type:?\s*([^\n]+)',
            r'employment type:?\s*([^\n]+)',
            r'job type:?\s*([^\n]+)'
        ]
        
        for pattern in type_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job['type'] = match.group(1).strip()
                break
                
        if not job['type']:
            job['type'] = 'Full-time'
            
        # Extract how to apply
        apply_patterns = [
            r'how to apply:?\s*([^\n]+)',
            r'apply:?\s*([^\n]+)',
            r'contact:?\s*([^\n]+)'
        ]
        
        for pattern in apply_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job['how_to_apply'] = match.group(1).strip()
                break
                
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

if __name__ == "__main__":
    # Create an instance of the collector
    collector = JobDataCollector()
    
    # Test the API connection
    print("\nTesting API connection...")
    collector.test_api_connection()
    
    # Fetch some jobs
    print("\nFetching jobs...")
    jobs = collector.fetch_jobs(job_title="Software", max_results=10)
    
    # Process and display the results
    if jobs:
        df = collector.process_jobs(jobs)
        print(f"\nFound {len(df)} jobs:")
        print(df[['title', 'company', 'location']].to_string())
    else:
        print("No jobs found.") 