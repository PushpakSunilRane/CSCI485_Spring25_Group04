import pandas as pd
import numpy as np
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """
    Clean text by removing special characters and extra whitespace
    """
    if not isinstance(text, str):
        return ""
    return ' '.join(text.split())

def calculate_salary_percentile(salary: float, salaries: pd.Series) -> float:
    """
    Calculate the percentile of a salary compared to all salaries
    """
    if pd.isna(salary):
        return np.nan
    return (salaries <= salary).mean() * 100

def get_skill_combinations(skills: List[str]) -> List[tuple]:
    """
    Generate all possible pairs of skills
    """
    combinations = []
    for i in range(len(skills)):
        for j in range(i+1, len(skills)):
            combinations.append((skills[i], skills[j]))
    return combinations

def format_currency(amount: float) -> str:
    """
    Format number as currency string
    """
    if pd.isna(amount):
        return "N/A"
    return f"${amount:,.0f}"

def calculate_skill_demand(skill_matrix: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate the demand score for each skill
    """
    total_jobs = len(skill_matrix)
    skill_demand = {}
    
    for skill in skill_matrix.columns:
        skill_count = skill_matrix[skill].sum()
        skill_demand[skill] = (skill_count / total_jobs) * 100
        
    return skill_demand

def get_job_titles(df: pd.DataFrame) -> List[str]:
    """
    Extract unique job titles from the dataset
    """
    return df['title'].unique().tolist()

def get_locations(df: pd.DataFrame) -> List[str]:
    """
    Extract unique locations from the dataset
    """
    return df['location'].unique().tolist()

def filter_jobs(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Filter jobs based on multiple criteria
    """
    filtered_df = df.copy()
    
    for key, value in filters.items():
        if value:
            if key == 'skills':
                filtered_df = filtered_df[filtered_df['skills'].apply(lambda x: value in x)]
            elif key == 'salary_min':
                filtered_df = filtered_df[filtered_df['avg_salary'] >= value]
            elif key == 'salary_max':
                filtered_df = filtered_df[filtered_df['avg_salary'] <= value]
            else:
                filtered_df = filtered_df[filtered_df[key] == value]
                
    return filtered_df 