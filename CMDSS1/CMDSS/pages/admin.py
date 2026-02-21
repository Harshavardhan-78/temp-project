import streamlit as st
import pandas as pd
from utils.db_handler import get_db

st.title("👑 Admin Panel")

if "role" not in st.session_state or st.session_state["role"] != "admin":
    st.error("Access Denied")
    st.stop()

db = get_db()

# -------- System Stats --------
st.subheader("📊 System Overview")

total_users = db.users.count_documents({})
total_sales = db.sales.count_documents({})

col1, col2 = st.columns(2)
col1.metric("Total Users", total_users)
col2.metric("Total Sales Records", total_sales)

st.markdown("---")

# -------- Pending Approvals --------
st.subheader("⏳ Pending User Approvals")

pending_users = list(db.users.find({"approved": False}))

if pending_users:
    for user in pending_users:
        col1, col2 = st.columns([3,1])
        col1.write(user["username"])
        if col2.button(f"Approve {user['username']}"):
            db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"approved": True}}
            )
            st.success("User approved")
            st.rerun()
else:
    st.info("No pending approvals")

st.markdown("---")

# -------- All Users --------
st.subheader("👥 All Users")

users = list(db.users.find({}, {"_id": 0, "password": 0}))
if users:
    st.dataframe(pd.DataFrame(users), use_container_width=True)
