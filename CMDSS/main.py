import streamlit as st

st.set_page_config(page_title="Smart Canteen", layout="wide")

dashboard = st.Page("pages/Dashboard.py", title="Dashboard", icon="📊")
predictor = st.Page("pages/Predictor.py", title="Predictor", icon="🔮")
home = st.Page("pages/home.py", title="Home", icon="🏠")
data_entry = st.Page("pages/data_entry.py", title="Data Entry", icon="📥")

if "owner_id" in st.session_state:
    pg = st.navigation({
        "Operations": [dashboard, predictor, data_entry],
        "Account": [home]
    })
else:
    pg = st.navigation([home])

pg.run()
