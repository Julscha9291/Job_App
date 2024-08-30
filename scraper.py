from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def initialize_driver():
    """Initialisiert den WebDriver mit den angegebenen Optionen."""
    options = webdriver.ChromeOptions()
    options.headless = True  # Öffnet den Browser nicht sichtbar für den Benutzer
    return webdriver.Chrome(options=options)

def close_popup(driver):
    """Versucht, ein Popup-Fenster zu schließen, falls vorhanden."""
    try:
        popup = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mosaic-desktopserpjapopup"]/div[1]/button')))
        popup.click()
        print("Popup geschlossen.")
    except:
        print("Kein Popup gefunden.")

def capture_cookies(driver):
    """Erfasst und speichert die Cookies des WebDriver."""
    return driver.get_cookies()


def extract_job_information(driver, job_type):
    """Extrahiert die Jobtitel, Unternehmen, Standorte und Links zu den Stellen."""
    wait = WebDriverWait(driver, 10)
    job_elements = driver.find_elements(By.XPATH, '//div[@class="job_seen_beacon"]')
    job_info = []
    for job_element in job_elements:
        job_title_element = job_element.find_element(By.XPATH, './/span[@title]')
        job_title = job_title_element.get_attribute("title")
        if job_title:
            company_name_element = job_element.find_element(By.XPATH, './/span[@data-testid="company-name"]')
            company_name = company_name_element.text
            location_element = job_element.find_element(By.XPATH, './/div[@data-testid="text-location"]')
            location = location_element.text
            job_link_element = job_element.find_element(By.XPATH, './/a')
            job_link = job_link_element.get_attribute("href")
            if not any(keyword in job_title for keyword in ["Senior","Java", "C#",".NET","Hilfskraft" , "C/C++" , "Studierende", "Student", "student", "Ausbildung", "intern"]):
                job_info.append({"title": job_title, "company": company_name, "location": location, "link": job_link})
            print(job_title)
            print(company_name)
            print(location)
    print(job_info)
    return job_info


def job_search(jobs):   
    # Initialisiere den WebDriver
    driver = initialize_driver()
    
    job_info_combined = []
    
    for job in jobs:
        # Öffne die Seite, um Cookies zu erfassen und akzeptiere das Cookie-Banner
        url = f'https://de.indeed.com/jobs?q={job}&l=Dortmund&radius=25&fromage=7&vjk=7b6691336c6e7a77'
        driver.get(url)

        # Schließe das Popup, falls vorhanden
        close_popup(driver)

        # Erfasse und speichere die Cookies
        cookies = capture_cookies(driver)
        pickle.dump(cookies, open("cookies.pkl", "wb"))

        # Extrahiere die Jobinformationen (Titel und Links)
        job_info = extract_job_information(driver)
        job_info_combined.extend(job_info)
    
    # Beende den WebDriver
    driver.quit()    

    return job_info_combined

def send_email(job_info):
    # E-Mail Konfiguration
    sender_email = config.EMAIL
    receiver_email = config.EMPF
    password = config.PASSWORD
    subject = "Neue Jobangebote"

    # Jobs nach Typen trennen
    job_info_separated = {}
    for job in job_info:
        job_type = job["type"]
        if job_type not in job_info_separated:
            job_info_separated[job_type] = []
        job_info_separated[job_type].append(job)

    # E-Mail-Inhalt erstellen
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # HTML-Teil der E-Mail hinzufügen
    html = "<h1>Neue Jobangebote</h1>"
    for job_type, jobs in job_info_separated.items():
        html += f"<h2>{job_type}:</h2>"
        html += "<ul>"
        for job in jobs:
            html += f"<li><strong>{job['title']}</strong> bei {job['company']} in {job['location']}. Link: <a href='{job['link']}'>Hier klicken</a></li>"
        html += "</ul>"

    message.attach(MIMEText(html, "html"))

    # E-Mail senden
    try:
        with smtplib.SMTP_SSL('smtp.strato.de', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

def job_search(job_type, keyword):   
    """Durchsucht die Indeed-Jobseite nach einem bestimmten Jobtyp und Keyword."""
    # Initialisiere den WebDriver
    driver = initialize_driver()
    # Öffne die Seite, um Cookies zu erfassen und akzeptiere das Cookie-Banner
    url = f'https://de.indeed.com/jobs?q={keyword}&l=Dortmund&radius=25&fromage=7&vjk=7b6691336c6e7a77'
    driver.get(url)

    # Schließe das Popup, falls vorhanden
    close_popup(driver)

    # Erfasse und speichere die Cookies
    cookies = capture_cookies(driver)
    pickle.dump(cookies, open("cookies.pkl", "wb"))

    # Extrahiere die Jobinformationen (Titel, Unternehmen, Standorte und Links)
    job_info = extract_job_information(driver, job_type)
    for info in job_info:
        info["type"] = job_type
        print("Jobtyp:", job_type)
        print("Jobtitel:", info["title"])
        print("Company:", info["company"])
        print("Location:", info["location"])
        print("Link zur Stelle:", info["link"])

    # Beende den WebDriver
    driver.quit()
    
    return job_info

jobs_to_search = [
    {"type": "Softwareentwickler", "keyword": "Softwareentwickler"},
    {"type": "Python", "keyword": "Python"},
    {"type": "Data Engineer", "keyword": "Data Engineer"}
]

job_info = []
for job in jobs_to_search:
    job_info.extend(job_search(job["type"], job["keyword"]))

send_email(job_info)
