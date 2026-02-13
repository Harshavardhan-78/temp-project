import streamlit as st
import pandas as pd
from utils.db_handler import fetch_sales_data
from utils.processor import generate_historical_insights
from utils.processor import generate_menu_plan

st.title("📊 Smart Dashboard")

if "owner_id" not in st.session_state:
    st.error("Please login")
    st.stop()

df = fetch_sales_data(st.session_state["owner_id"])

if df.empty:
    st.warning("No sales data available")
    st.stop()

df["quantity"] = df["quantity"].astype(int)
df["date"] = pd.to_datetime(df["date"])

st.metric("Total Units Sold", df["quantity"].sum())

st.subheader("Insights")
for insight in generate_historical_insights(df):
    st.success(insight)

st.subheader("Item-wise Sales")
st.bar_chart(df.groupby("item")["quantity"].sum())

st.subheader("Daily Trend")
st.line_chart(df.groupby("date")["quantity"].sum())
st.subheader("📅 Recommended Weekly Menu Plan")

menu_plan = generate_menu_plan(df)

for day, slots in menu_plan.items():
    st.markdown(f"### {day}")
    for slot, items in slots.items():
        st.write(f"**{slot}:** {', '.join(items)}")