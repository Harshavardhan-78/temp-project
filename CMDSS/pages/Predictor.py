import streamlit as st
import pandas as pd
import pickle
import os
import plotly.express as px
from utils.db_handler import fetch_sales_data

st.set_page_config(page_title="Demand Predictor", layout="wide")

# ------------------ SESSION STATE INIT ------------------

if "predicted_df" not in st.session_state:
    st.session_state["predicted_df"] = None

# ------------------ LOAD MODELS ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "rb") as f:
    rf = pickle.load(f)

with open(os.path.join(MODEL_DIR, "gb_model.pkl"), "rb") as f:
    gb = pickle.load(f)

with open(os.path.join(MODEL_DIR, "encoders.pkl"), "rb") as f:
    encoders = pickle.load(f)

# ------------------ SAFE ENCODE ------------------

def safe_encode(column, value):
    if value in encoders[column].classes_:
        return encoders[column].transform([value])[0]
    return encoders[column].transform([encoders[column].classes_[0]])[0]

# ------------------ LOAD DATA ------------------

@st.cache_data
def load_data(owner_id):
    return fetch_sales_data(owner_id)

st.title("🔮 Smart Next-Day Demand Forecast")

if "owner_id" not in st.session_state:
    st.error("Please login first.")
    st.stop()

df = load_data(st.session_state["owner_id"])

if df.empty:
    st.warning("No sales data available.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df["exams"] = df["exams"].fillna("None")
df = df.sort_values(["item", "date"])

# ------------------ CONTEXT INPUT ------------------

st.subheader("📌 Tomorrow Context")

col1, col2, col3, col4 = st.columns(4)

with col1:
    weather = st.selectbox("Weather", ["Sunny", "Rainy", "Cloudy"])
with col2:
    exams = st.selectbox("Exams", ["None", "Midterms", "Finals"])
with col3:
    region = st.selectbox("Region", ["Urban", "Rural"])
with col4:
    time_slot = st.selectbox("Time Slot", ["Morning", "Afternoon", "Evening", "Night"])

# ------------------ PREDICT BUTTON ------------------

if st.button("🚀 Predict Tomorrow Demand", use_container_width=True):

    results = []
    items = df["item"].unique()

    last_date = df["date"].max()
    next_date = last_date + pd.Timedelta(days=1)

    day_of_week = next_date.weekday()
    week_of_year = next_date.isocalendar().week

    for item in items:

        item_data = df[df["item"] == item].sort_values("date")
        quantities = item_data["quantity"].values

        lag_1 = quantities[-1] if len(quantities) >= 1 else 0
        lag_2 = quantities[-2] if len(quantities) >= 2 else 0
        lag_3 = quantities[-3] if len(quantities) >= 3 else 0
        lag_7 = quantities[-7] if len(quantities) >= 7 else 0

        rolling_avg_3 = item_data["quantity"].tail(3).mean()
        rolling_avg_7 = item_data["quantity"].tail(7).mean()
        rolling_std_7 = item_data["quantity"].tail(7).std()
        rolling_std_7 = 0 if pd.isna(rolling_std_7) else rolling_std_7

        input_data = {
            "weather": safe_encode("weather", weather),
            "exams": safe_encode("exams", exams),
            "region": safe_encode("region", region),
            "time_slot": safe_encode("time_slot", time_slot),
            "day_of_week": day_of_week,
            "week_of_year": week_of_year,
            "item": safe_encode("item", item),
            "lag_1": lag_1,
            "lag_2": lag_2,
            "lag_3": lag_3,
            "lag_7": lag_7,
            "rolling_avg_3": rolling_avg_3,
            "rolling_avg_7": rolling_avg_7,
            "rolling_std_7": rolling_std_7
        }

        feature_order = [
            "weather", "exams", "region", "time_slot",
            "day_of_week", "week_of_year", "item",
            "lag_1", "lag_2", "lag_3", "lag_7",
            "rolling_avg_3", "rolling_avg_7", "rolling_std_7"
        ]

        input_df = pd.DataFrame([input_data])[feature_order]

        rf_pred = rf.predict(input_df)[0]
        gb_pred = gb.predict(input_df)[0]

        predicted = max(0, round((rf_pred + gb_pred) / 2))

        results.append({"Item": item, "Predicted Demand": predicted})

    st.session_state["predicted_df"] = (
        pd.DataFrame(results)
        .sort_values("Predicted Demand", ascending=False)
    )

# ------------------ DISPLAY RESULTS (Persistent) ------------------

if st.session_state["predicted_df"] is not None:

    result_df = st.session_state["predicted_df"]

    st.markdown("## 📊 Forecast Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Highest Demand", result_df.iloc[0]["Predicted Demand"])
    col2.metric("📦 Total Demand", result_df["Predicted Demand"].sum())
    col3.metric("📈 Avg Demand", round(result_df["Predicted Demand"].mean(), 1))

    # -------- FILTER --------

    selected_items = st.multiselect(
        "Filter Items",
        result_df["Item"],
        default=result_df["Item"]
    )

    filtered_df = result_df[result_df["Item"].isin(selected_items)]

    # -------- VIEW MODE --------

    view_mode = st.radio("View Mode", ["Table", "Graph"], horizontal=True)

    if view_mode == "Table":
        st.dataframe(filtered_df, use_container_width=True)
    else:
        fig = px.bar(
            filtered_df,
            x="Item",
            y="Predicted Demand",
            text="Predicted Demand",
            color="Predicted Demand",
            color_continuous_scale="greens"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # -------- TOP 3 --------

    st.markdown("### 🏆 Top 3 High Demand Items")
    medals = ["🥇", "🥈", "🥉"]

    for i, (_, row) in enumerate(result_df.head(3).iterrows()):
        st.success(f"{medals[i]} {row['Item']} → {row['Predicted Demand']} units")