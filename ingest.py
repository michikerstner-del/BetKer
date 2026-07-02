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
        if response.status_code != 200:
            return f"API-Fehler: {response.status_code} - {response.text}"
            
        data = response.json()
        matches = data.get('matches', [])
        
        if not matches:
            return "API-Sync: Keine Spiele gefunden (vielleicht falscher Wettbewerbs-Code?)"

        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        count = 0
        for match in matches:
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, external_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE 
                SET external_data = EXCLUDED.external_data;
            """, (str(match['id']), match['utcDate'], json.dumps(match)))
            count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {count} Spiele in die Datenbank geschrieben."
    
    except Exception as e:
        return f"Fehler bei DB-Verbindung: {str(e)}"
