import streamlit as st
from pymongo import MongoClient
import pandas as pd

@st.cache_resource
def get_db():
    client = MongoClient(st.secrets["MONGO_URI"])
    return client[st.secrets["DB_NAME"]]

def fetch_sales_data(owner_id):
    db = get_db()
    data = list(db.sales.find({"owner_id": owner_id}, {"_id": 0}))
    return pd.DataFrame(data)
