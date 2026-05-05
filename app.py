import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Strategic Expansion Intelligence",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #FAFAF8;
    }

    .hero {
        background: linear-gradient(135deg, #0B0B0B 0%, #1E1E1E 100%);
        padding: 2rem;
        border-radius: 22px;
        margin-bottom: 1.5rem;
        color: white;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #D6C28D;
        max-width: 900px;
    }

    .section-note {
        color: #666666;
        font-size: 0.95rem;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E8E3D5;
        padding: 1rem;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("beauty_expansion_data.csv")

# -----------------------------
# SIDEBAR
# -----------------------------
logo_path = Path("logo.png")

if logo_path.exists():
    st.sidebar.image("logo.png", width=160)

st.sidebar.title("Scenario Controls")
st.sidebar.markdown("Adjust assumptions to test expansion scenarios.")

selected_cities = st.sidebar.multiselect(
    "Select Markets",
    options=df["City"].unique(),
    default=df["City"].unique()
)

rent_change = st.sidebar.slider(
    "Rent Change (%)",
    min_value=-30,
    max_value=50,
    value=0,
    step=5
)

ticket_change = st.sidebar.slider(
    "Revenue / Average Ticket Change (%)",
    min_value=-30,
    max_value=50,
    value=0,
    step=5
)

customer_change = st.sidebar.slider(
    "Customer Volume Change (%)",
    min_value=-30,
    max_value=50,
    value=0,
    step=5
)

# -----------------------------
# FILTER DATA
# -----------------------------
filtered = df[df["City"].isin(selected_cities)].copy()

# -----------------------------
# SCENARIO CALCULATIONS
# -----------------------------
filtered["Scenario_Rent"] = filtered["Estimated_Monthly_Rent"] * (1 + rent_change / 100)

filtered["Scenario_Revenue"] = (
    filtered["Estimated_Monthly_Revenue"]
    * (1 + ticket_change / 100)
    * (1 + customer_change / 100)
)

filtered["Non_Rent_Cost"] = (
    filtered["Estimated_Monthly_Cost"] - filtered["Estimated_Monthly_Rent"]
)

filtered["Scenario_Cost"] = filtered["Non_Rent_Cost"] + filtered["Scenario_Rent"]

filtered["Scenario_Profit"] = filtered["Scenario_Revenue"] - filtered["Scenario_Cost"]

filtered["Scenario_ROI"] = filtered["Scenario_Profit"] / filtered["Scenario_Cost"]

# -----------------------------
# RECOMMENDATION LOGIC
# -----------------------------
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

filtered["Final_Scenario_Score"] = (
    filtered["Beauty_Expansion_Score"] * 0.5
    + (filtered["Scenario_ROI"] * 100) * 0.5
)

filtered = filtered.sort_values("Final_Scenario_Score", ascending=False)

# -----------------------------
# HERO HEADER
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">Strategic Expansion Intelligence Platform</div>
    <div class="hero-subtitle">
        Interactive decision-support system for beauty franchise expansion,
        market prioritization, ROI simulation, and executive recommendations.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# EMPTY STATE
# -----------------------------
if filtered.empty:
    st.warning("Please select at least one market from the sidebar.")
    st.stop()

# -----------------------------
# KPI CARDS
# -----------------------------
top_market = filtered.iloc[0]["City"]
avg_roi = filtered["Scenario_ROI"].mean()
total_profit = filtered["Scenario_Profit"].sum()
priority_count = (
    filtered["AI_Strategic_Recommendation"] == "Priority Expansion Market"
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Top Market", top_market)
col2.metric("Average Scenario ROI", f"{avg_roi:.1%}")
col3.metric("Total Scenario Profit", f"${total_profit:,.0f}")
col4.metric("Priority Markets", priority_count)

st.divider()

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Financial Scenario",
    "Market Positioning",
    "Recommendation Engine",
    "Executive Summary"
])

# -----------------------------
# TAB 1 — OVERVIEW
# -----------------------------
with tab1:
    st.subheader("Market Expansion Ranking")
    st.markdown(
        '<p class="section-note">Markets are ranked based on expansion score and scenario-adjusted ROI.</p>',
        unsafe_allow_html=True
    )

    fig = px.bar(
        filtered,
        x="City",
        y="Final_Scenario_Score",
        color="AI_Strategic_Recommendation",
        text="Final_Scenario_Score",
        title="Final Scenario Score by Market"
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(height=520)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Executive Ranking Table")

    overview_cols = [
        "City",
        "Beauty_Demand_Signal",
        "Premium_Fit_Score",
        "Competitive_Pressure",
        "Beauty_Expansion_Score",
        "Scenario_ROI",
        "Scenario_Profit",
        "Final_Scenario_Score",
        "AI_Strategic_Recommendation"
    ]

    st.dataframe(
        filtered[overview_cols],
        use_container_width=True
    )

# -----------------------------
# TAB 2 — FINANCIAL SCENARIO
# -----------------------------
with tab2:
    st.subheader("Revenue vs. Cost Simulation")
    st.markdown(
        '<p class="section-note">This view shows whether each market remains financially viable under the selected assumptions.</p>',
        unsafe_allow_html=True
    )

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
    fig2.update_layout(height=520)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Scenario ROI by Market")

    fig3 = px.bar(
        filtered,
        x="City",
        y="Scenario_ROI",
        color="AI_Strategic_Recommendation",
        text="Scenario_ROI",
        title="Scenario ROI"
    )
    fig3.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TAB 3 — MARKET POSITIONING
# -----------------------------
with tab3:
    st.subheader("Demand vs Premium Fit Matrix")
    st.markdown(
        '<p class="section-note">This matrix compares demand strength against premium positioning potential.</p>',
        unsafe_allow_html=True
    )

    fig4 = px.scatter(
        filtered,
        x="Beauty_Demand_Signal",
        y="Premium_Fit_Score",
        size="Population",
        color="AI_Strategic_Recommendation",
        hover_name="City",
        title="Market Positioning Matrix"
    )
    fig4.update_layout(height=560)
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Competitive Pressure")

    fig5 = px.bar(
        filtered,
        x="City",
        y="Competitive_Pressure",
        color="AI_Strategic_Recommendation",
        title="Competitive Pressure by Market"
    )
    fig5.update_layout(height=480)
    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# TAB 4 — RECOMMENDATION ENGINE
# -----------------------------
with tab4:
    st.subheader("AI-Assisted Strategic Recommendation")

    recommendation_cols = [
        "City",
        "Scenario_Revenue",
        "Scenario_Cost",
        "Scenario_Profit",
        "Scenario_ROI",
        "Premium_Fit_Score",
        "Final_Scenario_Score",
        "AI_Strategic_Recommendation"
    ]

    st.dataframe(
        filtered[recommendation_cols],
        use_container_width=True
    )

    st.markdown("### Recommendation Logic")

    st.markdown("""
    - **Priority Expansion Market:** positive profit and ROI equal to or above 15%.
    - **Validate Further:** positive profit but ROI below 15%.
    - **Premium Niche / High Cost Risk:** strong premium fit but negative profit.
    - **High Risk Under Current Assumptions:** weak financial viability under current assumptions.
    """)

# -----------------------------
# TAB 5 — EXECUTIVE SUMMARY
# -----------------------------
with tab5:
    top = filtered.iloc[0]

    st.subheader("Auto-Generated Executive Summary")

    st.markdown(f"""
    ### Key Recommendation

    **Top recommended market:** {top["City"]}

    Under the selected scenario assumptions, **{top["City"]}** ranks as the strongest expansion opportunity with a final scenario score of **{top["Final_Scenario_Score"]:.1f}**.

    **Current scenario assumptions:**
    - Rent change: **{rent_change}%**
    - Revenue / average ticket change: **{ticket_change}%**
    - Customer volume change: **{customer_change}%**

    **Model recommendation:** **{top["AI_Strategic_Recommendation"]}**

    This market shows the strongest balance between demand potential, premium fit, competitive positioning, and financial viability under the current scenario.
    """)

    st.markdown("### Suggested Next Steps")

    st.markdown("""
    1. Validate top markets using real estate listings and broker input.
    2. Move from city-level analysis to ZIP-code or trade-area analysis.
    3. Replace assumptions with internal revenue, service mix, and customer data.
    4. Use the dashboard as a recurring decision-support tool for expansion planning.
    """)
