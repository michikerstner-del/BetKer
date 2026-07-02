import requests
import psycopg2
import streamlit as st
import json

def fetch_and_save_data():
    api_key = st.secrets["FOOTBALL_DATA_API_KEY"]
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {'X-Auth-Token': api_key}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Test: Drucke die ersten 3 Teamnamen in die Streamlit-Konsole
        matches = data.get('matches', [])
        print(f"DEBUG: Gefundene Spiele: {len(matches)}")
        if len(matches) > 0:
            print(f"DEBUG: Erstes Heimteam: {matches[0].get('homeTeam', {}).get('name')}")
            
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        # Nur ein Test-INSERT für ein einziges Team, um Rechte zu prüfen
        cur.execute("INSERT INTO public.teams (name) VALUES ('TestTeam-2') ON CONFLICT (name) DO NOTHING;")
        conn.commit()
        
        cur.close()
        conn.close()
        return f"Erfolg: {len(matches)} Spiele gefunden. Prüfe die Tabelle 'teams' auf 'TestTeam-2'."
    except Exception as e:
        return f"Fehler: {str(e)}"
