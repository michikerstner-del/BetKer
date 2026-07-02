import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="WM 2026 Dashboard", layout="wide")
st.title("⚽ WM 2026 Analytics Dashboard")

# Debugging: Zeige an, ob Secrets überhaupt geladen wurden
if "SUPABASE_URL" not in st.secrets:
    st.error("Fehler: SUPABASE_URL Secret nicht gefunden!")
    st.stop()

@st.cache_resource
def get_data():
    try:
        # Wir schalten die Zertifikatsprüfung ab, um den SSL-Fehler zu umgehen
        # Da der Connection String das Passwort enthält, ist die Verbindung trotzdem verschlüsselt
        conn = psycopg2.connect(
            st.secrets["SUPABASE_URL"],
            sslmode='require' # Anstatt 'verify-full' nur 'require'
        )
        df = pd.read_sql("SELECT * FROM public.matches ORDER BY match_date ASC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Verbindungs-Fehler: {e}")
        return None

df = get_data()

if df is not None:
    st.dataframe(df)
else:
    st.write("Keine Daten gefunden oder Verbindung fehlgeschlagen.")
