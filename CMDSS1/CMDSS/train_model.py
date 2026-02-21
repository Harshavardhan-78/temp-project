import pandas as pd
import pickle
import os
import streamlit as st
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np

# ------------------ DATABASE ------------------

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = st.secrets["DB_NAME"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

df = pd.DataFrame(list(db.sales.find({}, {"_id": 0})))

if df.empty:
    raise Exception("No data available")

# ------------------ FEATURE ENGINEERING ------------------

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["item", "date"])

df["day_of_week"] = df["date"].dt.weekday
df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

# Fill exams null
df["exams"] = df["exams"].fillna("None")

# Lag features
df["lag_1"] = df.groupby("item")["quantity"].shift(1)
df["lag_2"] = df.groupby("item")["quantity"].shift(2)
df["lag_3"] = df.groupby("item")["quantity"].shift(3)
df["lag_7"] = df.groupby("item")["quantity"].shift(7)

# Rolling features
df["rolling_avg_3"] = df.groupby("item")["quantity"].transform(lambda x: x.rolling(3).mean())
df["rolling_avg_7"] = df.groupby("item")["quantity"].transform(lambda x: x.rolling(7).mean())
df["rolling_std_7"] = df.groupby("item")["quantity"].transform(lambda x: x.rolling(7).std())

df = df.fillna(0)

# ------------------ ENCODING ------------------

encoders = {}
categorical_cols = ["weather", "exams", "region", "time_slot", "item"]

for col in categorical_cols:
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col])

# ------------------ FEATURES ------------------

feature_cols = [
    "weather", "exams", "region", "time_slot",
    "day_of_week", "week_of_year", "item",
    "lag_1", "lag_2", "lag_3", "lag_7",
    "rolling_avg_3", "rolling_avg_7", "rolling_std_7"
]

X = df[feature_cols]
y = df["quantity"]

# ------------------ TIME SERIES SPLIT ------------------

tscv = TimeSeriesSplit(n_splits=5)

r2_scores = []
mae_scores = []

for train_index, test_index in tscv.split(X):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    rf = RandomForestRegressor(
        n_estimators=400,
        max_depth=15,
        min_samples_leaf=3,
        random_state=42
    )

    gb = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )

    rf.fit(X_train, y_train)
    gb.fit(X_train, y_train)

    rf_pred = rf.predict(X_test)
    gb_pred = gb.predict(X_test)

    final_pred = (rf_pred + gb_pred) / 2

    r2_scores.append(r2_score(y_test, final_pred))
    mae_scores.append(mean_absolute_error(y_test, final_pred))

print("\n==============================")
print(f"Average R²: {round(np.mean(r2_scores),3)}")
print(f"Average MAE: {round(np.mean(mae_scores),2)}")
print("==============================")

# Train final model on full dataset
rf.fit(X, y)
gb.fit(X, y)

# Save both models
os.makedirs("models", exist_ok=True)

with open("models/rf_model.pkl", "wb") as f:
    pickle.dump(rf, f)

with open("models/gb_model.pkl", "wb") as f:
    pickle.dump(gb, f)

with open("models/encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)

print("✅ Advanced ensemble model trained and saved.")