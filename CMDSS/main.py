import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Smart Canteen CMDSS",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# ADAPTIVE THEME CSS (Light + Dark Compatible)
# ---------------------------------------------------
st.markdown("""
<style>

/* ===== Headings ===== */
h1, h2, h3 {
    font-weight: 600;
}

/* ===== Metric Cards (Adaptive) ===== */
div[data-testid="stMetric"] {
    padding: 20px;
    border-radius: 16px;
    transition: 0.3s ease;
}

/* Light Mode */
html[data-theme="light"] div[data-testid="stMetric"] {
    background-color: #ffffff;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* Dark Mode */
html[data-theme="dark"] div[data-testid="stMetric"] {
    background-color: #1e293b;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

/* ===== Buttons ===== */
.stButton>button {
    border-radius: 10px;
    padding: 0.5em 1.5em;
    font-weight: 500;
    transition: 0.3s ease;
}

/* Light Mode Button */
html[data-theme="light"] .stButton>button {
    background-color: #2563eb;
    color: white;
}

/* Dark Mode Button */
html[data-theme="dark"] .stButton>button {
    background-color: #3b82f6;
    color: white;
}

/* Hover Animation */
.stButton>button:hover {
    transform: translateY(-2px);
}

/* Selectbox */
div[data-baseweb="select"] > div {
    border-radius: 8px !important;
}

/* Spacing */
.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# PAGE NAVIGATION
# ---------------------------------------------------
dashboard = st.Page("pages/Dashboard.py", title="Dashboard", icon="📊")
predictor = st.Page("pages/Predictor.py", title="Predictor", icon="🔮")
home = st.Page("pages/home.py", title="Home", icon="🏠")
data_entry = st.Page("pages/data_entry.py", title="Data Entry", icon="📥")
admin = st.Page("pages/admin.py", title="Admin", icon="👑")

if "owner_id" in st.session_state:

    role = st.session_state.get("role", "owner")

    if role == "admin":
        pg = st.navigation({
            "👑 Admin": [admin],
            
            "👤 Account": [home]
        })
    else:
        pg = st.navigation({
            "📊 Operations": [dashboard, predictor, data_entry],
            "👤 Account": [home]
        })
else:
    pg = st.navigation([home])

pg.run()



