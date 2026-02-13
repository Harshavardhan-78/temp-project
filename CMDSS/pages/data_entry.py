import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_handler import get_db

st.title("📥 Data Management")

if "owner_id" not in st.session_state:
    st.error("Please login first")
    st.stop()

db = get_db()

mode = st.radio(
    "Select Data Entry Mode",
    ["📂 Upload Historical CSV", "📝 Daily Journal Entry"]
)

# =====================================
# MODE 1 — CSV UPLOAD
# =====================================
if mode == "📂 Upload Historical CSV":

    st.subheader("Upload Historical Sales Data (CSV)")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        required_columns = [
            "item", "quantity", "weather",
            "exams", "region", "time_slot", "date"
        ]

        if not all(col in df.columns for col in required_columns):
            st.error("CSV format incorrect. Missing required columns.")
            st.stop()

        df["owner_id"] = st.session_state["owner_id"]
        df["date"] = pd.to_datetime(df["date"])

        if st.button("Upload to Database"):

            records = df.to_dict("records")
            db.sales.insert_many(records)

            st.success("Historical data uploaded successfully!")
            st.write(f"{len(records)} records inserted.")


# =====================================
# MODE 2 — DAILY JOURNAL ENTRY
# =====================================
else:
    st.subheader("Enter Daily Sales Journal")

    from datetime import datetime

    # Initialize session storage
    if "daily_items" not in st.session_state:
        st.session_state.daily_items = []

    # Step 1: Select Day Context (Once)
    st.markdown("### 📅 Day Details")

    date = st.date_input("Date", value=datetime.today())
    weather = st.selectbox("Weather", ["Sunny", "Rainy", "Cloudy"])
    exams = st.selectbox("Exam Schedule", ["None", "Midterms", "Finals"])
    region = st.selectbox("Region", ["Urban", "Rural"])

    st.markdown("---")
    st.markdown("### ➕ Add Items")

    # Step 2: Add Items Form
    with st.form("add_item_form"):

        item = st.text_input("Item Name")
        quantity = st.number_input("Quantity Sold", min_value=0)
        time_slot = st.selectbox(
            "Time Slot",
            ["Morning", "Afternoon", "Evening", "Night"]
        )

        add_item = st.form_submit_button("Add Item")

        if add_item:
            st.session_state.daily_items.append({
                "item": item,
                "quantity": quantity,
                "time_slot": time_slot
            })
            st.success(f"{item} added!")

    # Show added items
    if st.session_state.daily_items:
        st.markdown("### 📋 Items Added Today")
        for i, entry in enumerate(st.session_state.daily_items):
            st.write(f"{i+1}. {entry['item']} - {entry['quantity']} ({entry['time_slot']})")

    # Step 3: Final Save Button
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
