import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import ast

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
            
        # Initialize skills column if it doesn't exist
        if 'skills' not in self.df.columns:
            self.df['skills'] = [[] for _ in range(len(self.df))]
        
        # Convert skills from string to list if it's a string
        if len(self.df) > 0 and isinstance(self.df['skills'].iloc[0], str):
            self.df['skills'] = self.df['skills'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        
        # Calculate average salary
        self.df['avg_salary'] = self.df.apply(
            lambda x: (x['salary_min'] + x['salary_max']) / 2 
            if pd.notnull(x['salary_min']) and pd.notnull(x['salary_max']) 
            else x['salary_min'] if pd.notnull(x['salary_min']) 
            else x['salary_max'] if pd.notnull(x['salary_max']) 
            else np.nan, 
            axis=1
        )
        
        # Create skill count feature
        self.df['skill_count'] = self.df['skills'].apply(len)
        
        # Convert contract type to categorical
        self.df['contract_type'] = self.df['contract_type'].fillna('Unknown')
        
        # Extract year from created date
        if 'created' in self.df.columns:
            self.df['year'] = pd.to_datetime(self.df['created']).dt.year
        else:
            self.df['year'] = pd.Timestamp.now().year
            
        return self.df
    
    def create_skill_matrix(self):
        """
        Create a matrix of job postings vs skills
        """
        if self.df.empty:
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
            'contract_type': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'
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