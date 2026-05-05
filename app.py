import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Strategic Expansion Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS DARK LUXURY THEME
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0B0B0D;
        color: #F5F2EA;
    }

    section[data-testid="stSidebar"] {
        background-color: #080809;
        border-right: 1px solid #2A2418;
    }

    section[data-testid="stSidebar"] * {
        color: #E8D28A !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    .hero {
        background: linear-gradient(135deg, #111111 0%, #1A1A1A 100%);
        border: 1px solid #3B321F;
        padding: 2rem 2.2rem;
        border-radius: 24px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 35px rgba(0,0,0,0.45);
    }

    .hero-title {
        color: #F6E6A8;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        color: #D8D1BF;
        font-size: 1rem;
        max-width: 900px;
        line-height: 1.6;
    }

    .metric-card {
        background-color: #171719;
        border: 1px solid #3B321F;
        padding: 1.2rem;
        border-radius: 20px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.35);
    }

    div[data-testid="stMetric"] {
        background-color: #171719;
        border: 1px solid #3B321F;
        padding: 1rem;
        border-radius: 18px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.35);
    }

    div[data-testid="stMetricLabel"] {
        color: #C8B56E !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 1.7rem;
        font-weight: 800;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #171719;
        border: 1px solid #3B321F;
        border-radius: 14px;
        color: #E8D28A;
        padding: 10px 18px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #E8D28A !important;
        color: #090909 !important;
        font-weight: 700;
    }

    h1, h2, h3 {
        color: #F6E6A8 !important;
    }

    .section-note {
        color: #BFB8A6;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .stDataFrame {
        background-color: #111111;
        border-radius: 18px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("beauty_expansion_data.csv")
df.columns = df.columns.str.strip()

if "City" not in df.columns:
    st.error("The CSV must include a column named 'City'. Please check the file.")
    st.stop()

df = df.dropna(subset=["City"])

# -----------------------------
# SIDEBAR
# -----------------------------
logo_path = Path("logo.png")

if logo_path.exists():
    st.sidebar.image("logo.png", width=120)

st.sidebar.markdown("## Scenario Controls")
st.sidebar.markdown("Adjust assumptions to test expansion scenarios.")

selected_cities = st.sidebar.multiselect(
    "Select Markets",
    options=sorted(df["City"].unique()),
    default=sorted(df["City"].unique())
)

rent_change = st.sidebar.slider("Rent Change (%)", -30, 50, 0, 5)
ticket_change = st.sidebar.slider("Revenue / Average Ticket Change (%)", -30, 50, 0, 5)
customer_change = st.sidebar.slider("Customer Volume Change (%)", -30, 50, 0, 5)

# -----------------------------
# FILTER
# -----------------------------
filtered = df[df["City"].isin(selected_cities)].copy()

if filtered.empty:
    st.warning("Please select at least one market from the sidebar.")
    st.stop()

# -----------------------------
# SCENARIO CALCULATIONS
# -----------------------------
filtered["Scenario_Rent"] = filtered["Estimated_Monthly_Rent"] * (1 + rent_change / 100)

filtered["Scenario_Revenue"] = (
    filtered["Estimated_Monthly_Revenue"]
    * (1 + ticket_change / 100)
    * (1 + customer_change / 100)
)

filtered["Non_Rent_Cost"] = filtered["Estimated_Monthly_Cost"] - filtered["Estimated_Monthly_Rent"]
filtered["Scenario_Cost"] = filtered["Non_Rent_Cost"] + filtered["Scenario_Rent"]
filtered["Scenario_Profit"] = filtered["Scenario_Revenue"] - filtered["Scenario_Cost"]
filtered["Scenario_ROI"] = filtered["Scenario_Profit"] / filtered["Scenario_Cost"]

def recommendation(row):
    if row["Scenario_Profit"] > 0 and row["Scenario_ROI"] >= 0.15:
        return "Priority Expansion"
    elif row["Scenario_Profit"] > 0:
        return "Validate Further"
    elif row["Premium_Fit_Score"] >= 70 and row["Scenario_Profit"] < 0:
        return "Premium Strategy"
    else:
        return "High Risk"

filtered["Recommendation"] = filtered.apply(recommendation, axis=1)

filtered["Final_Scenario_Score"] = (
    filtered["Beauty_Expansion_Score"] * 0.5
    + (filtered["Scenario_ROI"] * 100) * 0.5
)

filtered = filtered.sort_values("Final_Scenario_Score", ascending=False)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">Strategic Expansion Intelligence Platform</div>
    <div class="hero-subtitle">
        Executive dashboard for beauty franchise expansion, market prioritization,
        ROI scenario simulation, and strategic recommendations.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# KPIs
# -----------------------------
top_market = filtered.iloc[0]["City"]
avg_roi = filtered["Scenario_ROI"].mean()
total_profit = filtered["Scenario_Profit"].sum()
priority_count = (filtered["Recommendation"] == "Priority Expansion").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Top Market", top_market)
col2.metric("Average ROI", f"{avg_roi:.1%}")
col3.metric("Scenario Profit", f"${total_profit:,.0f}")
col4.metric("Priority Markets", priority_count)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Financials",
    "Market Positioning",
    "Recommendations",
    "Executive Summary"
])

# -----------------------------
# TAB 1
# -----------------------------
with tab1:
    st.subheader("Market Expansion Ranking")
    st.markdown('<p class="section-note">Markets ranked by scenario-adjusted expansion score.</p>', unsafe_allow_html=True)

    fig = px.bar(
        filtered,
        x="City",
        y="Final_Scenario_Score",
        color="Recommendation",
        text="Final_Scenario_Score",
        color_discrete_sequence=["#E8D28A", "#B89A45", "#6F5B2E", "#3A3A3A"]
    )
    fig.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font_color="#F5F2EA",
        height=520
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2
# -----------------------------
with tab2:
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
        color_discrete_sequence=["#E8D28A", "#8C6F2F"]
    )
    fig2.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font_color="#F5F2EA",
        height=520
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Scenario ROI")

    fig3 = px.bar(
        filtered,
        x="City",
        y="Scenario_ROI",
        color="Recommendation",
        text="Scenario_ROI",
        color_discrete_sequence=["#E8D28A", "#B89A45", "#6F5B2E", "#3A3A3A"]
    )
    fig3.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font_color="#F5F2EA",
        height=480
    )
    fig3.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TAB 3
# -----------------------------
with tab3:
    st.subheader("Demand vs Premium Fit")

    fig4 = px.scatter(
        filtered,
        x="Beauty_Demand_Signal",
        y="Premium_Fit_Score",
        size="Population",
        color="Recommendation",
        hover_name="City",
        color_discrete_sequence=["#E8D28A", "#B89A45", "#6F5B2E", "#3A3A3A"]
    )
    fig4.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font_color="#F5F2EA",
        height=560
    )
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# TAB 4
# -----------------------------
with tab4:
    st.subheader("Recommendation Engine")

    cols = [
        "City",
        "Scenario_Revenue",
        "Scenario_Cost",
        "Scenario_Profit",
        "Scenario_ROI",
        "Premium_Fit_Score",
        "Final_Scenario_Score",
        "Recommendation"
    ]

    st.dataframe(filtered[cols], use_container_width=True)

    st.markdown("""
    ### Logic
    - **Priority Expansion:** positive profit and ROI ≥ 15%.
    - **Validate Further:** positive profit but ROI below 15%.
    - **Premium Strategy:** strong premium fit but negative profit.
    - **High Risk:** weak financial viability under current assumptions.
    """)

# -----------------------------
# TAB 5
# -----------------------------
with tab5:
    top = filtered.iloc[0]

    st.subheader("Auto-Generated Executive Summary")

    st.markdown(f"""
    ### Key Recommendation

    **Top recommended market:** {top["City"]}

    Under the selected scenario, **{top["City"]}** ranks as the strongest expansion opportunity with a final scenario score of **{top["Final_Scenario_Score"]:.1f}**.

    **Scenario assumptions:**
    - Rent change: **{rent_change}%**
    - Revenue / ticket change: **{ticket_change}%**
    - Customer volume change: **{customer_change}%**

    **Model recommendation:** **{top["Recommendation"]}**

    This market shows the strongest balance between demand potential, premium fit, competitive positioning, and financial viability.
    """)
