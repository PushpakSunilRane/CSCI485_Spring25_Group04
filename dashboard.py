import streamlit as st
import pandas as pd
import plotly.express as px
from data_collector import JobDataCollector

st.set_page_config(page_title="Job Market Dashboard", layout="wide")

st.title("Job Market Dashboard")

# Initialize the collector
collector = JobDataCollector()

# Sidebar filters
st.sidebar.header("Search Filters")
job_title = st.sidebar.text_input("Job Title", "")
location = st.sidebar.text_input("Location", "")
max_results = st.sidebar.slider("Maximum Results", 10, 100, 20)

# Search button
if st.sidebar.button("Search Jobs"):
    if not job_title:
        st.error("Please enter a job title to search for")
    else:
        with st.spinner("Fetching jobs..."):
            if collector.test_api_connection():
                # Fetch jobs
                jobs = collector.fetch_jobs(job_title=job_title, location=location, max_results=max_results)
                
                if jobs:
                    # Process jobs into DataFrame
                    df = collector.process_jobs(jobs)
                    
                    # Display results
                    st.subheader(f"Found {len(df)} Jobs")
                    
                    # Job listings
                    for _, job in df.iterrows():
                        with st.expander(f"{job['title']} at {job['company']}"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write("**Description:**", job['description'])
                                st.write("**Category:**", job['category'])
                                st.write("**URL:**", job['url'])
                            
                            with col2:
                                st.write("**Location:**", job['location'])
                                st.write("**Type:**", job['type'])
                                if job['salary_min'] and job['salary_max']:
                                    st.write("**Salary Range:**", f"${job['salary_min']} - ${job['salary_max']}")
                                st.write("**Posted:**", job['created_at'])
                                
                    # Analytics
                    st.subheader("Job Analytics")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Location distribution
                        if not df['location'].empty:
                            location_counts = df['location'].value_counts()
                            fig = px.pie(values=location_counts.values, 
                                       names=location_counts.index, 
                                       title="Jobs by Location")
                            st.plotly_chart(fig)
                    
                    with col2:
                        # Job type distribution
                        if not df['type'].empty:
                            type_counts = df['type'].value_counts()
                            fig = px.bar(x=type_counts.index, 
                                       y=type_counts.values,
                                       title="Jobs by Type")
                            st.plotly_chart(fig)
                    
                    # Salary analysis
                    if 'salary_min' in df.columns and 'salary_max' in df.columns:
                        df['salary_avg'] = (df['salary_min'].fillna(0) + df['salary_max'].fillna(0)) / 2
                        if not df['salary_avg'].empty and df['salary_avg'].sum() > 0:
                            st.subheader("Salary Analysis")
                            fig = px.box(df, y='salary_avg', title="Salary Distribution")
                            st.plotly_chart(fig)
                    
                    # Save data option
                    if st.button("Save Results to CSV"):
                        collector.save_data(df)
                        st.success("Data saved to job_data.csv")
                else:
                    st.error("No jobs found. Try adjusting your search criteria.")
            else:
                st.error("Failed to connect to the job API. Please check your API credentials.") 