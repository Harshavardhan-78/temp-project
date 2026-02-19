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
col1, col2, col3 = st.columns(3)

col1.metric("📦 Total Units Sold", df["quantity"].sum())
col2.metric("📅 Active Days", df["date"].nunique())
col3.metric("🍽 Unique Items", df["item"].nunique())

st.markdown("---")

# Better grouped charts
import plotly.express as px

st.subheader("📊 Item-wise Sales")

item_sales = df.groupby("item")["quantity"].sum().reset_index()
fig1 = px.bar(item_sales, x="item", y="quantity",
              color="quantity",
              title="Total Sales per Item")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Daily Trend")

daily_sales = df.groupby("date")["quantity"].sum().reset_index()
fig2 = px.line(daily_sales, x="date", y="quantity",
               markers=True,
               title="Daily Sales Trend")
st.plotly_chart(fig2, use_container_width=True)
