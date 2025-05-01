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

# GitHub Jobs Dashboard

A dashboard application that searches for job postings in GitHub repositories using the GitHub API.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your GitHub token:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```
   To get a GitHub token:
   - Go to GitHub.com and log in
   - Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with the `repo` scope
   - Copy the token and paste it in the `.env` file

## Usage

1. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```
2. Use the sidebar to:
   - Enter a job title to search for
   - Optionally specify a location
   - Choose maximum number of results
3. Click 'Search Jobs' to start the search
4. View results in the main panel:
   - Expandable job listings with details
   - Analytics charts showing job distribution
   - Option to save results to CSV

## Features

- Search GitHub repositories for job postings
- Filter by job title and location
- Interactive dashboard with Streamlit
- Data visualization with Plotly
- Export results to CSV
- Rate limit handling
- Flexible job information extraction

## Files

- `data_collector.py`: Core job data collection logic
- `dashboard.py`: Streamlit dashboard interface
- `requirements.txt`: Project dependencies
- `.env`: GitHub API token configuration