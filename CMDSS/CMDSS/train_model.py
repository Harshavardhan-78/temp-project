import pandas as pd
import pickle
import streamlit as st
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = st.secrets["DB_NAME"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

df = pd.DataFrame(list(db.sales.find({}, {"_id": 0})))

if df.empty:
    raise Exception("No data available for training")

encoders = {}
for col in ["weather", "exams", "region"]:
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col])

def inventory_label(q):
    if q < 50:
        return "LOW"
    elif q < 120:
        return "MEDIUM"
    return "HIGH"

df["inventory_level"] = df["quantity"].apply(inventory_label)

X = df[["weather", "exams", "region"]]
y = df["inventory_level"]

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X, y)

with open("models/rf_classifier.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved")
