import streamlit as st
from utils.db_handler import get_db, fetch_sales_data

st.title("🏠 Smart Canteen Management System")

st.markdown("""
### 🚀 About This Application

Smart Canteen Management System (CMDSS) is an intelligent decision-support
platform designed to help canteen owners:

• 📊 Analyze historical sales data  
• 🔮 Predict future item demand  
• 📅 Generate optimized weekly menu plans  
• 📈 Monitor business performance through dashboards  

The system uses data-driven insights to improve inventory planning,
reduce wastage, and increase profitability.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📊 **Interactive Dashboard**\n\nTrack sales trends and item performance.")

with col2:
    st.info("🔮 **Demand Prediction**\n\nForecast weekly demand based on conditions.")

with col3:
    st.info("📥 **Smart Data Entry**\n\nUpload CSV or maintain daily journal entries.")

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
            if user:
                st.session_state.owner_id = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

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
                            "password": password
                        })
                        st.success("Registration successful! Awaiting admin approval.")

# ---------------- LOGGED IN VIEW ----------------
else:
    st.success(f"Welcome {st.session_state.owner_id} 👋")

    if st.button("Logout"):
        del st.session_state["owner_id"]
        st.rerun()
