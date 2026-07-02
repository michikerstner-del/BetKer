import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="WM 2026 Dashboard", layout="wide")
st.title("⚽ WM 2026 Analytics Dashboard")

@st.cache_resource
def get_data():
    # Aufbau der Verbindung aus den Einzelteilen
    conn_str = f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASS']}@{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"
    conn = psycopg2.connect(conn_str)
    query = "SELECT * FROM matches ORDER BY match_date ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    df = get_data()
    st.dataframe(df)
except Exception as e:
    st.error(f"Verbindungsfehler: {e}")
    st.write("Bitte prüfe den Connection String in den Streamlit-Secrets.")
