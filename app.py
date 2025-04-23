import streamlit as st
import pandas as pd
from data_collector import JobDataCollector
from data_processor import JobDataProcessor
from visualizations import JobVisualizer

# Page config
st.set_page_config(
    page_title="Job Market Analysis",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None

def main():
    st.title("Job Market Analysis Dashboard")
    
    # Initialize collector
    collector = JobDataCollector()
    
    # Sidebar controls
    st.sidebar.header("Search Options")
    
    # Job title selection
    job_title = st.sidebar.text_input("Job Title (Optional)", 
                                     help="Leave empty to fetch all jobs")
    
    # Location selection
    location = st.sidebar.text_input("Location (Optional)", 
                                    help="Leave empty to fetch jobs from all locations")
    
    # Max results selection
    max_results = st.sidebar.slider("Maximum Results", 10, 100, 50, 10)
    
    # Search button
    if st.sidebar.button("Search Jobs"):
        with st.spinner("Fetching job data..."):
            try:
                # Fetch jobs based on selected options
                jobs = collector.fetch_jobs(job_title, location, max_results)
                    
                if not jobs:
                    st.error("No jobs found with the current filters. Please try different options.")
                    return
                    
                # Process the data
                df = collector.process_jobs(jobs)
                if df.empty:
                    st.error("No valid job data to process. Please try different options.")
                    return
                    
                # Initialize processor and visualizer with the DataFrame
                processor = JobDataProcessor(df)
                visualizer = JobVisualizer(df)
                
                # Display metrics
                st.header("Job Market Overview")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Jobs", len(df))
                with col2:
                    unique_companies = df['company'].nunique()
                    st.metric("Unique Companies", unique_companies)
                with col3:
                    unique_locations = df['location'].nunique()
                    st.metric("Unique Locations", unique_locations)
                
                # Display job types
                st.subheader("Job Types")
                type_counts = df['type'].value_counts()
                if not type_counts.empty:
                    st.bar_chart(type_counts)
                else:
                    st.info("No job type data available")
                
                # Display locations
                st.subheader("Job Locations")
                location_counts = df['location'].value_counts().head(10)
                if not location_counts.empty:
                    st.bar_chart(location_counts)
                else:
                    st.info("No location data available")
                
                # Display companies
                st.subheader("Top Companies")
                company_counts = df['company'].value_counts().head(10)
                if not company_counts.empty:
                    st.bar_chart(company_counts)
                else:
                    st.info("No company data available")
                
                # Display job listings
                st.subheader("Job Listings")
                st.dataframe(df[['title', 'company', 'location', 'type', 'created_at']], 
                           use_container_width=True)
                
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
    else:
        st.info("Please use the sidebar to set your search criteria and click 'Search Jobs' to begin.")

if __name__ == "__main__":
    main() 