import requests
import psycopg2
import streamlit as st
import json

def get_or_create_id(cur, table, name):
    if not name: return None
    # Team/Stadion suchen
    cur.execute(f"SELECT id FROM public.{table} WHERE name = %s", (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    # Falls nicht gefunden, neu anlegen
    cur.execute(f"INSERT INTO public.{table} (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]

def fetch_and_save_data():
    api_key = st.secrets["FOOTBALL_DATA_API_KEY"]
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {'X-Auth-Token': api_key}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        count = 0
        for match in data.get('matches', []):
            h_name = match.get('homeTeam', {}).get('name')
            a_name = match.get('awayTeam', {}).get('name')
            s_name = match.get('venue')
            
            # IDs holen oder erstellen
            h_id = get_or_create_id(cur, "teams", h_name)
            a_id = get_or_create_id(cur, "teams", a_name)
            s_id = get_or_create_id(cur, "stadiums", s_name)
            
            # Upsert mit IDs
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, home_team_id, away_team_id, stadium_id, external_data)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE 
                SET home_team_id = EXCLUDED.home_team_id,
                    away_team_id = EXCLUDED.away_team_id,
                    stadium_id = EXCLUDED.stadium_id;
            """, (str(match['id']), match['utcDate'], h_id, a_id, s_id, json.dumps(match)))
            count += 1
            
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {count} Spiele inkl. Mapping verarbeitet."
    except Exception as e:
        return f"Fehler: {str(e)}"
