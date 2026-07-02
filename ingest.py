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
        
        count = 0
        for match in data.get('matches', []):
            # Wir speichern das Spiel primär. 
            # Wir lassen die IDs hier erst einmal WEG, um den Fehler zu isolieren.
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, external_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE 
                SET match_date = EXCLUDED.match_date,
                    external_data = EXCLUDED.external_data;
            """, (str(match['id']), match['utcDate'], json.dumps(match)))
            count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {count} Spiele ohne ID-Mapping gespeichert."
    except Exception as e:
        return f"Fehler: {str(e)}"
