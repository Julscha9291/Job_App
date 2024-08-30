import pandas as pd
import requests
import re
from time import sleep

# Erstellen Sie einen leeren DataFrame für die Jobs und Standorte
columns = ['title', 'company', 'location', 'latitude', 'longitude']
jobs_df = pd.DataFrame(columns=columns)

# Zwischenspeicher für die Geokodierung
geocode_cache = {}

def clean_location(location):
    """Bereinigt den Standort von PLZ und zusätzlichen Informationen."""
    # Entfernt PLZ (z.B. '44227 Dortmund' -> 'Dortmund')
    location = re.sub(r'\b\d{5}\b', '', location)
    # Entfernt alles nach einem Klammer auf (z.B. 'Wetter (Ruhr)' -> 'Wetter')
    location = re.sub(r'\s*\(.*?\)', '', location)
    # Entfernt führende und nachfolgende Leerzeichen
    location = location.strip()
    return location

def geocode_location(location):
    """Konvertiert einen Standort in geografische Koordinaten (Latitude, Longitude)."""
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        lat, lon = response.json()[0]['lat'], response.json()[0]['lon']
        print(f"Geokodierung für '{location}': Latitude={lat}, Longitude={lon}")  # Debug-Ausgabe
        return lat, lon
    print(f"Geokodierung fehlgeschlagen für '{location}'")  # Debug-Ausgabe bei Fehler
    return None, None

def add_job_to_dataframe(job_info):
    global jobs_df
    for job in job_info:
        sleep(2)  # Wartezeit zwischen den Anfragen
        locations = job['location'].split(', ')  # Annahme: Mehrere Standorte sind durch Kommas getrennt
        for location in locations:
            lat, lon = geocode_location(location)
            if lat and lon:
                job_entry = {
                    'title': job['title'],
                    'company': job['company'],
                    'location': location,
                    'latitude': lat,
                    'longitude': lon
                }
                jobs_df = pd.concat([jobs_df, pd.DataFrame([job_entry])], ignore_index=True)

# Beispiel-Nutzung
job_info = [
    {'title': 'Software Engineer', 'company': 'Tech Co.', 'location': 'Dortmund'},
    {'title': 'Data Scientist', 'company': 'Data Inc.', 'location': '58300 Wetter (Ruhr), Munich'},
    {'title': 'Web Developer', 'company': 'Web Solutions', 'location': 'Hamburg'}
]

add_job_to_dataframe(job_info)

print(jobs_df)
