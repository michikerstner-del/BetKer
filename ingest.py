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
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        # 1. Wir legen erst manuell ein Test-Team an, um zu sehen, ob das Skript schreiben kann
        cur.execute("INSERT INTO public.teams (name) VALUES ('TestTeam') ON CONFLICT DO NOTHING;")
        conn.commit()
        
        count = 0
        for match in data.get('matches', []):
            # Wir schreiben das Spiel in die DB
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, external_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE SET match_date = EXCLUDED.match_date;
            """, (str(match['id']), match['utcDate'], json.dumps(match)))
            count += 1
            
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {count} Spiele gespeichert. Prüfe jetzt, ob 'TestTeam' in der Tabelle 'teams' existiert."
    except Exception as e:
        return f"Fehler: {str(e)}"
