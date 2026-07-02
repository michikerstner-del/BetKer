import os
import requests
import psycopg2

def run_ingestion():
    # Verbindung
    conn = psycopg2.connect(os.environ['SUPABASE_URL'])
    cur = conn.cursor()

    # Beispiel: API-Football abfragen
    url = "https://v3.football.api-sports.io/fixtures?league=1&season=2026"
    headers = {'x-rapidapi-key': os.environ['API_FOOTBALL_KEY'], 'x-rapidapi-host': 'v3.football.api-sports.io'}
    response = requests.get(url, headers=headers).json()

    # Daten einfügen
    for match in response['response'][:5]: # Wir nehmen nur die ersten 5 als Test
        cur.execute(
            "INSERT INTO matches (match_date, home_team, away_team, league_name, api_source) VALUES (%s, %s, %s, %s, %s)",
            (match['fixture']['date'], match['teams']['home']['name'], match['teams']['away']['name'], "WM 2026", "API-Football")
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Daten erfolgreich in die Tabelle geschrieben!")

if __name__ == "__main__":
    run_ingestion()
