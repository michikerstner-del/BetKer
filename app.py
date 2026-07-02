import streamlit as st
import psycopg2
import pandas as pd
import ingest # Dein Ingest-Modul

st.set_page_config(page_title="WM 2026 Dashboard", layout="wide")
st.title("⚽ WM 2026 Analytics Dashboard")

# 1. Sicherstellen, dass Secrets geladen sind
if "SUPABASE_URL" not in st.secrets:
    st.error("Fehler: SUPABASE_URL Secret nicht gefunden!")
    st.stop()

# 2. Daten laden mit LEFT JOIN
@st.cache_resource
def get_data():
    try:
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        # LEFT JOIN stellt sicher, dass wir alle Spiele sehen, auch wenn Teams noch nicht verknüpft sind
        query = """
        SELECT 
            m.match_date, 
            COALESCE(t1.name, 'Noch offen') AS home_team, 
            COALESCE(t2.name, 'Noch offen') AS away_team, 
            COALESCE(s.name, 'Noch offen') AS stadium
        FROM public.matches m
        LEFT JOIN public.teams t1 ON m.home_team_id = t1.id
        LEFT JOIN public.teams t2 ON m.away_team_id = t2.id
        LEFT JOIN public.stadiums s ON m.stadium_id = s.id
        ORDER BY m.match_date ASC;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Datenbankfehler: {e}")
        return None

# 3. UI-Anzeige
df = get_data()

if df is not None and not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Noch keine Daten in der Datenbank. Nutze die Sidebar, um die API zu synchronisieren.")

# 4. Sidebar Funktionen
st.sidebar.header("Admin")
if st.sidebar.button("API-Daten synchronisieren"):
    with st.spinner('Synchronisiere Daten mit der API...'):
        try:
            meldung = ingest.fetch_and_save_data()
            st.sidebar.success(meldung)
            st.rerun() # Aktualisiert die App, um neue Daten zu laden
        except Exception as e:
            st.sidebar.error(f"Fehler: {e}")

if st.sidebar.button("Datenbank-Test: Team hinzufügen"):
    try:
        conn = psycopg2.connect(st.secrets["SUPABASE_URL"], sslmode='require')
        cur = conn.cursor()
        cur.execute("INSERT INTO public.teams (name) VALUES ('Deutschland') ON CONFLICT DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
        st.sidebar.success("Test-Team 'Deutschland' hinzugefügt.")
    except Exception as e:
        st.sidebar.error(f"Fehler: {e}")
