import pandas as pd
import pickle
import os
import streamlit as st
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error

# ------------------ DATABASE ------------------

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = st.secrets["DB_NAME"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

df = pd.DataFrame(list(db.sales.find({}, {"_id": 0})))

if df.empty:
    raise Exception("No data available for training")

# ------------------ FEATURE ENGINEERING ------------------

df["date"] = pd.to_datetime(df["date"])
df["day_of_week"] = df["date"].dt.weekday

# Rolling average (strong feature)
df = df.sort_values("date")
df["rolling_avg_3"] = (
    df.groupby("item")["quantity"]
      .transform(lambda x: x.rolling(3, min_periods=1).mean())
)

# ------------------ ENCODING ------------------

encoders = {}

categorical_cols = ["weather", "exams", "region", "time_slot", "item"]

for col in categorical_cols:
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col])

# ------------------ FEATURES & TARGET ------------------

X = df[[
    "weather",
    "exams",
    "region",
    "time_slot",
    "day_of_week",
    "item",
    "rolling_avg_3"
]]

y = df["quantity"]

# ------------------ TRAIN TEST SPLIT ------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ------------------ MODEL ------------------

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=3,
    random_state=42
)

model.fit(X_train, y_train)

# ------------------ EVALUATION ------------------

y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print("\n==============================")
print(f"R² Score: {round(r2, 3)}")
print(f"Mean Absolute Error: {round(mae, 2)} units")
print("==============================")

# Cross Validation (R²)
cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")

print(f"Cross Validation R²: {round(cv_scores.mean(),3)}")

# ------------------ FEATURE IMPORTANCE ------------------

print("\nFeature Importance:")
for feature, importance in zip(X.columns, model.feature_importances_):
    print(f"{feature}: {round(importance * 100, 2)}%")

# ------------------ SAVE MODEL + ENCODERS ------------------

os.makedirs("models", exist_ok=True)

with open("models/rf_regressor.pkl", "wb") as f:
    pickle.dump(model, f)

with open("models/encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)

print("\n✅ Regression model trained and saved successfully.")
