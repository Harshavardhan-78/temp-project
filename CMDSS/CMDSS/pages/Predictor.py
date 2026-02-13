import streamlit as st
import pandas as pd
from utils.db_handler import fetch_sales_data

st.title("🔮 Item-wise Weekly Demand Predictor")

if "owner_id" not in st.session_state:
    st.error("Please login")
    st.stop()

df = fetch_sales_data(st.session_state["owner_id"])

if df.empty:
    st.warning("No sales data available")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# Require minimum 7 days
if df["date"].nunique() < 7:
    st.warning("Minimum 7 days of data required.")
    st.stop()

st.subheader("📊 Historical Item Performance")

weather = st.selectbox("Next Week Weather", ["Sunny", "Rainy", "Cloudy"])
exams = st.selectbox("Next Week Exams", ["None", "Midterms", "Finals"])
region = st.selectbox("Region", ["Urban", "Rural"])

if st.button("Predict Item-wise Demand"):

    results = []

    items = df["item"].unique()

    for item in items:

        item_data = df[df["item"] == item]

        # Average demand under selected conditions
        condition_data = item_data[
            (item_data["weather"] == weather) &
            (item_data["exams"] == exams) &
            (item_data["region"] == region)
        ]

        if not condition_data.empty:
            predicted = condition_data["quantity"].mean()
        else:
            predicted = item_data["quantity"].mean()

        results.append({
            "Item": item,
            "Predicted Demand": round(predicted, 2)
        })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Predicted Demand", ascending=False)

    st.subheader("📈 Predicted Demand for Next Week")
    st.dataframe(result_df)

    # Show condition sensitivity
    st.subheader("🌦 Condition Sensitivity Analysis")

    for item in items:
        st.markdown(f"### {item}")

        avg_sunny = df[(df["item"] == item) & (df["weather"] == "Sunny")]["quantity"].mean()
        avg_rainy = df[(df["item"] == item) & (df["weather"] == "Rainy")]["quantity"].mean()
        avg_finals = df[(df["item"] == item) & (df["exams"] == "Finals")]["quantity"].mean()

        st.write(f"Sunny Avg: {round(avg_sunny,2) if not pd.isna(avg_sunny) else 0}")
        st.write(f"Rainy Avg: {round(avg_rainy,2) if not pd.isna(avg_rainy) else 0}")
        st.write(f"Finals Avg: {round(avg_finals,2) if not pd.isna(avg_finals) else 0}")

        if avg_rainy > avg_sunny:
            st.success("⬆ Demand increases during Rainy days")

        if avg_finals > avg_sunny:
            st.success("⬆ Demand increases during Exam periods")
