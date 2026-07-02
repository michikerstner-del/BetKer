import requests
import psycopg2
import streamlit as st
import json

def fetch_and_save_data():
    api_key = st.secrets["FOOTBALL_DATA_API_KEY"]
    headers = {'X-Auth-Token': api_key}
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        for match in data.get('matches', []):
            # Wir versuchen hier direkt den INSERT, ohne komplexe Funktionen
            # Wir nehmen nur die API-Daten
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, external_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE SET match_date = EXCLUDED.match_date;
            """, (str(match['id']), match['utcDate'], json.dumps(match)))
        
        conn.commit()
        cur.close()
        conn.close()
        return "Erfolg: 104 Spiele ohne IDs gespeichert."
    except Exception as e:
        return f"Fehler: {str(e)}"
