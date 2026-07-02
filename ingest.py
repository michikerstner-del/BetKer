import psycopg2
import streamlit as st

def test_verbindung():
    conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
    cur = conn.cursor()
    # Test-Eintrag
    cur.execute("INSERT INTO public.teams (name, group_name) VALUES ('Deutschland', 'A') ON CONFLICT DO NOTHING;")
    conn.commit()
    cur.close()
    conn.close()
    return "Erfolg: Deutschland ist in der DB!"

print(test_verbindung())
