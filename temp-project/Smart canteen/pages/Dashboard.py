import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_handler import fetch_sales_data



st.title("📊 Canteen Performance Dashboard")

if "owner_id" not in st.session_state:
    st.error("Please login first.")
    st.stop()

df = fetch_sales_data(st.session_state["owner_id"])

if df.empty:
    st.warning("No sales data available.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# ------------------ KPI SECTION ------------------

st.markdown("## 📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_sales = df["quantity"].sum()
avg_sales = round(df["quantity"].mean(), 2)
top_item = df.groupby("item")["quantity"].sum().idxmax()
total_items = df["item"].nunique()

col1.metric("📦 Total Units Sold", total_sales)
col2.metric("📈 Avg Daily Demand", avg_sales)
col3.metric("🏆 Top Performing Item", top_item)
col4.metric("🍽 Total Menu Items", total_items)

st.markdown("---")

# ------------------ FILTERS ------------------

st.markdown("## 🎛 Filter Data")

colf1, colf2 = st.columns(2)

with colf1:
    selected_items = st.multiselect(
        "Select Items",
        df["item"].unique(),
        default=df["item"].unique()
    )

with colf2:
    selected_weather = st.multiselect(
        "Weather Condition",
        df["weather"].unique(),
        default=df["weather"].unique()
    )

filtered_df = df[
    (df["item"].isin(selected_items)) &
    (df["weather"].isin(selected_weather))
]

st.markdown("---")

# ------------------ VISUALIZATION ------------------

st.markdown("## 📈 Demand Trends")

view = st.radio("Select View", ["Time Series", "Item Comparison"], horizontal=True)

if view == "Time Series":
    daily = filtered_df.groupby("date")["quantity"].sum().reset_index()

    fig = px.line(
        daily,
        x="date",
        y="quantity",
        markers=True,
        title="Daily Demand Trend"
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

else:
    item_summary = filtered_df.groupby("item")["quantity"].sum().reset_index()

    fig = px.bar(
        item_summary,
        x="item",
        y="quantity",
        text="quantity",
        color="quantity",
        color_continuous_scale="greens",
        title="Item-wise Sales"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ------------------ CONTEXT INSIGHTS ------------------

st.markdown("## 🧠 Context Insights")

colc1, colc2 = st.columns(2)

with colc1:
    weather_avg = filtered_df.groupby("weather")["quantity"].mean().reset_index()
    fig_weather = px.bar(
        weather_avg,
        x="weather",
        y="quantity",
        color="quantity",
        color_continuous_scale="blues",
        title="Average Demand by Weather"
    )
    fig_weather.update_layout(template="plotly_white")
    st.plotly_chart(fig_weather, use_container_width=True)

with colc2:
    exam_avg = filtered_df.groupby("exams")["quantity"].mean().reset_index()
    fig_exam = px.bar(
        exam_avg,
        x="exams",
        y="quantity",
        color="quantity",
        color_continuous_scale="oranges",
        title="Average Demand by Exam Status"
    )
    fig_exam.update_layout(template="plotly_white")
    st.plotly_chart(fig_exam, use_container_width=True)