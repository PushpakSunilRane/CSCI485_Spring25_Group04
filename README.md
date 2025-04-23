# FINAL PROJECT

# MATH-485 : ADVANCED DATA SCIENCE 

# JOB MARKET ANALYSIS

# Job Market Analysis Dashboard

A Streamlit-based dashboard for analyzing job market trends using the GitHub Jobs API.

## Features

- Real-time job data fetching from GitHub Jobs API
- Interactive job search by title and location
- Visualizations of job market trends
- Analysis of top companies and locations
- Job type distribution analysis
- Recent job postings tracking

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Use the sidebar to:
   - Enter job title (optional)
   - Enter location (optional)
   - Set maximum number of results
   - Click "Search Jobs" to fetch and analyze data

3. View the dashboard to see:
   - Job market overview metrics
   - Job posting trends
   - Top companies and locations
   - Job type distribution
   - Recent job listings

## Data Sources

This project uses the [GitHub Jobs API](https://jobs.github.com/api) to fetch job data. The API is free to use and provides job listings from various companies that post on GitHub Jobs.

## Project Structure

- `app.py`: Main Streamlit application
- `data_collector.py`: Handles data fetching from GitHub Jobs API
- `data_processor.py`: Processes and analyzes job data
- `visualizations.py`: Creates interactive visualizations
- `requirements.txt`: Lists required Python packages

## Contributing

Feel free to submit issues and enhancement requests!

## Technologies Used

- Python
- Streamlit
- Scikit-learn
- NetworkX
- Pandas
- Plotly
- SerpAPI
- Adzuna API
- USAJobs API