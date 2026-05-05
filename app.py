import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Expansion Intelligence",
    layout="wide"
)

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("beauty_expansion_data.csv")

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.title("Scenario Controls")

selected_cities = st.sidebar.multiselect(
    "Select markets",
    options=df["City"].unique(),
    default=df["City"].unique()
)

rent_change = st.sidebar.slider(
    "Rent change scenario (%)",
    min_value=-30,
    max_value=50,
    value=0,
    step=5
)

ticket_change = st.sidebar.slider(
    "Revenue / average ticket change (%)",
    min_value=-30,
    max_value=50,
    value=0,
    step=5
)

customer_change = st.sidebar.slider(
    "Customer volume change (%)",
    min_value=-30,
    max_value=50,
    value=0,
    step=5
)

# -----------------------------
# Filter data
# -----------------------------
filtered = df[df["City"].isin(selected_cities)].copy()

# -----------------------------
# Scenario calculations
# -----------------------------
filtered["Scenario_Rent"] = filtered["Estimated_Monthly_Rent"] * (1 + rent_change / 100)

filtered["Scenario_Revenue"] = (
    filtered["Estimated_Monthly_Revenue"]
    * (1 + ticket_change / 100)
    * (1 + customer_change / 100)
)

# Keep non-rent costs fixed
filtered["Non_Rent_Cost"] = filtered["Estimated_Monthly_Cost"] - filtered["Estimated_Monthly_Rent"]

filtered["Scenario_Cost"] = filtered["Non_Rent_Cost"] + filtered["Scenario_Rent"]

filtered["Scenario_Profit"] = filtered["Scenario_Revenue"] - filtered["Scenario_Cost"]

filtered["Scenario_ROI"] = filtered["Scenario_Profit"] / filtered["Scenario_Cost"]

# Recommendation logic
def recommendation(row):
    if row["Scenario_Profit"] > 0 and row["Scenario_ROI"] >= 0.15:
        return "Priority Expansion Market"
    elif row["Scenario_Profit"] > 0 and row["Scenario_ROI"] < 0.15:
        return "Validate Further"
    elif row["Premium_Fit_Score"] >= 70 and row["Scenario_Profit"] < 0:
        return "Premium Niche / High Cost Risk"
    else:
        return "High Risk Under Current Assumptions"

filtered["AI_Strategic_Recommendation"] = filtered.apply(recommendation, axis=1)

# Final ranking
filtered["Final_Scenario_Score"] = (
    filtered["Beauty_Expansion_Score"] * 0.5
    + (filtered["Scenario_ROI"] * 100) * 0.5
)

filtered = filtered.sort_values("Final_Scenario_Score", ascending=False)

# -----------------------------
# Header
# -----------------------------
st.title("Expansion Intelligence Dashboard")
st.markdown(
    "Interactive decision-support tool for beauty franchise expansion, market prioritization, and ROI scenario analysis."
)

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

top_market = filtered.iloc[0]["City"] if len(filtered) > 0 else "N/A"
avg_roi = filtered["Scenario_ROI"].mean() if len(filtered) > 0 else 0
total_profit = filtered["Scenario_Profit"].sum() if len(filtered) > 0 else 0
priority_count = (filtered["AI_Strategic_Recommendation"] == "Priority Expansion Market").sum()

col1.metric("Top Market", top_market)
col2.metric("Average Scenario ROI", f"{avg_roi:.1%}")
col3.metric("Total Scenario Profit", f"${total_profit:,.0f}")
col4.metric("Priority Markets", priority_count)

st.divider()

# -----------------------------
# Charts
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Expansion Ranking")
    fig = px.bar(
        filtered,
        x="City",
        y="Final_Scenario_Score",
        title="Final Scenario Score by Market",
        text="Final_Scenario_Score"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Revenue vs Cost")
    revenue_cost = filtered.melt(
        id_vars="City",
        value_vars=["Scenario_Revenue", "Scenario_Cost"],
        var_name="Metric",
        value_name="Amount"
    )
    fig2 = px.bar(
        revenue_cost,
        x="City",
        y="Amount",
        color="Metric",
        barmode="group",
        title="Scenario Revenue vs Scenario Cost"
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Demand vs Premium Fit")
    fig3 = px.scatter(
        filtered,
        x="Beauty_Demand_Signal",
        y="Premium_Fit_Score",
        size="Population",
        color="AI_Strategic_Recommendation",
        hover_name="City",
        title="Market Positioning Matrix"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Scenario ROI")
    fig4 = px.bar(
        filtered,
        x="City",
        y="Scenario_ROI",
        title="Scenario ROI by Market",
        text="Scenario_ROI"
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# -----------------------------
# Table
# -----------------------------
st.subheader("Executive Market Ranking Table")

display_cols = [
    "City",
    "Beauty_Demand_Signal",
    "Premium_Fit_Score",
    "Competitive_Pressure",
    "Beauty_Expansion_Score",
    "Scenario_Revenue",
    "Scenario_Cost",
    "Scenario_Profit",
    "Scenario_ROI",
    "Final_Scenario_Score",
    "AI_Strategic_Recommendation"
]

st.dataframe(
    filtered[display_cols],
    use_container_width=True
)

# -----------------------------
# Executive Summary
# -----------------------------
st.subheader("Auto-Generated Executive Summary")

if len(filtered) > 0:
    top = filtered.iloc[0]

    st.markdown(f"""
    **Top recommended market:** {top["City"]}

    Under the current scenario assumptions, **{top["City"]}** ranks as the strongest expansion opportunity with a final scenario score of **{top["Final_Scenario_Score"]:.1f}**.

    The current scenario assumes:
    - Rent change: **{rent_change}%**
    - Revenue / average ticket change: **{ticket_change}%**
    - Customer volume change: **{customer_change}%**

    The model recommends: **{top["AI_Strategic_Recommendation"]}**.
    """)
