import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from datetime import datetime
import re

class JobDataProcessor:
    def __init__(self, df):
        self.df = df.copy()
        
    def clean_data(self):
        """
        Clean and preprocess the job data
        """
        if self.df.empty:
            print("No data to process")
            return self.df
            
        # Convert created_at to datetime if it exists
        if 'created_at' in self.df.columns:
            self.df['created_at'] = pd.to_datetime(self.df['created_at'])
            
        # Fill missing values
        self.df['type'] = self.df['type'].fillna('Unknown')
        self.df['location'] = self.df['location'].fillna('Remote')
        self.df['company'] = self.df['company'].fillna('Unknown Company')
        
        # Extract year and month from created_at if it exists
        if 'created_at' in self.df.columns:
            self.df['year'] = self.df['created_at'].dt.year
            self.df['month'] = self.df['created_at'].dt.month
            
        # Clean salary data
        if 'salary_min' in self.df.columns and 'salary_max' in self.df.columns:
            self.df['salary_min'] = pd.to_numeric(self.df['salary_min'], errors='coerce')
            self.df['salary_max'] = pd.to_numeric(self.df['salary_max'], errors='coerce')
            self.df['avg_salary'] = (self.df['salary_min'] + self.df['salary_max']) / 2
            
        # Extract skills from job description
        if 'description' in self.df.columns:
            self.df['skills'] = self.df['description'].apply(self._extract_skills)
            self.df['skill_count'] = self.df['skills'].apply(len)
            
        return self.df
    
    def _extract_skills(self, description):
        """
        Extract skills from job description using common programming languages and technologies
        """
        if pd.isna(description):
            return []
            
        # Common programming languages and technologies
        skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift',
            'Kotlin', 'Go', 'Rust', 'TypeScript', 'SQL', 'NoSQL', 'MongoDB',
            'PostgreSQL', 'MySQL', 'Oracle', 'AWS', 'Azure', 'GCP', 'Docker',
            'Kubernetes', 'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask',
            'Spring', 'Express', 'TensorFlow', 'PyTorch', 'Machine Learning',
            'Artificial Intelligence', 'Data Science', 'Big Data', 'Hadoop',
            'Spark', 'Kafka', 'Redis', 'Elasticsearch', 'Git', 'CI/CD', 'DevOps'
        ]
        
        # Convert description to string and lowercase
        desc = str(description).lower()
        
        # Find matching skills
        found_skills = []
        for skill in skills:
            if skill.lower() in desc:
                found_skills.append(skill)
                
        return found_skills
    
    def create_skill_matrix(self):
        """
        Create a matrix of job postings vs skills
        """
        if self.df.empty or 'skills' not in self.df.columns:
            return pd.DataFrame()
            
        # Get unique skills
        all_skills = set()
        for skills in self.df['skills']:
            all_skills.update(skills)
        all_skills = sorted(list(all_skills))
        
        if not all_skills:
            return pd.DataFrame()
            
        # Create skill matrix
        skill_matrix = pd.DataFrame(0, index=self.df.index, columns=all_skills)
        for idx, skills in enumerate(self.df['skills']):
            for skill in skills:
                skill_matrix.loc[idx, skill] = 1
                
        return skill_matrix
    
    def cluster_jobs(self, n_clusters=5):
        """
        Cluster jobs based on skills and features
        """
        if self.df.empty:
            return self.df
            
        skill_matrix = self.create_skill_matrix()
        if skill_matrix.empty:
            self.df['cluster'] = 0
            return self.df
        
        # Add numerical features
        features = pd.concat([
            skill_matrix,
            self.df[['skill_count']]
        ], axis=1)
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=min(n_clusters, len(self.df)), random_state=42)
        self.df['cluster'] = kmeans.fit_predict(scaled_features)
        
        return self.df
    
    def analyze_skill_relationships(self):
        """
        Analyze relationships between skills
        """
        skill_matrix = self.create_skill_matrix()
        if skill_matrix.empty:
            return pd.DataFrame()
        return skill_matrix.corr()
    
    def get_cluster_summary(self):
        """
        Get summary statistics for each cluster
        """
        if self.df.empty:
            return pd.DataFrame()
            
        cluster_summary = self.df.groupby('cluster').agg({
            'avg_salary': ['mean', 'std', 'count'],
            'skill_count': ['mean', 'std'],
            'type': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'
        }).round(2)
        
        return cluster_summary
    
    def get_top_skills(self, n=10):
        """
        Get the most common skills across all job postings
        """
        skill_matrix = self.create_skill_matrix()
        if skill_matrix.empty:
            return pd.Series()
        skill_counts = skill_matrix.sum().sort_values(ascending=False)
        return skill_counts.head(n)
        
    def analyze_salary_by_skill(self):
        """
        Analyze average salary for each skill
        """
        if self.df.empty or 'avg_salary' not in self.df.columns:
            return pd.Series()
            
        skill_matrix = self.create_skill_matrix()
        if skill_matrix.empty:
            return pd.Series()
            
        # Calculate average salary for each skill
        salary_by_skill = {}
        for skill in skill_matrix.columns:
            skill_jobs = self.df[skill_matrix[skill] == 1]
            if not skill_jobs.empty:
                avg_salary = skill_jobs['avg_salary'].mean()
                if not pd.isna(avg_salary):
                    salary_by_skill[skill] = avg_salary
                    
        return pd.Series(salary_by_skill).sort_values(ascending=False)
    
    def get_job_trends(self):
        """
        Analyze job posting trends over time
        """
        if self.df.empty or 'created_at' not in self.df.columns:
            return pd.DataFrame()
            
        # Group by month and count jobs
        trends = self.df.groupby(['year', 'month']).size().reset_index(name='count')
        trends['date'] = pd.to_datetime(trends[['year', 'month']].assign(day=1))
        
        return trends
    
    def get_top_companies(self, n=10):
        """
        Get the companies with the most job postings
        """
        if self.df.empty:
            return pd.Series()
        return self.df['company'].value_counts().head(n)
    
    def get_top_locations(self, n=10):
        """
        Get the locations with the most job postings
        """
        if self.df.empty:
            return pd.Series()
        return self.df['location'].value_counts().head(n)
    
    def get_job_types_distribution(self):
        """
        Get the distribution of job types
        """
        if self.df.empty:
            return pd.Series()
        return self.df['type'].value_counts()
    
    def get_recent_jobs(self, days=7):
        """
        Get jobs posted in the last n days
        """
        if self.df.empty or 'created_at' not in self.df.columns:
            return pd.DataFrame()
            
        recent_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        return self.df[self.df['created_at'] >= recent_date] 