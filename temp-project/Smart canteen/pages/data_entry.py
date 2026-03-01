import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_handler import get_db

st.title("📥 Data Management")

if "owner_id" not in st.session_state:
    st.error("Please login first")
    st.stop()

db = get_db()

st.markdown("---")

mode = st.radio(
    "Select Data Entry Mode",
    ["📂 Upload Historical CSV", "📝 Daily Journal Entry"],
    horizontal=True
)

st.markdown("---")

# ======================================================
# MODE 1 — CSV UPLOAD
# ======================================================
if mode == "📂 Upload Historical CSV":

    st.subheader("📂 Upload Historical Sales Data")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        required_columns = [
            "item", "quantity", "weather",
            "exams", "region", "time_slot", "date"
        ]

        if not all(col in df.columns for col in required_columns):
            st.error("❌ CSV format incorrect. Missing required columns.")
            st.stop()

        st.success("✅ File validated successfully!")

        st.dataframe(df.head(), use_container_width=True)

        if st.button("🚀 Upload to Database"):

            df["owner_id"] = st.session_state["owner_id"]
            df["date"] = pd.to_datetime(df["date"])

            records = df.to_dict("records")
            db.sales.insert_many(records)

            st.success(f"🎉 {len(records)} records uploaded successfully!")

# ======================================================
# MODE 2 — DAILY JOURNAL ENTRY
# ======================================================
else:

    st.subheader("📝 Enter Daily Sales Journal")

    # Initialize session storage
    if "daily_items" not in st.session_state:
        st.session_state.daily_items = []

    # ---------------- Day Context ----------------
    st.markdown("### 📅 Day Details")

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date", value=datetime.today())
        weather = st.selectbox("Weather", ["Sunny", "Rainy", "Cloudy"])

    with col2:
        exams = st.selectbox("Exam Schedule", ["None", "Midterms", "Finals"])
        region = st.selectbox("Region", ["Urban", "Rural"])

    st.markdown("---")

    # ---------------- Add Items Form ----------------
    st.markdown("### ➕ Add Items")

    with st.form("add_item_form"):

        col1, col2 = st.columns(2)

        with col1:
            item = st.text_input("🍔 Item Name")
            quantity = st.number_input("📦 Quantity Sold", min_value=0)

        with col2:
            time_slot = st.selectbox(
                "⏰ Time Slot",
                ["Morning", "Afternoon", "Evening", "Night"]
            )

        add_item = st.form_submit_button("➕ Add Item")

        if add_item:
            if not item.strip():
                st.warning("Item name cannot be empty")
            else:
                st.session_state.daily_items.append({
                    "item": item,
                    "quantity": quantity,
                    "time_slot": time_slot
                })
                st.success(f"{item} added successfully!")

    # ---------------- Show Added Items ----------------
    if st.session_state.daily_items:

        st.markdown("### 📋 Items Added Today")

        preview_df = pd.DataFrame(st.session_state.daily_items)
        st.dataframe(preview_df, use_container_width=True)

        st.markdown("---")

        if st.button("✅ End Day & Save to Database"):

            for entry in st.session_state.daily_items:
                db.sales.insert_one({
                    "owner_id": st.session_state["owner_id"],
                    "item": entry["item"],
                    "quantity": int(entry["quantity"]),
                    "weather": weather,
                    "exams": exams,
                    "region": region,
                    "time_slot": entry["time_slot"],
                    "date": datetime.combine(date, datetime.min.time())
                })

            st.success("🎉 All items saved successfully!")

            # Clear session state
            st.session_state.daily_items = []

            st.rerun()
