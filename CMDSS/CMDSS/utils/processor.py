import pandas as pd
def generate_historical_insights(df):
    insights = []

    if df.empty:
        return ["No data available."]

    top_item = df.groupby("item")["quantity"].sum().idxmax()
    insights.append(f"🔥 Most popular item: {top_item}")

    total_sales = df["quantity"].sum()
    insights.append(f"📦 Total units sold: {total_sales}")

    rainy_sales = df[df["weather"] == "Rainy"]["quantity"].sum()
    if rainy_sales > 0:
        insights.append("🌧 Rainy days increase demand.")

    return insights
def generate_menu_plan(df):

    df["date"] = pd.to_datetime(df["date"])
    df["day_name"] = df["date"].dt.day_name()

    grouped = df.groupby(
        ["day_name", "time_slot", "item"]
    )["quantity"].sum().reset_index()

    menu_plan = {}

    for _, row in grouped.iterrows():
        day = row["day_name"]
        slot = row["time_slot"]
        item = row["item"]

        if day not in menu_plan:
            menu_plan[day] = {}

        if slot not in menu_plan[day]:
            menu_plan[day][slot] = []

        menu_plan[day][slot].append(item)

    return menu_plan

