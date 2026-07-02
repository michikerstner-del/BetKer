import requests
import psycopg2
import streamlit as st
import json

def fetch_and_save_data():
    api_key = st.secrets["FOOTBALL_DATA_API_KEY"] # Stelle sicher, dass dieser Key in den Secrets ist!
    headers = {'X-Auth-Token': api_key}
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        for match in data['matches']:
            # Wir speichern die API-Daten in das JSONB-Feld 'external_data'
            # 'api_id' ist der eindeutige Identifier
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, external_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE 
                SET external_data = EXCLUDED.external_data;
            """, (str(match['id']), match['utcDate'], json.dumps(match)))
        
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {len(data['matches'])} Spiele verarbeitet."
    except Exception as e:
        return f"Fehler: {e}"

# Ruf die Funktion auf
if __name__ == "__main__":
    print(fetch_and_save_data())
