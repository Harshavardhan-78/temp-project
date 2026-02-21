import streamlit as st
from utils.db_handler import get_db, fetch_sales_data
import base64

# ---------------------------------------------------
# BACKGROUND IMAGE
# ---------------------------------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()

    st.markdown(f"""
    <style>

    /* Full page background */
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Dark glass container */
    .block-container {{
        background: rgba(0, 0, 0, 0.55);
        padding: 2rem;
        border-radius: 20px;
    }}

    /* All normal text white */
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# CALL BACKGROUND
add_bg_from_local("assets/canteen_bg2.png")

st.markdown("""
<style>

/* Hide Streamlit header (white bar) */
header[data-testid="stHeader"] {
    display: none;
}

/* Hide hamburger menu (⋮) */
#MainMenu {
    visibility: hidden;
}

/* Remove top spacing that header leaves */
.block-container {
    padding-top: 0rem !important;
}

/* Remove footer */
footer {
    visibility: hidden;
}

/* Remove "Made with Streamlit" */
[data-testid="stToolbar"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# ONLY LOGIN + LOGOUT BUTTON TEXT BLACK
# ---------------------------------------------------
st.markdown("""
<style>

/* ---------- LABELS (Username / Password) ---------- */
label, .stTextInput label, .stPasswordInput label {
    color: white !important;
    font-weight: 500;
}

/* ---------- INPUT TEXT ---------- */
input {
    color: black !important;
    background-color: rgba(255,255,255,0.92) !important;
    border-radius: 12px !important;
}

/* ---------- TABS (Login | Register) ---------- */
button[data-baseweb="tab"] {
    color: white !important;
    font-weight: 600;
}

/* Active tab underline */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #4ade80 !important;   /* green highlight */
    border-bottom: 3px solid #4ade80 !important;
}

/* ---------- LOGIN BUTTON ONLY ---------- */
.stButton > button {
    background-color: #16a34a !important;   /* green button */
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
}

/* Hover */
.stButton > button:hover {
    background-color: #15803d !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# PAGE CONTENT
# ---------------------------------------------------

st.title("Smart Canteen Management Decision Support System")

st.markdown("""
### Intelligent Demand Forecasting & Analytics Platform  
Designed to help canteen managers make data-driven operational decisions.
""")

st.markdown("---")

st.markdown("## 🚀 What This System Does")

st.markdown("""
- 📊 Analyze historical sales patterns  
- 🔮 Predict next-day demand using advanced ML  
- 📈 Monitor item-level performance  
- 🏆 Identify high-demand items  
- 📉 Reduce overproduction and stock-outs  
- 🧠 Provide contextual reasoning insights  
""")

st.markdown("---")

# ---------------------------------------------------
# DATABASE
# ---------------------------------------------------
db = get_db()

# ---------------- CHECK IF LOGGED IN ----------------
if "owner_id" in st.session_state:

    df = fetch_sales_data(st.session_state["owner_id"])

    if df.empty:
        st.info("""
👋 Welcome! To start using CMDSS:

1️⃣ Go to Data Entry  
2️⃣ Upload at least 7 days of data  
3️⃣ Visit Dashboard for insights  
4️⃣ Use Predictor for forecasting  
""")

# ---------------- LOGIN / REGISTER ----------------
if "owner_id" not in st.session_state:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            user = db.users.find_one({
                "username": username,
                "password": password
            })

            if not user:
                st.error("Invalid credentials")
            else:
                if not user.get("approved", False):
                    st.error("Your account is awaiting admin approval.")
                else:
                    st.session_state.owner_id = username
                    st.session_state.role = user.get("role", "owner")
                    st.success("Login successful!")
                    st.rerun()

    with tab2:
        with st.form("register_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Register")

            if submitted:
                if not username.strip():
                    st.error("Username cannot be empty.")

                elif not password.strip():
                    st.error("Password cannot be empty.")

                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")

                else:
                    existing_user = db.users.find_one({"username": username})

                    if existing_user:
                        st.error("Username already exists.")
                    else:
                        db.users.insert_one({
                            "username": username,
                            "password": password,
                            "role": "owner",
                            "approved": False
                        })

                        st.success("Registration successful! Awaiting admin approval.")

# ---------------- LOGGED IN VIEW ----------------
else:
    st.success(f"Welcome {st.session_state.owner_id} 👋")

    if st.button("Logout"):
        del st.session_state["owner_id"]
        st.rerun()