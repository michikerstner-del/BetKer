import os
import requests
import psycopg2

# 1. Verbindung zur Datenbank herstellen
def get_db_connection():
    return psycopg2.connect(os.environ['SUPABASE_URL'])

# 2. Daten von API-Football abrufen (Beispiel für Spielpläne)
def fetch_api_football():
    url = "https://v3.football.api-sports.io/fixtures?league=1&season=2026"
    headers = {'x-rapidapi-key': os.environ['API_FOOTBALL_KEY'], 'x-rapidapi-host': 'v3.football.api-sports.io'}
    response = requests.get(url, headers=headers)
    return response.json().get('response', [])

# 3. Haupt-Logik
def run_ingestion():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Beispiel: Daten abrufen
    matches = fetch_api_football()
    
    # Beispiel: Daten in die DB schreiben
    for match in matches:
        date = match['fixture']['date']
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        
        cur.execute("INSERT INTO matches (match_date) VALUES (%s)", (date,))
        
    conn.commit()
    cur.close()
    conn.close()
    print("Daten erfolgreich verarbeitet!")

if __name__ == "__main__":
    run_ingestion()
