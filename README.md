# Job Search Application

This project is a web-based job search application that aggregates job listings from Indeed and StepStone. The application provides users with an interface to search for jobs based on various criteria such as job title, location, radius, job type, and posting date. Users can also exclude specific keywords from their search results.

##  Features

- **Search Across Multiple Platforms:** The application searches for jobs on Indeed and StepStone.
- **Filter and Exclude Keywords:** Users can filter results by job title, location, and job type, and can exclude jobs containing specific keywords.
- **Sort by Date:** Results can be sorted by the date the job was posted.
- **Responsive Design:** The application is designed to work on different screen sizes.

## Technologies Used

- **Flask:** A lightweight WSGI web application framework for Python.
- **Selenium:** A browser automation tool used to scrape job data from Indeed and StepStone.
- **HTML/CSS:** For structuring and styling the web pages.
- **JavaScript:** For dynamic interactions on the frontend.
- **WebDriver Manager:** To manage the Chrome WebDriver automatically.

## Setup Instructions

### Prerequisites

- Python 3.x
- Chrome browser

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Julscha9291/Job_App
   cd Job_App

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`

3. Install the required packages:
pip install -r requirements.txt

4. Run the Flask application:
python app.py

5.Open your browser and navigate to http://localhost:5000 to access the application.

### Usage

1. Enter the desired job title, location, radius, job type, and date range.
2. Optionally, enter keywords to exclude certain jobs from the results.
3. Click the "Search" button to retrieve job listings.
4. View the aggregated results, sorted by the date they were posted.

