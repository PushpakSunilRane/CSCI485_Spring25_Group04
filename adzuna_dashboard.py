import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime, timedelta
#from dotenv import load_dotenv
from data_processor import JobDataProcessor
import random

# Load environment variables
load_dotenv()

# Adzuna API configuration
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"

# Available countries for Adzuna API
ADZUNA_COUNTRIES = {
    'us': 'United States',
    'gb': 'United Kingdom',
    'au': 'Australia',
    'br': 'Brazil',
    'ca': 'Canada',
    'de': 'Germany',
    'fr': 'France',
    'in': 'India',
    'it': 'Italy',
    'mx': 'Mexico',
    'nl': 'Netherlands',
    'nz': 'New Zealand',
    'pl': 'Poland',
    'ru': 'Russia',
    'sg': 'Singapore',
    'es': 'Spain',
    'za': 'South Africa'
}

# Dynamic color schemes
COLOR_SCHEMES = [
    ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD'],  # Warm to Cool
    ['#2E86C1', '#3498DB', '#5DADE2', '#85C1E9', '#AED6F1'],  # Blue Shades
    ['#E74C3C', '#EC7063', '#F1948A', '#F5B7B1', '#FADBD8'],  # Red Shades
    ['#27AE60', '#2ECC71', '#58D68D', '#82E0AA', '#ABEBC6'],  # Green Shades
    ['#8E44AD', '#9B59B6', '#AF7AC5', '#C39BD3', '#D7BDE2'],  # Purple Shades
    ['#D35400', '#E67E22', '#F39C12', '#F1C40F', '#F9E79F'],  # Orange Shades
    ['#1ABC9C', '#16A085', '#138D75', '#117A65', '#0E6655'],  # Teal Shades
    ['#C0392B', '#E74C3C', '#F1948A', '#F5B7B1', '#FADBD8'],  # Burgundy Shades
]

def get_random_color_scheme():
    """Get a random color scheme from the available schemes"""
    return random.choice(COLOR_SCHEMES)

st.set_page_config(page_title="Job Market Analytics Dashboard", layout="wide")

# Initialize session state
if 'jobs' not in st.session_state:
    st.session_state.jobs = pd.DataFrame()
    st.session_state.processor = None
    st.session_state.current_color_scheme = get_random_color_scheme()

def fetch_jobs(job_title="", country="us", max_results=20):
    """Fetch jobs from Adzuna API"""
    try:
        # Update base URL with selected country
        base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'results_per_page': max_results,
            'what': job_title,
            'content-type': 'application/json'
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'results' in data:
            # Update color scheme when new search is performed
            st.session_state.current_color_scheme = get_random_color_scheme()
            return data['results']
        return []
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return []

def process_jobs(jobs):
    """Process raw job data into a structured DataFrame"""
    if not jobs:
        return pd.DataFrame()
        
    processed_jobs = []
    for job in jobs:
        processed_job = {
            'title': job.get('title', ''),
            'company': job.get('company', {}).get('display_name', ''),
            'location': job.get('location', {}).get('display_name', ''),
            'description': job.get('description', ''),
            'type': job.get('contract_type', ''),
            'created_at': job.get('created', ''),
            'url': job.get('redirect_url', ''),
            'salary_min': job.get('salary_min', 0),
            'salary_max': job.get('salary_max', 0),
            'category': job.get('category', {}).get('label', '')
        }
        processed_jobs.append(processed_job)
    
    return pd.DataFrame(processed_jobs)

def create_salary_by_location_plot(df):
    """Create a salary distribution plot by location"""
    # Calculate average salary for each location
    location_salary = df.groupby('location').agg({
        'salary_min': 'mean',
        'salary_max': 'mean'
    }).reset_index()
    
    location_salary['avg_salary'] = (location_salary['salary_min'] + location_salary['salary_max']) / 2
    
    fig = px.bar(
        location_salary,
        x='location',
        y='avg_salary',
        title='Average Salary by Location',
        color='avg_salary',
        color_continuous_scale=st.session_state.current_color_scheme,
        labels={'avg_salary': 'Average Salary (USD)', 'location': 'Location'}
    )
    
    fig.update_layout(
        template='plotly_white',
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

st.title("Job Market Analytics Dashboard")

# Sidebar filters
st.sidebar.header("Search & Filters")

# Search functionality
job_title = st.sidebar.text_input("Job Title", "")
country = st.sidebar.selectbox("Select Country (Optional)", [''] + list(ADZUNA_COUNTRIES.keys()), format_func=lambda x: ADZUNA_COUNTRIES.get(x, 'All Countries'))
max_results = st.sidebar.slider("Maximum Results", 5, 100, 10)

# Search button
if st.sidebar.button("Search Jobs"):
    if not job_title:
        st.error("Please enter a job title to search for")
    else:
        with st.spinner("Fetching jobs..."):
            # Use 'us' as default if no country selected
            selected_country = country if country else 'us'
            jobs = fetch_jobs(job_title=job_title, country=selected_country, max_results=max_results)
            
            if jobs:
                # Process jobs into DataFrame
                st.session_state.jobs = process_jobs(jobs)
                st.session_state.processor = JobDataProcessor(st.session_state.jobs)
                st.session_state.jobs = st.session_state.processor.clean_data()
            else:
                st.error("No jobs found. Try adjusting your search criteria.")

# Salary range filter
if not st.session_state.jobs.empty:
    st.sidebar.subheader("Salary Filter")
    
    try:
        if 'salary_min' in st.session_state.jobs.columns and 'salary_max' in st.session_state.jobs.columns:
            # Filter out zero or negative salaries
            valid_salaries = st.session_state.jobs[
                (st.session_state.jobs['salary_min'] > 0) & 
                (st.session_state.jobs['salary_max'] > 0)
            ]
            
            if not valid_salaries.empty:
                min_salary = int(valid_salaries['salary_min'].min())
                max_salary = int(valid_salaries['salary_max'].max())
                
                if min_salary < max_salary:
                    salary_range = st.sidebar.slider(
                        "Salary Range (USD)",
                        min_value=min_salary,
                        max_value=max_salary,
                        value=(min_salary, max_salary)
                    )
                else:
                    st.sidebar.info("No valid salary range available for filtering")
            else:
                st.sidebar.info("No valid salary data available for filtering")
    except Exception as e:
        st.sidebar.error("Error processing salary data")

# Apply salary filter
if not st.session_state.jobs.empty:
    filtered_df = st.session_state.jobs.copy()
    
    try:
        if 'salary_min' in filtered_df.columns and 'salary_max' in filtered_df.columns and 'salary_range' in locals():
            filtered_df = filtered_df[
                (filtered_df['salary_min'] >= salary_range[0]) &
                (filtered_df['salary_max'] <= salary_range[1])
            ]
    except Exception as e:
        st.error("Error applying salary filter")

    # Main content
    st.subheader(f"Found {len(filtered_df)} jobs for {job_title} in {ADZUNA_COUNTRIES[selected_country]}")

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Job Listings", "Skills Analysis", "Market Trends", "Company Insights"])

    with tab1:
        # Job listings with enhanced information
        for _, job in filtered_df.iterrows():
            with st.expander(f"{job['title']} at {job['company']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Description:**", job['description'])
                    if 'skills' in job and isinstance(job['skills'], list):
                        st.write("**Required Skills:**", ", ".join(job['skills']))
                    st.write("**URL:**", job['url'])
                
                with col2:
                    st.write("**Location:**", job['location'])
                    st.write("**Type:**", job['type'])
                    if 'salary_min' in job and 'salary_max' in job:
                        st.write("**Salary Range:**", f"${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
                    if 'created_at' in job:
                        st.write("**Posted:**", job['created_at'])

    with tab2:
        # Skills analysis
        st.subheader("Skills Analysis")
        
        # Top skills visualization
        top_skills = st.session_state.processor.get_top_skills(10)
        if not top_skills.empty:
            fig = px.bar(
                x=top_skills.values,
                y=top_skills.index,
                orientation='h',
                title="Most In-Demand Skills",
                color=top_skills.values,
                color_continuous_scale=st.session_state.current_color_scheme
            )
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        # Salary by location
        st.plotly_chart(
            create_salary_by_location_plot(filtered_df),
            use_container_width=True
        )

    with tab3:
        # Market trends
        st.subheader("Market Trends Analysis")
        
        # Create three columns for different trend visualizations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Job posting trends with moving average
            trends = st.session_state.processor.get_job_trends()
            if not trends.empty:
                # Calculate 7-day moving average
                trends['moving_avg'] = trends['count'].rolling(window=7, min_periods=1).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trends['date'],
                    y=trends['count'],
                    name='Daily Postings',
                    mode='lines+markers',
                    line=dict(color=st.session_state.current_color_scheme[0])
                ))
                fig.add_trace(go.Scatter(
                    x=trends['date'],
                    y=trends['moving_avg'],
                    name='7-Day Moving Average',
                    mode='lines',
                    line=dict(color=st.session_state.current_color_scheme[1], dash='dash')
                ))
                fig.update_layout(
                    title="Job Posting Trends Over Time",
                    template='plotly_white',
                    xaxis_title="Date",
                    yaxis_title="Number of Postings",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Salary trends over time
            if 'salary_min' in filtered_df.columns and 'salary_max' in filtered_df.columns:
                salary_trends = filtered_df.copy()
                salary_trends['created_at'] = pd.to_datetime(salary_trends['created_at'])
                salary_trends['avg_salary'] = (salary_trends['salary_min'] + salary_trends['salary_max']) / 2
                salary_trends = salary_trends.groupby(salary_trends['created_at'].dt.date)['avg_salary'].mean().reset_index()
                
                fig = px.line(
                    salary_trends,
                    x='created_at',
                    y='avg_salary',
                    title="Average Salary Trends Over Time",
                    color_discrete_sequence=st.session_state.current_color_scheme
                )
                fig.update_layout(
                    template='plotly_white',
                    xaxis_title="Date",
                    yaxis_title="Average Salary (USD)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Job type distribution with enhanced labels
            type_dist = st.session_state.processor.get_job_types_distribution()
            if not type_dist.empty:
                # Clean and standardize job type labels
                type_dist.index = type_dist.index.str.replace('_', ' ').str.title()
                type_dist = type_dist.sort_values(ascending=False)
                
                fig = px.pie(
                    values=type_dist.values,
                    names=type_dist.index,
                    title="Job Type Distribution",
                    color_discrete_sequence=st.session_state.current_color_scheme
                )
                fig.update_layout(
                    template='plotly_white',
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional market insights
        st.subheader("Additional Market Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            # Top growing skills
            skills_trend = st.session_state.processor.get_skills_trend()
            if not skills_trend.empty:
                fig = px.bar(
                    skills_trend.head(10),
                    x='growth_rate',
                    y='skill',
                    orientation='h',
                    title="Top Growing Skills",
                    color='growth_rate',
                    color_continuous_scale=st.session_state.current_color_scheme
                )
                fig.update_layout(
                    template='plotly_white',
                    xaxis_title="Growth Rate (%)",
                    yaxis_title="Skill"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Location-based salary comparison
            location_salary = filtered_df.groupby('location').agg({
                'salary_min': 'mean',
                'salary_max': 'mean'
            }).reset_index()
            location_salary['avg_salary'] = (location_salary['salary_min'] + location_salary['salary_max']) / 2
            location_salary = location_salary.sort_values('avg_salary', ascending=False).head(10)
            
            fig = px.bar(
                location_salary,
                x='avg_salary',
                y='location',
                orientation='h',
                title="Top 10 Highest Paying Locations",
                color='avg_salary',
                color_continuous_scale=st.session_state.current_color_scheme
            )
            fig.update_layout(
                template='plotly_white',
                xaxis_title="Average Salary (USD)",
                yaxis_title="Location"
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        # Company insights
        col1, col2 = st.columns(2)
        
        with col1:
            # Top companies
            top_companies = st.session_state.processor.get_top_companies(10)
            if not top_companies.empty:
                fig = px.bar(
                    x=top_companies.values,
                    y=top_companies.index,
                    orientation='h',
                    title="Top Companies by Job Postings",
                    color=top_companies.values,
                    color_continuous_scale=st.session_state.current_color_scheme
                )
                fig.update_layout(template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top locations
            top_locations = st.session_state.processor.get_top_locations(10)
            if not top_locations.empty:
                fig = px.bar(
                    x=top_locations.values,
                    y=top_locations.index,
                    orientation='h',
                    title="Top Locations by Job Postings",
                    color=top_locations.values,
                    color_continuous_scale=st.session_state.current_color_scheme
                )
                fig.update_layout(template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

    # Download option
    if st.button("Download Results"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="job_results.csv",
            mime="text/csv"
        ) 