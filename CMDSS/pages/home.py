import streamlit as st
from utils.db_handler import get_db, fetch_sales_data

st.set_page_config(layout="wide")

st.title("🍽 Smart Canteen Management Decision Support System")

st.markdown("""
### Intelligent Demand Forecasting & Analytics Platform
Designed to help canteen managers make data-driven operational decisions.
""")

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🚀 What This System Does")

    st.markdown("""
    - 📊 Analyze historical sales patterns  
    - 🔮 Predict next-day demand using advanced ML  
    - 📈 Monitor item-level performance  
    - 🏆 Identify high-demand items  
    - 📉 Reduce overproduction and stock-outs  
    - 🧠 Provide contextual reasoning insights  
    """)

with col2:
    st.info("""
    ### 🛠 Core Technologies
    - Random Forest
    - Gradient Boosting
    - Time-Series Forecasting
    - MongoDB Atlas
    - Streamlit
    - Plotly Visualization
    """)

st.markdown("---")

st.subheader("📌 How It Works")

col3, col4, col5 = st.columns(3)

with col3:
    st.success("1️⃣ Data Collection")
    st.write("Daily sales, weather, exam schedule and context are recorded.")

with col4:
    st.success("2️⃣ ML Forecasting")
    st.write("Advanced ensemble time-aware model predicts tomorrow's demand.")

with col5:
    st.success("3️⃣ Decision Support")
    st.write("System provides insights and recommendations for preparation planning.")

st.markdown("---")

st.markdown("### 🎯 Project Objective")

st.write("""
The primary objective of CMDSS is to provide intelligent operational support 
for canteen managers through accurate short-term demand forecasting and 
clear analytics visualization.
""")

st.markdown("---")

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
                # Check approval status
                if not user.get("approved", False):
                    st.error("Your account is awaiting admin approval.")
                
                else:
                    # Set session variables
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
