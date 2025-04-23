import streamlit as st
import pandas as pd
from data_collector import JobDataCollector
from data_processor import JobDataProcessor
from visualizations import JobVisualizer
import os
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="Job Market Analysis",
    page_icon="📊",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None

def main():
    st.title("US Job Market Analysis Dashboard")
    
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
    
    # Category selection
    categories = [
        "IT Jobs", "Engineering Jobs", "Healthcare Jobs", "Finance Jobs",
        "Marketing Jobs", "Sales Jobs", "Education Jobs", "Design Jobs"
    ]
    category = st.sidebar.selectbox("Job Category (Optional)", 
                                  [None] + categories,
                                  help="Select a category to filter jobs")
    
    # Max results selection - updated range
    max_results = st.sidebar.slider("Maximum Results", 10, 100, 50, 10)
    
    # Search button
    if st.sidebar.button("Search Jobs"):
        with st.spinner("Fetching job data..."):
            try:
                # Fetch jobs based on selected options
                if category:
                    jobs = collector.fetch_jobs_by_category(category, max_results)
                else:
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
                    avg_salary = df['salary_min'].mean()
                    st.metric("Average Salary", f"${avg_salary:,.2f}" if not pd.isna(avg_salary) else "N/A")
                with col3:
                    unique_companies = df['company'].nunique()
                    st.metric("Unique Companies", unique_companies)
                
                # Display job categories
                st.subheader("Job Categories")
                category_counts = df['category'].value_counts()
                if not category_counts.empty:
                    st.bar_chart(category_counts)
                else:
                    st.info("No category data available")
                
                # Display locations
                st.subheader("Job Locations")
                location_counts = df['location'].value_counts().head(10)
                if not location_counts.empty:
                    st.bar_chart(location_counts)
                else:
                    st.info("No location data available")
                
                # Process data for visualizations
                try:
                    # Clean and prepare data
                    df = processor.clean_data()
                    
                    # Create skill matrix
                    skill_matrix = processor.create_skill_matrix()
                    if not skill_matrix.empty:
                        # Display top skills
                        st.subheader("Top Required Skills")
                        top_skills = processor.get_top_skills()
                        st.bar_chart(top_skills)
                        
                        # Display skill relationships
                        st.subheader("Skill Relationships")
                        skill_relationships = processor.analyze_skill_relationships()
                        visualizer.plot_skill_network(skill_relationships)
                        
                        # Display salary by skill
                        st.subheader("Average Salary by Skill")
                        salary_by_skill = processor.analyze_salary_by_skill()
                        visualizer.plot_salary_by_skill(salary_by_skill)
                    else:
                        st.info("No skill data available for analysis")
                        
                    # Cluster jobs
                    clusters = processor.cluster_jobs()
                    if clusters is not None:
                        st.subheader("Job Clusters")
                        cluster_summary = processor.get_cluster_summary()
                        visualizer.plot_clusters(cluster_summary)
                    else:
                        st.info("No clustering data available")
                        
                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
                    
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
    else:
        st.info("Please use the sidebar to set your search criteria and click 'Search Jobs' to begin.")

if __name__ == "__main__":
    main() 