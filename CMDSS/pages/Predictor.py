import streamlit as st
import pandas as pd
from utils.db_handler import fetch_sales_data
import math

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

        item_data = df[df["item"] == item].sort_values("date")

        condition_data = item_data[
            (item_data["weather"] == weather) &
            (item_data["exams"] == exams) &
            (item_data["region"] == region)
        ]

        # --- Predicted Demand ---
        if not condition_data.empty:
            predicted = condition_data["quantity"].mean()
        else:
            predicted = item_data["quantity"].mean()

        predicted = math.ceil(predicted)

        # --- Demand Level ---
        if predicted < 50:
            level = "LOW"
            recommendation = "Reduce Stock"
        elif predicted < 120:
            level = "MEDIUM"
            recommendation = "Maintain Stock"
        else:
            level = "HIGH"
            recommendation = "Stock More"

        # --- Trend Calculation ---
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
            "Demand Level": level,
            "Trend": trend,
            "Recommendation": recommendation,
            "Predicted Value": predicted
        })

    result_df = pd.DataFrame(results)

    # Rank by predicted value
    result_df = result_df.sort_values(by="Predicted Value", ascending=False)

    # Drop numeric column before display
    display_df = result_df.drop(columns=["Predicted Value"])

    st.subheader("📊 Decision Support Summary")
    st.dataframe(display_df, use_container_width=True)

    # ---------------- TOP 3 HIGHLIGHT ----------------
    st.markdown("### 🏆 Top Performing Items")

    top3 = display_df.head(3)

    medals = ["🥇", "🥈", "🥉"]

    for i, (_, row) in enumerate(top3.iterrows()):
        st.success(f"{medals[i]} {row['Item']} → {row['Demand Level']} | {row['Trend']} | {row['Recommendation']}")

    # ---------------- REASONING SECTION ----------------
    st.markdown("---")
    st.markdown("### 🧠 Reasoning Behind Predictions")

    for item in items:

        item_df = df[df["item"] == item]

        st.markdown(f"#### {item}")
        reasons = []

        # ---- Weather Effect ----
        avg_sunny = item_df[item_df["weather"] == "Sunny"]["quantity"].mean()
        avg_rainy = item_df[item_df["weather"] == "Rainy"]["quantity"].mean()

        if pd.notna(avg_rainy) and pd.notna(avg_sunny):
            if avg_rainy > avg_sunny:
                reasons.append(f"🌧 Rainy days historically increase {item} sales")

        # ---- Exam Effect ----
        avg_none = item_df[item_df["exams"] == "None"]["quantity"].mean()
        avg_finals = item_df[item_df["exams"] == "Finals"]["quantity"].mean()

        if pd.notna(avg_finals) and pd.notna(avg_none):
            if avg_finals > avg_none:
                reasons.append("📚 Exam periods boost demand")

        # ---- Time Slot Effect ----
        avg_evening = item_df[item_df["time_slot"] == "Evening"]["quantity"].mean()
        avg_overall = item_df["quantity"].mean()

        if pd.notna(avg_evening):
            if avg_evening > avg_overall:
                reasons.append("🌇 Evening consumption is higher than other slots")

        # ---- Display Reasons ----
        if reasons:
            st.markdown("**Reason:**")
            for r in reasons:
                st.write(f"• {r}")
        else:
            st.write("• No strong historical pattern detected")

        st.write(" ")
