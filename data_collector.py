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
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
        
        # Verify API credentials
        if not self.app_id or not self.app_key:
            print("Error: Missing API credentials. Please check your .env file.")
            print(f"APP_ID: {'Present' if self.app_id else 'Missing'}")
            print(f"APP_KEY: {'Present' if self.app_key else 'Missing'}")
        else:
            print("API credentials found. Testing connection...")
            self.test_api_connection()
        
    def test_api_connection(self):
        """Test the API connection with a simple request"""
        try:
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': 1,
                'page': 1,
                'what': 'software',
                'where': 'us'
            }
            
            print(f"\nTesting API connection...")
            print(f"Request URL: {self.base_url}")
            print(f"Request Parameters: {params}")
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print("API connection successful!")
                print(f"Response status: {response.status_code}")
                print(f"Number of results: {len(data.get('results', []))}")
            else:
                print(f"API Error: {response.status_code}")
                print(f"Error message: {response.text}")
                
        except Exception as e:
            print(f"Error testing API connection: {str(e)}")
        
    def fetch_jobs(self, job_title=None, location=None, max_results=100):
        """
        Fetch job postings from Adzuna API
        If job_title or location is None, fetch all available jobs
        """
        if not self.app_id or not self.app_key:
            print("Error: Missing API credentials. Cannot fetch jobs.")
            return []
            
        jobs = []
        page = 1
        results_per_page = min(50, max_results)  # Limit results per page
        
        print(f"\nStarting job fetch with parameters:")
        print(f"Job Title: {job_title}")
        print(f"Location: {location}")
        print(f"Max Results: {max_results}")
        
        while len(jobs) < max_results:
            # Format the search parameters
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': results_per_page,
                'page': page,
                'what': job_title if job_title else 'all',
                'where': location if location else 'us'
            }
            
            try:
                print(f"\nMaking API request to: {self.base_url}")
                print(f"With parameters: {params}")
                
                response = requests.get(self.base_url, params=params)
                
                # Check for API errors
                if response.status_code != 200:
                    print(f"API Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
                data = response.json()
                print(f"API Response: {data}")
                
                if not data.get('results'):
                    print("No results found in API response")
                    print(f"Response data: {data}")
                    break
                    
                jobs.extend(data['results'])
                print(f"Fetched {len(jobs)} jobs so far...")
                page += 1
                
                # Respect API rate limits
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response status: {e.response.status_code}")
                    print(f"Response text: {e.response.text}")
                break
                
        print(f"\nTotal jobs fetched: {len(jobs)}")
        return jobs[:max_results]
    
    def fetch_jobs_by_category(self, category, max_results=100):
        """
        Fetch jobs by category
        """
        if not self.app_id or not self.app_key:
            print("Error: Missing API credentials. Cannot fetch jobs.")
            return []
            
        jobs = []
        page = 1
        results_per_page = min(50, max_results)  # Limit results per page
        
        print(f"\nStarting category job fetch:")
        print(f"Category: {category}")
        print(f"Max Results: {max_results}")
        
        while len(jobs) < max_results:
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'category': category,
                'results_per_page': results_per_page,
                'page': page,
                'where': 'us'
            }
            
            try:
                print(f"\nMaking API request to: {self.base_url}")
                print(f"With parameters: {params}")
                
                response = requests.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    print(f"API Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
                data = response.json()
                print(f"API Response: {data}")
                
                if not data.get('results'):
                    print("No results found in API response")
                    print(f"Response data: {data}")
                    break
                    
                jobs.extend(data['results'])
                print(f"Fetched {len(jobs)} jobs so far...")
                page += 1
                
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response status: {e.response.status_code}")
                    print(f"Response text: {e.response.text}")
                break
                
        print(f"\nTotal jobs fetched: {len(jobs)}")
        return jobs[:max_results]
    
    def process_jobs(self, jobs):
        """
        Process raw job data into a structured DataFrame
        """
        if not jobs:
            print("No jobs to process")
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description',
                'salary_min', 'salary_max', 'salary_currency',
                'created', 'contract_type', 'category', 'skills'
            ])
            
        processed_jobs = []
        
        for job in jobs:
            # Extract skills from description
            skills = self._extract_skills(job.get('description', ''))
            
            processed_job = {
                'title': job.get('title', ''),
                'company': job.get('company', {}).get('display_name', ''),
                'location': job.get('location', {}).get('display_name', ''),
                'description': job.get('description', ''),
                'salary_min': job.get('salary_min', None),
                'salary_max': job.get('salary_max', None),
                'salary_currency': job.get('salary_currency', 'USD'),
                'created': job.get('created', ''),
                'contract_type': job.get('contract_type', ''),
                'category': job.get('category', {}).get('label', ''),
                'skills': skills
            }
            processed_jobs.append(processed_job)
            
        # Create DataFrame
        df = pd.DataFrame(processed_jobs)
        
        # Ensure skills column exists and is a list
        if 'skills' not in df.columns:
            df['skills'] = [[] for _ in range(len(df))]
        elif not isinstance(df['skills'].iloc[0], list):
            df['skills'] = df['skills'].apply(lambda x: x if isinstance(x, list) else [])
            
        return df
    
    def _extract_skills(self, description):
        """
        Extract skills from job description
        """
        if not description:
            return []
            
        # Common skills to look for (expanded list)
        common_skills = [
            # Technical Skills
            'SQL', 'Python', 'R', 'Java', 'JavaScript', 'C++', 'C#', 'PHP',
            'HTML', 'CSS', 'React', 'Angular', 'Node.js', 'Django', 'Flask',
            'Tableau', 'Power BI', 'Excel', 'SAS', 'SPSS',
            
            # Data & Analytics
            'Machine Learning', 'Data Visualization', 'Statistics',
            'Data Mining', 'ETL', 'Data Warehousing', 'Big Data',
            'Hadoop', 'Spark', 'AWS', 'Azure', 'Google Cloud',
            
            # Business & Management
            'Project Management', 'Agile', 'Scrum', 'Business Analysis',
            'Strategic Planning', 'Leadership', 'Team Management',
            
            # Design & Creative
            'Photoshop', 'Illustrator', 'UI/UX', 'Graphic Design',
            'Video Editing', 'Motion Graphics',
            
            # Marketing & Sales
            'Digital Marketing', 'SEO', 'Social Media', 'Content Marketing',
            'Email Marketing', 'Sales', 'Business Development',
            
            # Finance & Accounting
            'Financial Analysis', 'Accounting', 'Budgeting', 'Forecasting',
            'Risk Management', 'Compliance',
            
            # Healthcare
            'Medical', 'Nursing', 'Healthcare', 'Patient Care',
            'Clinical Research', 'Pharmaceutical',
            
            # Education
            'Teaching', 'Curriculum Development', 'Educational Technology',
            'Student Services', 'Academic Advising'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in description.lower():
                found_skills.append(skill)
                
        return found_skills
    
    def save_data(self, df, filename='job_data.csv'):
        """
        Save processed data to CSV
        """
        if df.empty:
            print("No data to save")
            return
            
        # Ensure skills column exists
        if 'skills' not in df.columns:
            df['skills'] = [[] for _ in range(len(df))]
            
        # Convert skills list to string for CSV storage
        df_to_save = df.copy()
        df_to_save['skills'] = df_to_save['skills'].apply(str)
        df_to_save.to_csv(filename, index=False)
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
                    'salary_min', 'salary_max', 'salary_currency',
                    'created', 'contract_type', 'category', 'skills'
                ])
                
            # Convert skills string back to list
            if 'skills' in df.columns:
                df['skills'] = df['skills'].apply(eval)
            else:
                df['skills'] = [[] for _ in range(len(df))]
            return df
        except (pd.errors.EmptyDataError, FileNotFoundError):
            print(f"Could not load {filename}")
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description',
                'salary_min', 'salary_max', 'salary_currency',
                'created', 'contract_type', 'category', 'skills'
            ]) 