import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="WM 2026 Dashboard", layout="wide")
st.title("⚽ WM 2026 Analytics Dashboard")

# Verbindung zur Supabase-DB (benutzt den Connection String aus den Secrets)
# Hinweis: Du musst SUPABASE_URL auch als Secret für Streamlit hinterlegen, 
# wenn du es später auf der Streamlit Cloud hostest.
@st.cache_resource
def get_data():
    engine = create_engine(st.secrets["SUPABASE_URL"])
    return pd.read_sql("SELECT * FROM matches ORDER BY match_date ASC", engine)

df = get_data()

st.subheader("Spielplan & Daten")
st.dataframe(df)

if st.button('Daten aktualisieren'):
    st.rerun()
