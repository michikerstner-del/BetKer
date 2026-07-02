import streamlit as st
import psycopg2
import pandas as pd
import socket

@st.cache_resource
def get_data():
    # Wir holen uns die IP-Adresse direkt per Code in der Cloud
    # Das umgeht den DNS-Fehler, falls Streamlit Probleme hat
    host = "db.dmqsmadpsbjijuqysmie.supabase.co"
    ip = socket.gethostbyname(host)
    
    conn = psycopg2.connect(
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        host=ip, # Wir nutzen hier die IP, die der Server selbst findet
        port=st.secrets["DB_PORT"],
        sslmode='require' # Wichtig für die Sicherheit
    )
    df = pd.read_sql("SELECT * FROM matches ORDER BY match_date ASC", conn)
    conn.close()
    return df
