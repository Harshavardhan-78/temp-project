import streamlit as st
from utils.db_handler import get_db

st.title("🏠 Smart Canteen Management System")

db = get_db()

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
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")

            if st.form_submit_button("Register"):
                if db.users.find_one({"username": new_username}):
                    st.warning("Username already exists")
                else:
                    db.users.insert_one({
                        "username": new_username,
                        "password": new_password
                    })
                    st.success("Registration successful!")

else:
    st.success(f"Welcome {st.session_state.owner_id} 👋")

    if st.button("Logout"):
        del st.session_state["owner_id"]
        st.rerun()
