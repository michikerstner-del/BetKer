import requests
import psycopg2
import streamlit as st
import json

def get_or_create_team(cur, team_name):
    # Prüfen, ob Team bereits existiert
    cur.execute("SELECT id FROM public.teams WHERE name = %s", (team_name,))
    result = cur.fetchone()
    if result:
        return result[0]
    
    # Wenn nicht, neu anlegen
    cur.execute("INSERT INTO public.teams (name) VALUES (%s) RETURNING id", (team_name,))
    return cur.fetchone()[0]

def fetch_and_save_data():
    api_key = st.secrets["FOOTBALL_DATA_API_KEY"]
    headers = {'X-Auth-Token': api_key}
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"API-Fehler: {response.status_code}"
            
        data = response.json()
        matches = data.get('matches', [])
        
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        count = 0
        for match in matches:
            # Team-Namen aus API extrahieren
            home_name = match.get('homeTeam', {}).get('name', 'TBD')
            away_name = match.get('awayTeam', {}).get('name', 'TBD')
            
            # IDs holen/erstellen
            home_id = get_or_create_team(cur, home_name) if home_name != 'TBD' else None
            away_id = get_or_create_team(cur, away_name) if away_name != 'TBD' else None
            
            # Spiel speichern (mit verknüpften IDs)
            cur.execute("""
                INSERT INTO public."matches" (api_id, match_date, home_team_id, away_team_id, external_data)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE 
                SET home_team_id = EXCLUDED.home_team_id,
                    away_team_id = EXCLUDED.away_team_id,
                    external_data = EXCLUDED.external_data;
            """, (str(match['id']), match['utcDate'], home_id, away_id, json.dumps(match)))
            count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {count} Spiele inklusive Team-Verknüpfungen verarbeitet."
    
    except Exception as e:
        return f"Fehler: {str(e)}"
