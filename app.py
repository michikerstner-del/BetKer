import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="WM 2026 Dashboard", layout="wide")
st.title("⚽ WM 2026 Analytics Dashboard")

if "SUPABASE_URL" not in st.secrets:
    st.error("Fehler: SUPABASE_URL Secret nicht gefunden!")
    st.stop()

@st.cache_resource
def get_data():
    try:
        conn = psycopg2.connect(
            st.secrets["SUPABASE_URL"],
            sslmode='require'
        )
        # Hier ist der neue JOIN-Query, der alle Tabellen verbindet
        query = """
        SELECT 
            m.match_date, 
            t1.name AS home_team, 
            t2.name AS away_team, 
            s.name AS stadium
        FROM public.matches m
        JOIN public.teams t1 ON m.home_team_id = t1.id
        JOIN public.teams t2 ON m.away_team_id = t2.id
        JOIN public.stadiums s ON m.stadium_id = s.id
        ORDER BY m.match_date ASC;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Datenbankfehler (JOIN): {e}")
        return None

df = get_data()

if df is not None and not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("Noch keine verknüpften Daten gefunden. Stelle sicher, dass Teams und Stadien in der DB angelegt und mit einem Spiel verknüpft sind.")
