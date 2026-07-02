import streamlit as st
import psycopg2
import pandas as pd
import socket

@st.cache_resource
def get_data():
    # Wir isolieren den Hostnamen vom Connection-String
    host = "db.dmqsmadpsbjijuqysmie.supabase.co"
    
    # Der Trick: Wir erzwingen die IP-Auflösung manuell vor dem Verbindungsaufbau
    # Das umgeht die DNS-Probleme der Streamlit-Cloud-Infrastruktur
    try:
        ip = socket.gethostbyname(host)
    except:
        ip = host # Fallback auf den Hostnamen, falls das nicht klappt
        
    conn_str = f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASS']}@{ip}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"
    
    conn = psycopg2.connect(conn_str)
    df = pd.read_sql("SELECT * FROM matches ORDER BY match_date ASC", conn)
    conn.close()
    return df
