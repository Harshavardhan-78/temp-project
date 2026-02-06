import streamlit as st

st.set_page_config(page_title="Smart Canteen", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- PAGE DEFINITIONS ---
dashboard = st.Page("pages/Dashboard.py", title="Dashboard", icon="📊")
predictor = st.Page("pages/Predictor.py", title="Predictor", icon="🔮")
home = st.Page("pages/home.py", title="Home", icon="🏠")
data_entry = st.Page("pages/data_entry.py", title="Data Entry", icon="📝")

# --- NAVIGATION CONTROL ---
if st.session_state.logged_in:
    # Sidebar shows everything once logged in
    pg = st.navigation({
        "Operations": [dashboard, predictor, data_entry],
        "Account": [home]
    })
else:
    # Sidebar ONLY shows Home until login
    pg = st.navigation([home])


pg.run()
