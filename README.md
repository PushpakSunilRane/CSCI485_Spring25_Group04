# FINAL PROJECT

# MATH-485 : ADVANCED DATA SCIENCE 

# JOB MARKET ANALYSIS

# Job Market Analysis Dashboard

This project analyzes job market trends using data from the Adzuna API, focusing on Data Analyst positions in California. The analysis includes salary predictions, skill clustering, and interactive visualizations to help job seekers understand market trends.

## Features

- Real-time job data collection from Adzuna API
- Salary prediction model based on job features
- Skill clustering and network analysis
- Interactive dashboard with visualizations
- Job market trend analysis

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Adzuna API credentials:
   ```
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_app_key
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main Streamlit application
- `data_collector.py`: Adzuna API data collection
- `data_processor.py`: Data preprocessing and analysis
- `models.py`: Machine learning models
- `visualizations.py`: Plotting functions
- `utils.py`: Utility functions

## Data Analysis Components

1. **Data Collection**: Fetches job postings from Adzuna API
2. **Preprocessing**: Cleans and structures job data
3. **Clustering**: Groups similar job postings by skills
4. **Salary Prediction**: Predicts salary based on job features
5. **Network Analysis**: Visualizes skill relationships
6. **Dashboard**: Interactive visualization of findings

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