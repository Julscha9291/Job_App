from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

def initialize_driver():
    """Initialisiert den WebDriver mit den angegebenen Optionen."""
    options = Options()
    options.headless = True  # Browser im Hintergrund ausführen
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def close_popup(driver):
    """Versucht, ein Popup-Fenster zu schließen, falls vorhanden."""
    try:
        popup = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mosaic-desktopserpjapopup"]/div[1]/button')))
        popup.click()
        print("Popup geschlossen.")
    except Exception as e:
        print(f"Kein Popup gefunden oder Fehler beim Schließen: {e}")

def capture_cookies(driver):
    """Erfasst und speichert die Cookies des WebDriver."""
    return driver.get_cookies()

def extract_job_information(driver):
    """Extrahiert die Jobtitel, Unternehmen, Standorte und Links zu den Stellen auf StepStone."""
    try:
        job_elements = driver.find_elements(By.XPATH, './/article[@data-at="job-item"]')
        if not job_elements:
            print("Keine Job-Elemente gefunden auf der Seite.")
        job_info = []
        for job_element in job_elements:
            try:
                job_elements = driver.find_elements(By.XPATH, '//div[@class="job-title"]/h2')
                job_title_element = job_element.find_element(By.XPATH, './/a[@data-at="job-item-title"]')
                job_title = job_title_element.text
                company_name_element = job_element.find_element(By.XPATH, './/span[@data-at="job-item-company-name"]')
                company_name = company_name_element.text
                location = job_element.find_element(By.XPATH, './/span[@data-at="job-item-location"]').text
                job_link = job_element.find_element(By.XPATH, './/a[@data-testid="job-item-title"]').get_attribute("href")
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
    except Exception as e:
        print(f"Fehler beim Zugriff auf die StepStone-Seite: {e}")
        return []
    
    
def job_search(job_title, location):
    """Durchsucht die StepStone-Seite nach dem angegebenen Jobtitel und Standort."""
    # Initialisiere den WebDriver
    driver = initialize_driver()
    # Öffne die Seite, um Cookies zu erfassen und akzeptiere das Cookie-Banner
    base_url = "https://www.stepstone.de/jobs/"
    job_title = job_title.replace(" ", "-").lower()
    location = location.replace(" ", "-").lower()
    url = f"{base_url}{job_title}/in-{location}?radius=30"
    print(f"Zugriff auf URL: {url}")
    driver.get(url)

    # Schließe das Popup, falls vorhanden
    close_popup(driver)

    # Erfasse und speichere die Cookies
    cookies = capture_cookies(driver)
    pickle.dump(cookies, open("cookies.pkl", "wb"))

    # Extrahiere die Jobinformationen (Titel, Unternehmen, Standorte und Links)
    job_info = extract_job_information(driver)
    for info in job_info:
        print("Jobtitel:", info["title"])
        print("Company:", info["company"])
        print("Location:", info["location"])
        print("Time:", info["date"])
        print("Link zur Stelle:", info["link"])

    # Beende den WebDriver
    driver.quit()
    
    return job_info

# Beispielaufruf der Funktion
if __name__ == "__main__":
    job_title = "Software Engineer"
    location = "Berlin"
    job_search(job_title, location)
