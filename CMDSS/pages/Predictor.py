import streamlit as st
import pandas as pd
from utils.db_handler import fetch_sales_data
import math
import pickle
import datetime

with open("CMDSS/models/rf_regressor.pkl", "rb") as f:

    model = pickle.load(f)

with open("CMDSS/models/encoders.pkl", "rb") as f:
    encoders = pickle.load(f)

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
time_slot = st.selectbox("Time Slot", ["Morning", "Afternoon", "Evening", "Night"])
day_of_week = st.selectbox("Day of Week", list(range(7)))


if st.button("Predict Item-wise Demand"):

    results = []
    items = df["item"].unique()

    for item in items:

        item_data = df[df["item"] == item].sort_values("date")

        rolling_avg = item_data["quantity"].tail(3).mean()

        input_data = {
            "weather": encoders["weather"].transform([weather])[0],
            "exams": encoders["exams"].transform([exams])[0],
            "region": encoders["region"].transform([region])[0],
            "time_slot": encoders["time_slot"].transform([time_slot])[0],
            "day_of_week": day_of_week,
            "item": encoders["item"].transform([item])[0],
            "rolling_avg_3": rolling_avg
        }

        input_df = pd.DataFrame([input_data])

        predicted = model.predict(input_df)[0]
        predicted = max(0, round(predicted))

        # Convert to business label
        if predicted < df["quantity"].quantile(0.33):
            level = "LOW"
            recommendation = "Reduce Stock"
        elif predicted < df["quantity"].quantile(0.66):
            level = "MEDIUM"
            recommendation = "Maintain Stock"
        else:
            level = "HIGH"
            recommendation = "Stock More"

        # Trend
        if len(item_data) >= 6:
            recent = item_data.tail(3)["quantity"].mean()
            older = item_data.head(3)["quantity"].mean()

            if recent > older:
                trend = "📈 Increasing"
            elif recent < older:
                trend = "📉 Decreasing"
            else:
                trend = "➖ Stable"
        else:
            trend = "➖ Stable"

        results.append({
            "Item": item,
            "Predicted Demand": predicted,
            "Demand Level": level,
            "Trend": trend,
            "Recommendation": recommendation
        })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Predicted Demand", ascending=False)

    st.subheader("📊 Decision Support Summary")
    st.dataframe(result_df, use_container_width=True)

    
    st.markdown("### 🏆 Top Performing Items")
    medals = ["🥇", "🥈", "🥉"]

    for i, (_, row) in enumerate(result_df.head(3).iterrows()):
        st.success(
            f"{medals[i]} {row['Item']} → {row['Predicted Demand']} units | "
            f"{row['Demand Level']} | {row['Trend']} | {row['Recommendation']}"
        )

    # ---------------- REASONING ----------------

    st.markdown("---")
    st.markdown("### 🧠 Reasoning Behind Predictions")

    for item in items:

        item_df = df[df["item"] == item]
        st.markdown(f"#### {item}")

        reasons = []

        avg_rainy = item_df[item_df["weather"] == "Rainy"]["quantity"].mean()
        avg_sunny = item_df[item_df["weather"] == "Sunny"]["quantity"].mean()

        if pd.notna(avg_rainy) and pd.notna(avg_sunny):
            if avg_rainy > avg_sunny:
                reasons.append("🌧 Rainy days historically increase sales")

        avg_finals = item_df[item_df["exams"] == "Finals"]["quantity"].mean()
        avg_none = item_df[item_df["exams"] == "None"]["quantity"].mean()

        if pd.notna(avg_finals) and pd.notna(avg_none):
            if avg_finals > avg_none:
                reasons.append("📚 Exam periods boost demand")

        avg_evening = item_df[item_df["time_slot"] == "Evening"]["quantity"].mean()
        avg_overall = item_df["quantity"].mean()

        if pd.notna(avg_evening):
            if avg_evening > avg_overall:
                reasons.append("🌇 Evening consumption higher than average")

        if reasons:
            st.markdown("**Reason:**")
            for r in reasons:
                st.write(f"• {r}")
        else:
            st.write("• No strong historical pattern detected")

        st.write(" ")


