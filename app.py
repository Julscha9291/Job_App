from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime, timedelta
import requests
from pyvirtualdisplay import Display
import os


app = Flask(__name__)



def initialize_driver():
    """Initialisiert den WebDriver mit den angegebenen Optionen."""
    os.environ["WDM_LOCAL"] = "/tmp/.wdm"
    
    options = Options()
    options.add_argument("--headless=new")  # Headless-Modus
    options.add_argument("--no-sandbox")    # notwendig für Linux-Server
    options.add_argument("--disable-dev-shm-usage")  # verhindert Speicherprobleme
    options.add_argument("--remote-debugging-port=9222")  # um DevToolsActivePort-Fehler zu vermeiden
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    
    
    options.binary_location = "/usr/bin/chromium-browser"

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def close_popup(driver):
    """Versucht, ein Popup-Fenster zu schließen, falls vorhanden."""
    try:
        popup = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler')))
        popup.click()
        print("Popup geschlossen.")
    except:
        print("Kein Popup gefunden.")

def capture_cookies(driver):
    """Erfasst und speichert die Cookies des WebDriver."""
    return driver.get_cookies()

def extract_job_information_indeed(driver, exclude_words=None):
    if exclude_words is None:
        exclude_words = []
    else:
        exclude_words = [word.strip() for word in exclude_words if word.strip()]

    job_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "job_seen_beacon")]')

    if not job_elements:
        print("Keine Job-Elemente gefunden auf der Seite.")
    
    job_info = []
    seen_jobs = set()  
    
    for job_element in job_elements:
        job_title_element = job_element.find_element(By.XPATH, './/span[@title]')
        job_title = job_title_element.get_attribute("title")

        if exclude_words and any(word.lower() in job_title.lower() for word in exclude_words):
            continue
        
        company_name_element = job_element.find_element(By.XPATH, './/span[@data-testid="company-name"]')
        company_name = company_name_element.text
        location_element = job_element.find_element(By.XPATH, './/div[@data-testid="text-location"]')
        location = location_element.text
        job_link_element = job_element.find_element(By.XPATH, './/a')
        job_link = job_link_element.get_attribute("href")
        
        job_identifier = (job_title, company_name, location) 
        
        if job_identifier not in seen_jobs: 
            seen_jobs.add(job_identifier)
            job_info.append({
                "title": job_title,
                "company": company_name,
                "location": location,
                "link": job_link,
                "date": job_element.find_element(By.XPATH, './/span[@data-testid="myJobsStateDate"]').text  
            })
    
    return job_info


def extract_job_information_stepstone(driver, exclude_words=None, target_location=None):
    if exclude_words is None:
        exclude_words = []
    else:
        exclude_words = [word.strip() for word in exclude_words if word.strip()]


    print(f"Ausschlusswörter: {exclude_words}")

    job_elements = driver.find_elements(By.XPATH, './/article[@data-at="job-item"]')

    if not job_elements:
        print("Keine Job-Elemente gefunden auf der Seite.")
    
    job_info = []
    seen_jobs = set()  

    for job_element in job_elements:
        try:
            job_title_element = job_element.find_element(By.XPATH, './/a[@data-at="job-item-title"]')
            job_title = job_title_element.text
            
            if exclude_words and any(word.lower() in job_title.lower() for word in exclude_words):
                print(f"Job mit Titel '{job_title}' enthält Ausschlusswörter und wird ignoriert.")
                continue
            
            company_name_element = job_element.find_element(By.XPATH, './/span[@data-at="job-item-company-name"]')
            company_name = company_name_element.text
            location = job_element.find_element(By.XPATH, './/span[@data-at="job-item-location"]').text

            if target_location and target_location.lower() not in location.lower():
                print(f"Ignoriere Job in {location} (außerhalb des Zielorts).")
                continue  
            
            job_link = job_element.find_element(By.XPATH, './/a[@data-testid="job-item-title"]').get_attribute("href")
            
            job_identifier = (job_title, company_name)  
            
            if job_identifier not in seen_jobs: 
                seen_jobs.add(job_identifier)
                job_info.append({
                    "title": job_title,
                    "company": company_name,
                    "location": location,
                    "link": job_link,
                    "date": job_element.find_element(By.XPATH, './/span[@data-at="job-item-timeago"]').text,  
                    "source": "StepStone"
                })
        except Exception as e:
            print(f"Fehler beim Extrahieren eines Jobs von StepStone: {e}")
    
    return job_info


def job_search(job_title, location, radius, job_type, date_range, exclude_words):
    """Durchsucht Indeed nach den ersten drei Seiten."""
    driver = initialize_driver()
    job_info = []

    job_type_param = f"jt({job_type})" if job_type else ""
    date_range_param = date_range if date_range else "7"
    
    for page in range(0, 20, 10):  
        url = f'https://de.indeed.com/jobs?q={job_title}&l={location}&radius={radius}&sc={job_type_param}&fromage={date_range_param}&start={page}'
        
        print(f"Zugriff auf URL: {url}")
        driver.get(url)
        close_popup(driver)
        job_info.extend(extract_job_information_indeed(driver, exclude_words))
        
        time.sleep(5)

    driver.quit()
    return job_info


def stepstone_search(job_title, location, radius, job_type, date_range, exclude_words):
    """Durchsucht StepStone nach den ersten drei Seiten unter Berücksichtigung von job_type und date_range."""
    driver = initialize_driver()
    job_info = []
    
    base_url = "https://www.stepstone.de/jobs/"
    job_title = job_title.replace(" ", "-").lower()
    location = location.replace(" ", "-").lower()
    
    if job_type == "fulltime":
        job_type_param = "vollzeit"
    elif job_type == "parttime":
        job_type_param = "teilzeit"
    else:
        job_type_param = ""
    
    date_range_param = f"&ag=age_{date_range}" if date_range else "&ag=age_7"

    for page in range(1, 2):
        url = f"{base_url}{job_type_param}/{job_title}/in-{location}?radius={radius}&{date_range_param}&rsearch=1&page={page}"
        print(f"Zugriff auf URL: {url}")
        time.sleep(5) 
        driver.get(url)
        
        time.sleep(5)
        close_popup(driver)
        job_info.extend(extract_job_information_stepstone(driver, exclude_words, location))
        
        time.sleep(5)

    driver.quit()
    return job_info


def parse_date_string(date_string):
    """Parst einen Datums-String und gibt die Anzahl der Tage seit dem Datum zurück."""
    
    date_string = re.sub(r'Posted|geschaltet', '', date_string).strip()

    print(f"Bereinigter Datumsstring: {date_string}")

    patterns = {
        r'vor (\d+) Tag': lambda x: int(x[0]),
        r'vor (\d+) Tagen': lambda x: int(x[0]),
        r'vor (\d+) Woche': lambda x: int(x[0]) * 7,
        r'vor (\d+) Wochen': lambda x: int(x[0]) * 7,
        r'vor (\d+) Monat': lambda x: int(x[0]) * 30,
        r'vor (\d+) Monaten': lambda x: int(x[0]) * 30,
        r'vor (\d+) Jahr': lambda x: int(x[0]) * 365,
        r'vor (\d+) Jahren': lambda x: int(x[0]) * 365,
        r'vor einen Tag': lambda x: 1, 
        r'vor einem Monat': lambda x: 30,  
        r'vor einem Jahr': lambda x: 365, 
        r'Gerade': lambda x: 0,  
        r'vor (\d+) Stunden': lambda x: int(x[0]) / 24, 
        r'Gestern': lambda x: 1,
    }

    for pattern, func in patterns.items():
        match = re.match(pattern, date_string, re.IGNORECASE)  
        if match:
            return func(match.groups())

    return 1000

def remove_duplicates(jobs):
    """Entfernt Duplikate aus der Liste von Jobs basierend auf Titel, Firma und Standort."""
    seen_jobs = set()
    unique_jobs = []
    
    for job in jobs:
        job_identifier = (job['title'], job['company'], job['location'])
        if job_identifier not in seen_jobs:
            seen_jobs.add(job_identifier)
            unique_jobs.append(job)
    
    return unique_jobs

def aggregate_job_search(job_title, location, radius, job_type, date_range, sort_by, exclude_words):
    exclude_words = exclude_words or []
    
    indeed_jobs = job_search(job_title, location, radius, job_type, date_range, exclude_words)
    stepstone_jobs = stepstone_search(job_title, location, radius, job_type, date_range, exclude_words)
             
    print("Indeed Jobs (before processing):", indeed_jobs)
    print("StepStone Jobs (before processing):", stepstone_jobs)
    
    for job in indeed_jobs:
        original_date = job.get('date', '')
        try:
            job['days'] = parse_date_string(original_date)
        except Exception as e:
            print(f"Error parsing date for Indeed job: {e}")
            job['days'] = float('inf')
        print(f"Indeed Job: {job}")  
        
    for job in stepstone_jobs:
        original_date = job.get('date', '')
        try:
            job['days'] = parse_date_string(original_date)
        except Exception as e:
            print(f"Error parsing date for Stepstone job: {e}")
            job['days'] = float('inf')
        print(f"Stepstone Job: {job}")    

    if sort_by == "date":
        print("Sorting Indeed jobs by date...")
        indeed_jobs.sort(key=lambda x: x.get('days', float('inf')))  
        for job in indeed_jobs:
            print(f"Indeed Job - Title: {job['title']}, Days: {job['days']}")  

        print("Sorting Stepstone jobs by date...")
        stepstone_jobs.sort(key=lambda x: x.get('days', float('inf')))
        for job in stepstone_jobs:
            print(f"Stepstone Job - Title: {job['title']}, Days: {job['days']}") 


    all_jobs_list = remove_duplicates(indeed_jobs) + remove_duplicates(stepstone_jobs)

    total_jobs = len(all_jobs_list)
    today_jobs = len([job for job in all_jobs_list if job.get('days', 0) <= 1])
    last_7_days_jobs = len([job for job in all_jobs_list if job.get('days', 0) <= 8])

    print("All Jobs (after processing):", all_jobs_list)


    all_jobs = {
        "total_jobs": total_jobs,
        "today_jobs": today_jobs,
        "last_7_days_jobs": last_7_days_jobs,
        "jobs": all_jobs_list
    }

    return all_jobs


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    job_title = request.form['job_title']
    location = request.form['location']
    radius = request.form['radius']
    job_type = request.form['job_type']
    date_range = request.form['date_range']
    sort_by = request.form['sort_by']  

    exclude_words = request.form.get('exclude_words', '').split(',')

    job_info = aggregate_job_search(job_title, location, radius, job_type, date_range, sort_by, exclude_words)
    
    return jsonify(job_info)


if __name__ == "__main__":
    app.run(debug=True, port=5005)


