import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Strategic Expansion Intelligence TEST",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# COLORS
# -----------------------------
GOLD = "#C6A052"
GOLD_LIGHT = "#E8D28A"
BLACK = "#050505"
CHARCOAL = "#151515"
CARD = "#1B1B1D"
WHITE = "#F7F3EA"
MUTED = "#B8B1A3"

# -----------------------------
# CSS
# -----------------------------
st.markdown(f"""
<style>
    .stApp {{
        background-color: {BLACK};
        color: {WHITE};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1450px;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #080808;
        border-right: 1px solid #2C2415;
    }}

    section[data-testid="stSidebar"] * {{
        color: {WHITE};
    }}

    .hero {{
        background: linear-gradient(135deg, #141414 0%, #23201A 100%);
        border: 1px solid {GOLD};
        border-radius: 22px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 35px rgba(0,0,0,0.45);
    }}

    .hero-inner {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }}

    .hero-title {{
        color: {WHITE};
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem;
    }}

    .hero-subtitle {{
        color: {GOLD_LIGHT};
        font-size: 1rem;
        line-height: 1.5;
    }}

    .logo-box {{
        width: 92px;
        height: 92px;
        border-radius: 18px;
        background-color: {GOLD};
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .section-title {{
        color: {GOLD_LIGHT};
        font-size: 1.3rem;
        font-weight: 750;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }}

    .section-note {{
        color: {MUTED};
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }}

    div[data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid #3A301F;
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 8px 28px rgba(0,0,0,0.32);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {GOLD_LIGHT} !important;
        font-weight: 650;
    }}

    div[data-testid="stMetricValue"] {{
        color: {WHITE} !important;
        font-weight: 800;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        margin-bottom: 1rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #0D0D0D;
        border: 1px solid #4A3A1E;
        border-radius: 14px;
        color: {WHITE};
        padding: 10px 18px;
        font-weight: 650;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {GOLD} !important;
        color: #050505 !important;
        border: 1px solid {GOLD_LIGHT};
    }}

    h1, h2, h3 {{
        color: {GOLD_LIGHT} !important;
    }}

    .insight-card {{
        background-color: {CARD};
        border: 1px solid #3A301F;
        border-radius: 20px;
        padding: 1.2rem;
        min-height: 150px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.3);
    }}

    .insight-title {{
        color: {GOLD_LIGHT};
        font-size: 1rem;
        font-weight: 750;
        margin-bottom: 0.5rem;
    }}

    .insight-body {{
        color: {WHITE};
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    .dataframe {{
        background-color: {CARD};
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("beauty_expansion_data.csv")
df.columns = df.columns.str.strip()

if "City" not in df.columns:
    st.error("Your CSV must include a column named 'City'.")
    st.stop()

df = df.dropna(subset=["City"])

required_cols = [
    "Estimated_Monthly_Rent",
    "Estimated_Monthly_Revenue",
    "Estimated_Monthly_Cost",
    "Premium_Fit_Score",
    "Beauty_Expansion_Score",
    "Beauty_Demand_Signal",
    "Competitive_Pressure",
    "Population"
]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns in CSV: {missing_cols}")
    st.stop()

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
logo_path = Path("logo.png")

if logo_path.exists():
    st.sidebar.image("logo.png", width=140)

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
# FILTER DATA
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

filtered["Non_Rent_Cost"] = (
    filtered["Estimated_Monthly_Cost"] - filtered["Estimated_Monthly_Rent"]
)

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
# PLOTLY THEME HELPER
# -----------------------------
def dark_layout(fig, height=500):
    fig.update_layout(
        paper_bgcolor=CHARCOAL,
        plot_bgcolor=CHARCOAL,
        font=dict(color=WHITE),
        height=height,
        margin=dict(l=40, r=30, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=WHITE)
        )
    )
    fig.update_xaxes(gridcolor="#2A2A2A", zerolinecolor="#333333")
    fig.update_yaxes(gridcolor="#2A2A2A", zerolinecolor="#333333")
    return fig

# -----------------------------
# HERO HEADER
# -----------------------------
logo_html = ""
if logo_path.exists():
    import base64
    with open("logo.png", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded}" style="width:88px; height:88px; object-fit:contain;">'

st.markdown(f"""
<div class="hero">
    <div class="hero-inner">
        <div>{logo_html}</div>
        <div>
            <div class="hero-title">STRATEGIC EXPANSION INTELLIGENCE PLATFORM</div>
            <div class="hero-subtitle">
                Market prioritization, ROI scenarios, and expansion recommendations.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# TOP KPIs
# -----------------------------
top_market = filtered.iloc[0]["City"]
avg_roi = filtered["Scenario_ROI"].mean()
total_profit = filtered["Scenario_Profit"].sum()
priority_count = (filtered["Recommendation"] == "Priority Expansion").sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Top Market", top_market)
k2.metric("Average ROI", f"{avg_roi:.1%}")
k3.metric("Scenario Profit", f"${total_profit:,.0f}")
k4.metric("Priority Markets", priority_count)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Market Ranking",
    "Financial Scenario",
    "Market Positioning",
    "Recommendation Engine",
    "Data Quality & Assumptions"
])

# -----------------------------
# TAB 1: OVERVIEW
# -----------------------------
with tab1:
    left, right = st.columns([1, 2])

    with left:
        st.markdown('<div class="section-title">Executive Snapshot</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-note">High-level view of the strongest expansion opportunities.</div>', unsafe_allow_html=True)

        top = filtered.iloc[0]
        second = filtered.iloc[1] if len(filtered) > 1 else top

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Top Recommended Market</div>
            <div class="insight-body">
                <b>{top["City"]}</b> currently ranks highest under the selected scenario.
                <br><br>
                Recommendation: <b>{top["Recommendation"]}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Second Strongest Market</div>
            <div class="insight-body">
                <b>{second["City"]}</b> is the next strongest market based on scenario-adjusted score.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">Expansion Score by Market</div>', unsafe_allow_html=True)

        fig = px.bar(
            filtered,
            x="City",
            y="Final_Scenario_Score",
            color="Recommendation",
            text="Final_Scenario_Score",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838", "#3E3E3E"]
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(dark_layout(fig, 520), use_container_width=True)

# -----------------------------
# TAB 2: MARKET RANKING
# -----------------------------
with tab2:
    st.markdown('<div class="section-title">Executive Market Ranking Table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Consolidated ranking based on demand, premium fit, competition, ROI, and final recommendation.</div>', unsafe_allow_html=True)

    ranking_cols = [
        "City",
        "Beauty_Demand_Signal",
        "Premium_Fit_Score",
        "Competitive_Pressure",
        "Beauty_Expansion_Score",
        "Scenario_ROI",
        "Scenario_Profit",
        "Final_Scenario_Score",
        "Recommendation"
    ]

    st.dataframe(filtered[ranking_cols], use_container_width=True, height=420)

# -----------------------------
# TAB 3: FINANCIAL SCENARIO
# -----------------------------
with tab3:
    colA, colB = st.columns(2)

    with colA:
        st.markdown('<div class="section-title">Revenue vs Cost</div>', unsafe_allow_html=True)

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
            color_discrete_sequence=[GOLD_LIGHT, "#8C6F2F"]
        )
        st.plotly_chart(dark_layout(fig2, 500), use_container_width=True)

    with colB:
        st.markdown('<div class="section-title">Scenario ROI</div>', unsafe_allow_html=True)

        fig3 = px.bar(
            filtered,
            x="City",
            y="Scenario_ROI",
            color="Recommendation",
            text="Scenario_ROI",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838", "#3E3E3E"]
        )
        fig3.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        st.plotly_chart(dark_layout(fig3, 500), use_container_width=True)

# -----------------------------
# TAB 4: MARKET POSITIONING
# -----------------------------
with tab4:
    colA, colB = st.columns(2)

    with colA:
        st.markdown('<div class="section-title">Demand vs Premium Fit</div>', unsafe_allow_html=True)

        fig4 = px.scatter(
            filtered,
            x="Beauty_Demand_Signal",
            y="Premium_Fit_Score",
            size="Population",
            color="Recommendation",
            hover_name="City",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838", "#3E3E3E"]
        )
        st.plotly_chart(dark_layout(fig4, 520), use_container_width=True)

    with colB:
        st.markdown('<div class="section-title">Competitive Pressure</div>', unsafe_allow_html=True)

        fig5 = px.bar(
            filtered,
            x="City",
            y="Competitive_Pressure",
            color="Recommendation",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838", "#3E3E3E"]
        )
        st.plotly_chart(dark_layout(fig5, 520), use_container_width=True)

# -----------------------------
# TAB 5: RECOMMENDATION ENGINE
# -----------------------------
with tab5:
    st.markdown('<div class="section-title">AI-Assisted Recommendation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Rules-based recommendation logic based on profit, ROI, and premium fit.</div>', unsafe_allow_html=True)

    rec_cols = [
        "City",
        "Scenario_Revenue",
        "Scenario_Cost",
        "Scenario_Profit",
        "Scenario_ROI",
        "Premium_Fit_Score",
        "Final_Scenario_Score",
        "Recommendation"
    ]

    st.dataframe(filtered[rec_cols], use_container_width=True, height=360)

    st.markdown("""
    ### Recommendation Logic

    - **Priority Expansion:** positive profit and ROI equal to or above 15%.
    - **Validate Further:** positive profit but ROI below 15%.
    - **Premium Strategy:** strong premium fit but negative profit.
    - **High Risk:** weak financial viability under current assumptions.
    """)

# -----------------------------
# TAB 6: DATA QUALITY & ASSUMPTIONS
# -----------------------------
with tab6:
    st.markdown('<div class="section-title">Data Quality & Assumptions</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Current Data Sources</div>
            <div class="insight-body">
                Census demographic data, competitive market data, rent assumptions, and operating assumptions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Current Limitations</div>
            <div class="insight-body">
                Market-level data should be validated with ZIP-level, trade-area, lease, and internal performance data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Next Improvement</div>
            <div class="insight-body">
                Connect the dashboard to Google Sheets or external data sources for continuous updates.
            </div>
        </div>
        """, unsafe_allow_html=True)

    top = filtered.iloc[0]

    st.markdown("### Auto-Generated Executive Summary")
    st.markdown(f"""
    **Top recommended market:** {top["City"]}

    Under the selected scenario, **{top["City"]}** ranks as the strongest expansion opportunity with a final scenario score of **{top["Final_Scenario_Score"]:.1f}**.

    **Scenario assumptions:**
    - Rent change: **{rent_change}%**
    - Revenue / ticket change: **{ticket_change}%**
    - Customer volume change: **{customer_change}%**

    **Model recommendation:** **{top["Recommendation"]}**
    """)
