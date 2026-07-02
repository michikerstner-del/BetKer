import requests
import psycopg2
import streamlit as st
import json

def get_or_create_id(cur, table, name):
    if not name or name == "TBD":
        return None
    # Suche nach dem Namen
    cur.execute(f"SELECT id FROM public.{table} WHERE name = %s", (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    # Falls nicht gefunden, lege es an
    cur.execute(f"INSERT INTO public.{table} (name) VALUES (%s) RETURNING id", (name,))
    new_id = cur.fetchone()[0]
    return new_id

def fetch_and_save_data():
    api_key = st.secrets["c90be3756d4c4577be201d8c38701831"]
    headers = {'X-Auth-Token': api_key}
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        
        count = 0
        for match in data.get('matches', []):
            home_name = match.get('homeTeam', {}).get('name')
            away_name = match.get('awayTeam', {}).get('name')
            stadium_name = match.get('venue')
            
            # IDs abrufen
            h_id = get_or_create_id(cur, "teams", home_name)
            a_id = get_or_create_id(cur, "teams", away_name)
            s_id = get_or_create_id(cur, "stadiums", stadium_name)
            
            # Daten in 'matches' einfügen
            cur.execute("""
                INSERT INTO public.matches (api_id, match_date, home_team_id, away_team_id, stadium_id, external_data)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE 
                SET home_team_id = EXCLUDED.home_team_id,
                    away_team_id = EXCLUDED.away_team_id,
                    stadium_id = EXCLUDED.stadium_id,
                    external_data = EXCLUDED.external_data;
            """, (str(match['id']), match['utcDate'], h_id, a_id, s_id, json.dumps(match)))
            count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        return f"Erfolg: {count} Spiele verarbeitet und IDs gemappt."
    except Exception as e:
        return f"Fehler: {str(e)}"
