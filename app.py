import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import requests
import matplotlib.pyplot as plt

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER

st.set_page_config(
    page_title="Strategic Expansion Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

GOLD = "#C6A052"
GOLD_LIGHT = "#E8D28A"

logo_path = Path("logo.png")

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, #F7F3EA 0%, #FFFFFF 45%, #EFE6D1 100%);
        color: #111111;
    }}

    .block-container {{
        padding-top: 5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1450px;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #F7F1E4 0%, #EFE2BD 100%);
        border-right: 1px solid #D8C28A;
    }}

    section[data-testid="stSidebar"] * {{
        color: #111111 !important;
    }}

    .hero-title {{
        font-size: 2.5rem;
        font-weight: 900;
        color: #111111;
        letter-spacing: -1px;
        line-height: 1.1;
    }}

    .hero-subtitle {{
        margin-top: 0.4rem;
        font-size: 1.05rem;
        color: #7A6330;
        font-weight: 500;
    }}

    div[data-testid="stMetric"] {{
        background: rgba(255,255,255,0.92);
        border: 1px solid #E5D6AF;
        border-radius: 22px;
        padding: 0.8rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #6F5725 !important;
        font-weight: 650;
        font-size: 0.82rem !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: #111111 !important;
        font-weight: 750;
        font-size: 1.55rem !important;
        line-height: 1.05 !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        margin-bottom: 1rem;
        border-bottom: 1px solid #E6D8B6;
        padding-bottom: 0.8rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #FFFFFF;
        border: 1px solid #E5D6AF;
        border-radius: 14px;
        color: #111111;
        padding: 10px 18px;
        font-weight: 650;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #C6A052 0%, #E8D28A 100%) !important;
        color: #080808 !important;
        border: 1px solid #C6A052;
    }}

    h1, h2, h3 {{
        color: #1A1A1A !important;
    }}

    .section-title {{
        color: #8A6A24;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }}

    .section-note {{
        color: #6F6A60;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }}

    .insight-card {{
        background: rgba(255,255,255,0.95);
        border: 1px solid #E5D6AF;
        border-radius: 22px;
        padding: 1.3rem;
        min-height: 150px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.07);
    }}

    .insight-title {{
        color: #8A6A24;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }}

    .insight-body {{
        color: #171717;
        font-size: 0.95rem;
        line-height: 1.55;
    }}

    /* MULTISELECT TAGS */
    span[data-baseweb="tag"] {{
        background-color: #C6A052 !important;
        border-radius: 10px !important;
        border: none !important;
    }}

    span[data-baseweb="tag"] * {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}

    /* MULTISELECT INPUT BOX */
    div[data-baseweb="select"] > div {{
        border-radius: 14px !important;
        border: 1px solid #D8C28A !important;
        background-color: rgba(255,255,255,0.72) !important;
    }}

    /* SLIDER THUMB */
    .stSlider div[role="slider"] {{
        background-color: #C6A052 !important;
        border: 2px solid #B8923D !important;
        box-shadow: 0 2px 8px rgba(198,160,82,0.35) !important;
    }}

    /* SLIDER ACTIVE TRACK */
    .stSlider [data-baseweb="slider"] [data-testid="stTickBar"] + div {{
        background-color: #C6A052 !important;
    }}

    /* SLIDER GENERAL ACCENT */
    .stSlider div[data-baseweb="slider"] div {{
        color: #8A6A24 !important;
    }}
</style>
""", unsafe_allow_html=True)

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRlzu0foii8Px9Kajtdoa84Cy3rYy9VdCG3tBa-Hwt7rmisBrXF_x8dYdrn2RgHIhimS0YJNQFAoZVD/pub?gid=0&single=true&output=csv"
COMPETITORS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRlzu0foii8Px9Kajtdoa84Cy3rYy9VdCG3tBa-Hwt7rmisBrXF_x8dYdrn2RgHIhimS0YJNQFAoZVD/pub?gid=324687326&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error("Could not load Google Sheet. Make sure it is published to the web as CSV.")
        st.write("Current URL:", url)
        st.write("Error:", e)
        st.stop()

df = load_data(GOOGLE_SHEET_CSV_URL)
competitors_df = load_data(COMPETITORS_CSV_URL)
competitors_df.columns = competitors_df.columns.str.strip()
competitors_df["city"] = competitors_df["city"].astype(str).str.strip()
competitors_df["totalScore"] = pd.to_numeric(competitors_df["totalScore"], errors="coerce")
competitors_df["reviewsCount"] = pd.to_numeric(competitors_df["reviewsCount"], errors="coerce").fillna(0)
df.columns = df.columns.str.strip()

if "City" not in df.columns:
    st.error("Your CSV must include a column named 'City'.")
    st.stop()

df = df.dropna(subset=["City"])

required_cols = [
    "City",
    "State",
    "Estimated_Monthly_Rent",
    "Estimated_Monthly_Revenue",
    "Estimated_Monthly_Cost"
]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns in CSV: {missing_cols}")
    st.stop()

STATE_FIPS = {
    "FL": "12",
    "TX": "48",
    "GA": "13",
    "NC": "37",
    "TN": "47",
    "AZ": "04",
    "CA": "06",
    "NY": "36",
    "IL": "17"
}

# -----------------------------
# CITY COORDINATES
# -----------------------------
CITY_COORDS = {
    "Miami": (25.7617, -80.1918),
    "Orlando": (28.5383, -81.3792),
    "Tampa": (27.9506, -82.4572),
    "Coral Gables": (25.7215, -80.2684),
    "Doral": (25.8195, -80.3553),
    "Aventura": (25.9565, -80.1392),
    "Sunny Isles Beach": (25.9429, -80.1234),
    "Fort Lauderdale": (26.1224, -80.1373),
    "Dallas": (32.7767, -96.7970),
    "Houston": (29.7604, -95.3698),
    "Atlanta": (33.7490, -84.3880),
    "Charlotte": (35.2271, -80.8431),
    "Nashville": (36.1627, -86.7816),
    "Phoenix": (33.4484, -112.0740),
    "Los Angeles": (34.0522, -118.2437),
    "New York": (40.7128, -74.0060),
    "Chicago": (41.8781, -87.6298)
}

@st.cache_data(ttl=86400)
def get_census_place_data(year=2022):
    url = f"https://api.census.gov/data/{year}/acs/acs5"

    params = {
        "get": "NAME,B01003_001E,B19013_001E",
        "for": "place:*",
        "in": "state:*"
    }

    empty_census = pd.DataFrame(
        columns=["Census_Name", "Population", "Median_Income", "State_FIPS"]
    )

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            return empty_census

        data = response.json()

        cols = data[0]
        rows = data[1:]

        census_df = pd.DataFrame(rows, columns=cols)

        census_df = census_df.rename(columns={
            "NAME": "Census_Name",
            "B01003_001E": "Population",
            "B19013_001E": "Median_Income",
            "state": "State_FIPS"
        })

        census_df["Population"] = pd.to_numeric(census_df["Population"], errors="coerce")
        census_df["Median_Income"] = pd.to_numeric(census_df["Median_Income"], errors="coerce")

        return census_df

    except Exception:
        return empty_census


def normalize_city_name(city):
    city = str(city).lower().strip()

    city = city.replace(".", "")
    city = city.replace("-", " ")
    city = " ".join(city.split())

    return city


def extract_city_from_census_name(name):
    city = str(name).split(",")[0].lower()

    replacements = [
        " city",
        " town",
        " village",
        " municipality",
        " borough",
        " census designated place"
    ]

    for r in replacements:
        city = city.replace(r, "")

    city = city.strip()

    return city


census_df = get_census_place_data()

census_df["City_Key"] = census_df["Census_Name"].apply(extract_city_from_census_name)
df["City_Key"] = df["City"].apply(normalize_city_name)
df["State_FIPS"] = df["State"].map(STATE_FIPS)

df = df.merge(
    census_df[["City_Key", "State_FIPS", "Population", "Median_Income"]],
    on=["City_Key", "State_FIPS"],
    how="left"
)
st.write(df[["City", "Population", "Median_Income"]].head(20))

df = df.drop(columns=["City_Key", "State_FIPS"])

st.sidebar.markdown("## Scenario Controls")
st.sidebar.markdown("Adjust assumptions to test expansion scenarios.")

selected_city = st.sidebar.selectbox(
    "Select Market",
    options=sorted(df["City"].unique())
)

rent_change = st.sidebar.slider("Rent Change (%)", -30, 50, 0, 5)
ticket_change = st.sidebar.slider("Revenue / Average Ticket Change (%)", -30, 50, 0, 5)
customer_change = st.sidebar.slider("Customer Volume Change (%)", -30, 50, 0, 5)

filtered = df[df["City"] == selected_city].copy()
city_competitors = competitors_df[
    competitors_df["city"].str.lower() == selected_city.lower()
].copy()

competitor_count = len(city_competitors)

avg_rating = city_competitors["totalScore"].mean()

total_reviews = city_competitors["reviewsCount"].sum()

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

# -----------------------------
# AUTO SCORES FOR SELECTED MARKET
# -----------------------------
def normalize_selected(value, series):
    min_value = series.min()
    max_value = series.max()
    if pd.isna(value) or pd.isna(min_value) or pd.isna(max_value) or max_value == min_value:
        return 0
    return max(0, min(100, ((value - min_value) / (max_value - min_value)) * 100))

selected_population_score = normalize_selected(
    filtered.iloc[0]["Population"],
    df["Population"]
)

selected_income_score = normalize_selected(
    filtered.iloc[0]["Median_Income"],
    df["Median_Income"]
)

selected_roi_score = max(0, min(100, filtered.iloc[0]["Scenario_ROI"] * 100))

selected_review_score = normalize_selected(
    total_reviews,
    competitors_df.groupby(competitors_df["city"].str.lower())["reviewsCount"].sum()
)

selected_saturation_score = normalize_selected(
    competitor_count,
    competitors_df.groupby(competitors_df["city"].str.lower()).size()
)

filtered["Premium_Fit_Score"] = (
    selected_income_score * 0.70
    + selected_population_score * 0.30
)

filtered["Beauty_Demand_Signal"] = (
    selected_review_score * 0.60
    + (avg_rating * 20 if pd.notna(avg_rating) else 0) * 0.40
)

filtered["Competitive_Pressure"] = selected_saturation_score

filtered["Beauty_Expansion_Score"] = (
    filtered["Premium_Fit_Score"] * 0.35
    + filtered["Beauty_Demand_Signal"] * 0.35
    + selected_roi_score * 0.30
)
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
# OPPORTUNITY SCORING ENGINE
# -----------------------------
def normalize_score(value, min_value, max_value):
    if pd.isna(value) or max_value == min_value:
        return 0
    score = ((value - min_value) / (max_value - min_value)) * 100
    return max(0, min(100, score))


population_value = filtered.iloc[0]["Population"]
income_value = filtered.iloc[0]["Median_Income"]
roi_value = filtered.iloc[0]["Scenario_ROI"]
manual_demand_value = filtered.iloc[0]["Beauty_Demand_Signal"]
premium_fit_value = filtered.iloc[0]["Premium_Fit_Score"]

population_score = normalize_score(
    population_value,
    df["Population"].min(),
    df["Population"].max()
)

income_score = normalize_score(
    income_value,
    df["Median_Income"].min(),
    df["Median_Income"].max()
)

roi_score = max(0, min(100, roi_value * 100))

review_score = normalize_score(
    total_reviews,
    0,
    competitors_df.groupby(competitors_df["city"].str.lower())["reviewsCount"].sum().max()
)

saturation_score = normalize_score(
    competitor_count,
    0,
    competitors_df.groupby(competitors_df["city"].str.lower()).size().max()
)

market_attractiveness_score = (
    population_score * 0.35
    + income_score * 0.35
    + manual_demand_value * 0.30
)

financial_viability_score = (
    roi_score * 0.60
    + premium_fit_value * 0.40
)

competitive_market_score = (
    review_score * 0.60
    + avg_rating * 20 * 0.40
)

final_opportunity_score = (
    market_attractiveness_score * 0.35
    + financial_viability_score * 0.35
    + competitive_market_score * 0.20
    - saturation_score * 0.10
)

final_opportunity_score = max(0, min(100, final_opportunity_score))

if final_opportunity_score >= 80:
    opportunity_recommendation = "High-Priority Expansion Opportunity"
elif final_opportunity_score >= 65:
    opportunity_recommendation = "Strong Opportunity — Validate with Local Real Estate"
elif final_opportunity_score >= 50:
    opportunity_recommendation = "Moderate Opportunity — Requires Further Validation"
else:
    opportunity_recommendation = "Lower Priority Under Current Assumptions"

# -----------------------------
# DECISION READINESS ENGINE
# -----------------------------
data_completeness_score = 0

if pd.notna(population_value):
    data_completeness_score += 20
if pd.notna(income_value):
    data_completeness_score += 20
if competitor_count > 0:
    data_completeness_score += 20
if total_reviews > 0:
    data_completeness_score += 20
if pd.notna(roi_value):
    data_completeness_score += 20

risk_flags = []

if competitor_count >= 100:
    risk_flags.append("High competitive saturation")

if roi_value < 0.15:
    risk_flags.append("ROI below priority threshold")

if pd.isna(population_value) or pd.isna(income_value):
    risk_flags.append("Incomplete Census match")

if total_reviews < 3000:
    risk_flags.append("Limited review volume")

if final_opportunity_score < 65:
    risk_flags.append("Opportunity score requires validation")

if data_completeness_score >= 80 and len(risk_flags) <= 1:
    decision_readiness = "Leadership Ready"
elif data_completeness_score >= 60:
    decision_readiness = "Requires Validation"
else:
    decision_readiness = "Not Ready for Decision"
    
# -----------------------------
# ALL MARKETS COMPARISON ENGINE
# -----------------------------
competitor_summary = competitors_df.copy()
competitor_summary["city_key"] = competitor_summary["city"].str.lower()

market_competitors = competitor_summary.groupby("city_key").agg(
    Competitor_Count=("title", "count"),
    Avg_Rating=("totalScore", "mean"),
    Total_Reviews=("reviewsCount", "sum")
).reset_index()

comparison_df = df.copy()
comparison_df["city_key"] = comparison_df["City"].str.lower()

comparison_df = comparison_df.merge(
    market_competitors,
    on="city_key",
    how="left"
)

comparison_df["Competitor_Count"] = comparison_df["Competitor_Count"].fillna(0)
comparison_df["Avg_Rating"] = comparison_df["Avg_Rating"].fillna(0)
comparison_df["Total_Reviews"] = comparison_df["Total_Reviews"].fillna(0)

comparison_df["Scenario_Rent"] = comparison_df["Estimated_Monthly_Rent"] * (1 + rent_change / 100)

comparison_df["Scenario_Revenue"] = (
    comparison_df["Estimated_Monthly_Revenue"]
    * (1 + ticket_change / 100)
    * (1 + customer_change / 100)
)

comparison_df["Non_Rent_Cost"] = (
    comparison_df["Estimated_Monthly_Cost"] - comparison_df["Estimated_Monthly_Rent"]
)

comparison_df["Scenario_Cost"] = comparison_df["Non_Rent_Cost"] + comparison_df["Scenario_Rent"]
comparison_df["Scenario_Profit"] = comparison_df["Scenario_Revenue"] - comparison_df["Scenario_Cost"]
comparison_df["Scenario_ROI"] = comparison_df["Scenario_Profit"] / comparison_df["Scenario_Cost"]

def safe_normalize(series):
    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or max_value == min_value:
        return pd.Series([0] * len(series), index=series.index)
    return ((series - min_value) / (max_value - min_value) * 100).clip(0, 100)

comparison_df["Population_Score"] = safe_normalize(comparison_df["Population"])
comparison_df["Income_Score"] = safe_normalize(comparison_df["Median_Income"])
comparison_df["Review_Score"] = safe_normalize(comparison_df["Total_Reviews"])
comparison_df["Saturation_Score"] = safe_normalize(comparison_df["Competitor_Count"])
comparison_df["ROI_Score"] = (comparison_df["Scenario_ROI"] * 100).clip(0, 100)

# -----------------------------
# AUTO-GENERATED STRATEGIC SCORES
# -----------------------------

# Population & income normalization
comparison_df["Population_Score"] = safe_normalize(comparison_df["Population"])
comparison_df["Income_Score"] = safe_normalize(comparison_df["Median_Income"])

# Competitive signals
comparison_df["Review_Score"] = safe_normalize(comparison_df["Total_Reviews"])
comparison_df["Saturation_Score"] = safe_normalize(comparison_df["Competitor_Count"])

# Premium fit
comparison_df["Premium_Fit_Score"] = (
    comparison_df["Income_Score"] * 0.70
    + comparison_df["Population_Score"] * 0.30
).clip(0, 100)

# Beauty demand signal
comparison_df["Beauty_Demand_Signal"] = (
    comparison_df["Review_Score"] * 0.60
    + (comparison_df["Avg_Rating"] * 20) * 0.40
).clip(0, 100)

# Competitive pressure
comparison_df["Competitive_Pressure"] = (
    comparison_df["Saturation_Score"]
).clip(0, 100)

# Strategic expansion score
comparison_df["Beauty_Expansion_Score"] = (
    comparison_df["Premium_Fit_Score"] * 0.35
    + comparison_df["Beauty_Demand_Signal"] * 0.35
    + comparison_df["ROI_Score"] * 0.30
).clip(0, 100)

comparison_df["Market_Attractiveness_Score"] = (
    comparison_df["Population_Score"] * 0.35
    + comparison_df["Income_Score"] * 0.35
    + comparison_df["Beauty_Demand_Signal"] * 0.30
)

comparison_df["Financial_Viability_Score"] = (
    comparison_df["ROI_Score"] * 0.60
    + comparison_df["Premium_Fit_Score"] * 0.40
)

comparison_df["Competitive_Market_Signal"] = (
    comparison_df["Review_Score"] * 0.60
    + comparison_df["Avg_Rating"].fillna(0) * 20 * 0.40
)

comparison_df["Final_Opportunity_Score"] = (
    comparison_df["Market_Attractiveness_Score"] * 0.35
    + comparison_df["Financial_Viability_Score"] * 0.35
    + comparison_df["Competitive_Market_Signal"] * 0.20
    - comparison_df["Saturation_Score"] * 0.10
).clip(0, 100)

def opportunity_label(score):
    if score >= 80:
        return "High Priority"
    elif score >= 65:
        return "Strong Opportunity"
    elif score >= 50:
        return "Validate Further"
    else:
        return "Lower Priority"

comparison_df["Opportunity_Label"] = comparison_df["Final_Opportunity_Score"].apply(opportunity_label)

comparison_df = comparison_df.sort_values("Final_Opportunity_Score", ascending=False)

comparison_df["Latitude"] = comparison_df["City"].map(
    lambda x: CITY_COORDS.get(x, (None, None))[0]
)

comparison_df["Longitude"] = comparison_df["City"].map(
    lambda x: CITY_COORDS.get(x, (None, None))[1]
)

map_df = comparison_df.dropna(subset=["Latitude", "Longitude"]).copy()

def chart_layout(fig, height=500):
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.92)",
        plot_bgcolor="rgba(255,255,255,0.92)",
        font=dict(color="#111111"),
        height=height,
        margin=dict(l=40, r=30, t=60, b=40),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#111111")
        )
    )
    fig.update_xaxes(gridcolor="#EEE6D3", zerolinecolor="#D8C896")
    fig.update_yaxes(gridcolor="#EEE6D3", zerolinecolor="#D8C896")
    return fig

def generate_executive_pdf():
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#8A6A24"),
        alignment=TA_CENTER,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["BodyText"],
        fontSize=10,
        textColor=colors.HexColor("#6F5725"),
        alignment=TA_CENTER,
        spaceAfter=18
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#8A6A24"),
        spaceBefore=16,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#222222")
    )

    elements = []

    elements.append(Paragraph("Strategic Expansion Intelligence Report", title_style))
    elements.append(Paragraph(f"{selected_city} Market Analysis & Expansion Recommendation", subtitle_style))

    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#C6A052")
    ))

    elements.append(Spacer(1, 16))

    kpi_data = [
        ["Metric", "Value"],
        ["Selected Market", selected_city],
        ["Population", f"{population:,.0f}" if pd.notna(population) else "Not found"],
        ["Median Income", f"${median_income:,.0f}" if pd.notna(median_income) else "Not found"],
        ["Scenario ROI", f"{avg_roi:.1%}"],
        ["Average Competitor Rating", f"{avg_rating:.2f}" if pd.notna(avg_rating) else "Not found"],
        ["Competitor Count", f"{competitor_count:,}"],
        ["Total Reviews", f"{int(total_reviews):,}"],
        ["Opportunity Score", f"{final_opportunity_score:.1f}/100"],
        ["Recommendation", opportunity_recommendation],
    ]

    table = Table(kpi_data, colWidths=[210, 300])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C6A052")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FAF7F0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8C28A")),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Executive Summary", section_style))

    summary_text = f"""
    Under the selected scenario assumptions, <b>{selected_city}</b> demonstrates an opportunity score of
    <b>{final_opportunity_score:.1f}/100</b>. The market presents a population of
    <b>{population:,.0f}</b> and a median household income of <b>${median_income:,.0f}</b>.
    Competitive analysis identified <b>{competitor_count:,}</b> competitors, with a combined review volume of
    <b>{int(total_reviews):,}</b> and an average customer rating of <b>{avg_rating:.2f}</b>.
    Based on demographic attractiveness, financial viability, and competitive market signals, the current recommendation is:
    <b>{opportunity_recommendation}</b>.
    """

    elements.append(Paragraph(summary_text, body_style))

    elements.append(Paragraph("Scenario Assumptions", section_style))

    assumptions = f"""
    Rent adjustment: <b>{rent_change}%</b><br/>
    Revenue / ticket adjustment: <b>{ticket_change}%</b><br/>
    Customer volume adjustment: <b>{customer_change}%</b>
    """

    elements.append(Paragraph(assumptions, body_style))

    elements.append(Paragraph("Recommended Next Actions", section_style))

    next_actions = """
    1. Validate lease economics and available locations in the selected trade area.<br/>
    2. Compare top competitors by service offering, pricing, reviews, and digital presence.<br/>
    3. Refine revenue assumptions using average ticket, expected customer volume, and service mix.<br/>
    4. Move from city-level analysis to ZIP-code or neighborhood-level validation before final site selection.
    """

    elements.append(Paragraph(next_actions, body_style))

    elements.append(Spacer(1, 18))

    footer = '<font size="8" color="#777777">Generated by Strategic Expansion Intelligence Platform</font>'
    elements.append(Paragraph(footer, body_style))

    # --------------------------
    # CHARTS WITHOUT KALEIDO
    # --------------------------

    elements.append(Paragraph("Opportunity Score Breakdown", section_style))

    score_data_pdf = score_data.copy()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(score_data_pdf["Score Component"], score_data_pdf["Score"])
    ax.set_ylabel("Score")
    ax.set_ylim(0, 110)
    ax.set_title("Opportunity Score Breakdown")
    ax.tick_params(axis="x", rotation=25)

    for i, value in enumerate(score_data_pdf["Score"]):
        ax.text(i, value + 2, f"{value:.1f}", ha="center", fontsize=8)

    plt.tight_layout()

    score_img = BytesIO()
    fig.savefig(score_img, format="png", dpi=200)
    plt.close(fig)
    score_img.seek(0)

    elements.append(Image(score_img, width=500, height=280))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Revenue vs Cost Scenario", section_style))

    revenue_cost_pdf = filtered.melt(
        id_vars="City",
        value_vars=["Scenario_Revenue", "Scenario_Cost"],
        var_name="Metric",
        value_name="Amount"
    )

    fig, ax = plt.subplots(figsize=(7, 4))

    metrics = revenue_cost_pdf["Metric"].tolist()
    amounts = revenue_cost_pdf["Amount"].tolist()

    ax.bar(metrics, amounts)
    ax.set_ylabel("Amount ($)")
    ax.set_title("Revenue vs Cost Scenario")

    for i, value in enumerate(amounts):
        ax.text(i, value, f"${value:,.0f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()

    financial_img = BytesIO()
    fig.savefig(financial_img, format="png", dpi=200)
    plt.close(fig)
    financial_img.seek(0)

    elements.append(Image(financial_img, width=500, height=280))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("All Markets Opportunity Ranking", section_style))

    ranking_pdf = comparison_df.head(10).copy()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(ranking_pdf["City"], ranking_pdf["Final_Opportunity_Score"])
    ax.set_ylabel("Opportunity Score")
    ax.set_ylim(0, 110)
    ax.set_title("All Markets Opportunity Ranking")
    ax.tick_params(axis="x", rotation=25)

    for i, value in enumerate(ranking_pdf["Final_Opportunity_Score"]):
        ax.text(i, value + 2, f"{value:.1f}", ha="center", fontsize=8)

    plt.tight_layout()

    ranking_img = BytesIO()
    fig.savefig(ranking_img, format="png", dpi=200)
    plt.close(fig)
    ranking_img.seek(0)

    elements.append(Image(ranking_img, width=500, height=280))
    elements.append(Spacer(1, 18))

    doc.build(elements)
    buffer.seek(0)

    return buffer

# -----------------------------
# CLEAN HEADER — NO RECTANGLE
# -----------------------------
header_col1, header_col2 = st.columns([1, 9])

with header_col1:
    if logo_path.exists():
        st.image("logo.png", width=95)

with header_col2:
    st.markdown("""
    <div class="hero-title">
        STRATEGIC EXPANSION INTELLIGENCE PLATFORM
    </div>
    <div class="hero-subtitle">
        Market prioritization, ROI scenarios, and expansion recommendations.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

top_market = filtered.iloc[0]["City"]
population = filtered.iloc[0]["Population"]
median_income = filtered.iloc[0]["Median_Income"]
avg_roi = filtered["Scenario_ROI"].mean()
total_profit = filtered["Scenario_Profit"].sum()

k1, k2, k3, k4, k5, k6, k7, k8, k9 = st.columns(9)
k1.metric("Selected Market", top_market)
k2.metric("Population", f"{population:,.0f}" if pd.notna(population) else "Not found")
k3.metric("Median Income", f"${median_income:,.0f}" if pd.notna(median_income) else "Not found")
k4.metric("Scenario ROI", f"{avg_roi:.1%}")
k5.metric("Avg Rating", f"{avg_rating:.2f}")
k6.metric("Competitors", f"{competitor_count:,}")
k7.metric("Total Reviews", f"{int(total_reviews):,}")
k8.metric("Opportunity Score", f"{final_opportunity_score:.1f}")
k9.metric("Decision Status", decision_readiness)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "Overview",
    "Market Ranking",
    "Financial Scenario",
    "Market Positioning",
    "Competitive Intelligence",
    "Opportunity Scoring",
    "All Markets Comparison",
    "Executive Narrative",
    "Recommendation Engine",
    "Geo Intelligence",
    "Data Quality & Assumptions"
])

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
        st.plotly_chart(chart_layout(fig, 520), use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">Executive Market Ranking Table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Consolidated ranking based on demand, premium fit, competition, ROI, and final recommendation.</div>', unsafe_allow_html=True)

    ranking_cols = [
        "City",
        "Population",
        "Median_Income",
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
        st.plotly_chart(chart_layout(fig2, 500), use_container_width=True)

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
        st.plotly_chart(chart_layout(fig3, 500), use_container_width=True)

with tab4:

    colA, colB = st.columns(2)

    with colA:

        st.markdown(
            '<div class="section-title">Market Attractiveness Matrix</div>',
            unsafe_allow_html=True
        )

        fig4 = px.scatter(
            comparison_df,
            x="Median_Income",
            y="Population",
            size="Final_Opportunity_Score",
            color="Opportunity_Label",
            hover_name="City",
            hover_data={
                "Scenario_ROI": ":.1%",
                "Competitor_Count": True,
                "Total_Reviews": True
            },
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838"
            ]
        )

        fig4.update_layout(
            xaxis_title="Median Household Income",
            yaxis_title="Population"
        )

        st.plotly_chart(
            chart_layout(fig4, 520),
            use_container_width=True
        )

    with colB:

        st.markdown(
            '<div class="section-title">Competitive Saturation</div>',
            unsafe_allow_html=True
        )

        fig5 = px.bar(
            comparison_df.sort_values(
                "Competitor_Count",
                ascending=False
            ),
            x="City",
            y="Competitor_Count",
            color="Opportunity_Label",
            text="Competitor_Count",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838"
            ]
        )

        fig5.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig5, 520),
            use_container_width=True
        )

with tab5:
    st.markdown('<div class="section-title">Competitive Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">External market intelligence based on competitor listings, ratings, and review volume.</div>',
        unsafe_allow_html=True
    )

    if city_competitors.empty:
        st.warning(f"No competitor data found for {selected_city}.")
    else:
        top_competitors = city_competitors.sort_values("reviewsCount", ascending=False).head(10)

        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown('<div class="section-title">Top Competitors by Reviews</div>', unsafe_allow_html=True)

            fig_comp = px.bar(
                top_competitors,
                x="reviewsCount",
                y="title",
                orientation="h",
                color="totalScore",
                color_continuous_scale=["#EFE2BD", "#C6A052", "#7D6838"],
                text="reviewsCount"
            )

            fig_comp.update_layout(
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False
            )

            st.plotly_chart(chart_layout(fig_comp, 520), use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">Rating Distribution</div>', unsafe_allow_html=True)

            fig_rating = px.histogram(
                city_competitors,
                x="totalScore",
                nbins=10,
                color_discrete_sequence=[GOLD]
            )

            st.plotly_chart(chart_layout(fig_rating, 520), use_container_width=True)

        st.markdown('<div class="section-title">Market Insight</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{selected_city} Competitive Landscape</div>
            <div class="insight-body">
                {selected_city} currently shows <b>{competitor_count:,}</b> identified competitors,
                an average rating of <b>{avg_rating:.2f}</b>, and a total review volume of
                <b>{int(total_reviews):,}</b>.
                <br><br>
                High review volume suggests strong customer activity and beauty-service demand,
                while a large competitor base may indicate higher market saturation.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Competitor Detail Table</div>', unsafe_allow_html=True)

        competitor_cols = [
            "title",
            "totalScore",
            "reviewsCount",
            "street",
            "city",
            "state",
            "categoryName",
            "website",
            "url"
        ]

        available_cols = [col for col in competitor_cols if col in city_competitors.columns]

        st.dataframe(
            city_competitors[available_cols].sort_values("reviewsCount", ascending=False),
            use_container_width=True,
            height=420
        )

with tab6:
    st.markdown('<div class="section-title">Opportunity Scoring Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Composite scoring model combining demographics, financial viability, customer activity, and competitive saturation.</div>',
        unsafe_allow_html=True
    )

    score_data = pd.DataFrame({
        "Score Component": [
            "Market Attractiveness",
            "Financial Viability",
            "Competitive Market Signal",
            "Competitive Saturation Penalty",
            "Final Opportunity Score"
        ],
        "Score": [
            market_attractiveness_score,
            financial_viability_score,
            competitive_market_score,
            saturation_score,
            final_opportunity_score
        ]
    })

    fig_score = px.bar(
        score_data,
        x="Score Component",
        y="Score",
        text="Score",
        color="Score Component",
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#D8C28A", "#7D6838"]
    )
    fig_score.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_score.update_layout(showlegend=False)

    st.plotly_chart(chart_layout(fig_score, 520), use_container_width=True)

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">{selected_city} Opportunity Recommendation</div>
        <div class="insight-body">
            <b>Final Opportunity Score:</b> {final_opportunity_score:.1f}/100
            <br><br>
            <b>Recommendation:</b> {opportunity_recommendation}
            <br><br>
            This score combines Census demographics, income strength, financial scenario performance,
            competitor review volume, average rating, and competitive saturation.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
with tab7:
    st.markdown('<div class="section-title">All Markets Comparison</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Compares all markets using the same opportunity scoring logic under the selected scenario assumptions.</div>',
        unsafe_allow_html=True
    )

    best_market = comparison_df.iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Best Ranked Market</div>
            <div class="insight-body">
                <b>{best_market["City"]}</b>
                <br><br>
                Opportunity Score: <b>{best_market["Final_Opportunity_Score"]:.1f}/100</b>
                <br>
                Recommendation: <b>{best_market["Opportunity_Label"]}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        top_3 = ", ".join(comparison_df.head(3)["City"].tolist())
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Top 3 Markets</div>
            <div class="insight-body">
                {top_3}
                <br><br>
                These markets currently show the strongest combined demographic, financial, and competitive signals.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Scenario Applied</div>
            <div class="insight-body">
                Rent change: <b>{rent_change}%</b>
                <br>
                Revenue / ticket change: <b>{ticket_change}%</b>
                <br>
                Customer volume change: <b>{customer_change}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig_all = px.bar(
        comparison_df,
        x="City",
        y="Final_Opportunity_Score",
        color="Opportunity_Label",
        text="Final_Opportunity_Score",
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#D8C28A"]
    )
    fig_all.update_traces(texttemplate="%{text:.1f}", textposition="outside")

    st.plotly_chart(chart_layout(fig_all, 560), use_container_width=True)

    st.markdown('<div class="section-title">Market Comparison Table</div>', unsafe_allow_html=True)

    comparison_cols = [
        "City",
        "Population",
        "Median_Income",
        "Competitor_Count",
        "Avg_Rating",
        "Total_Reviews",
        "Scenario_ROI",
        "Scenario_Profit",
        "Market_Attractiveness_Score",
        "Financial_Viability_Score",
        "Competitive_Market_Signal",
        "Saturation_Score",
        "Final_Opportunity_Score",
        "Opportunity_Label"
    ]

    st.dataframe(
        comparison_df[comparison_cols],
        use_container_width=True,
        height=480
    )
    
with tab8:
    st.markdown('<div class="section-title">Executive Narrative</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Auto-generated strategic interpretation based on demographics, financial scenario, competitor intelligence, and opportunity scoring.</div>',
        unsafe_allow_html=True
    )

    selected_market = filtered.iloc[0]

    if final_opportunity_score >= 80:
        strategic_tone = "high-priority expansion candidate"
    elif final_opportunity_score >= 65:
        strategic_tone = "strong expansion candidate that should be validated further"
    elif final_opportunity_score >= 50:
        strategic_tone = "moderate opportunity requiring additional due diligence"
    else:
        strategic_tone = "lower-priority market under the current assumptions"

    if competitor_count >= 100:
        competition_interpretation = "The market shows elevated competitive saturation, which indicates strong category activity but also requires clear differentiation."
    elif competitor_count >= 40:
        competition_interpretation = "The market shows moderate competitive intensity, suggesting room for expansion if positioning and site selection are strong."
    else:
        competition_interpretation = "The market shows relatively limited visible competition, which may indicate whitespace opportunity or the need to validate demand more deeply."

    if total_reviews >= 10000:
        review_interpretation = "High review volume suggests strong customer engagement and active beauty-service demand."
    elif total_reviews >= 3000:
        review_interpretation = "Moderate review volume suggests meaningful customer activity, though additional local validation is recommended."
    else:
        review_interpretation = "Lower review volume suggests that demand should be validated through neighborhood-level research, search trends, and local customer data."

    if avg_roi >= 0.15:
        financial_interpretation = "The current scenario shows attractive financial viability, with ROI meeting or exceeding the priority threshold."
    elif avg_roi > 0:
        financial_interpretation = "The current scenario shows positive financial potential, but ROI remains below the priority threshold."
    else:
        financial_interpretation = "The current scenario shows financial pressure, meaning pricing, cost structure, location size, or customer volume assumptions may need adjustment."

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Summary</div>
        <div class="insight-body">
            <b>{selected_city}</b> is currently assessed as a <b>{strategic_tone}</b>, with a final opportunity score of
            <b>{final_opportunity_score:.1f}/100</b>.
            <br><br>
            The market combines demographic indicators, financial scenario performance, and external competitor intelligence to support expansion decision-making.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    n1, n2 = st.columns(2)

    with n1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Market Strengths</div>
            <div class="insight-body">
                Population: <b>{population:,.0f}</b><br>
                Median income: <b>${median_income:,.0f}</b><br>
                Average competitor rating: <b>{avg_rating:.2f}</b><br>
                Total review volume: <b>{int(total_reviews):,}</b>
                <br><br>
                {review_interpretation}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with n2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Risk Interpretation</div>
            <div class="insight-body">
                Identified competitors: <b>{competitor_count:,}</b><br>
                Scenario ROI: <b>{avg_roi:.1%}</b><br>
                Scenario profit: <b>${total_profit:,.0f}</b>
                <br><br>
                {competition_interpretation}
                <br><br>
                {financial_interpretation}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Recommended Next Actions</div>
        <div class="insight-body">
            1. Validate lease economics and real estate availability in the selected trade area.<br>
            2. Compare top competitors by service offering, pricing, reviews, and digital presence.<br>
            3. Refine revenue assumptions using average ticket, expected customer volume, and service mix.<br>
            4. Use ZIP-code or neighborhood-level analysis before making a final site-selection decision.
            <br><br>
            <b>Leadership takeaway:</b> {selected_city} should be evaluated as <b>{opportunity_recommendation}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    risk_list_html = "<br>".join([f"• {risk}" for risk in risk_flags]) if risk_flags else "No major risk flags detected."

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Decision Readiness Assessment</div>
        <div class="insight-body">
            <b>Status:</b> {decision_readiness}
            <br><br>
            <b>Data Completeness Score:</b> {data_completeness_score}/100
            <br><br>
            <b>Risk Flags:</b><br>
            {risk_list_html}
            <br><br>
            <b>Interpretation:</b> This assessment indicates whether the current market analysis is ready for leadership discussion
            or still requires further validation before making an expansion decision.
        </div>
    </div>
    """, unsafe_allow_html=True)

    pdf_file = generate_executive_pdf()

    st.download_button(
        label="Download Executive PDF Report",
        data=pdf_file,
        file_name=f"{selected_city.lower().replace(' ', '_')}_executive_report.pdf",
        mime="application/pdf"
    )

    
with tab9:
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

with tab10:

    st.markdown(
        '<div class="section-title">Geo Intelligence Layer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Interactive geographic visualization of expansion opportunities, competitive intensity, and market prioritization.</div>',
        unsafe_allow_html=True
    )

    geo_fig = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        size="Final_Opportunity_Score",
        color="Opportunity_Label",
        hover_name="City",
        hover_data={
            "Population": ":,.0f",
            "Median_Income": ":,.0f",
            "Scenario_ROI": ":.1%",
            "Competitor_Count": True,
            "Final_Opportunity_Score": ":.1f"
        },
        zoom=3.2,
        height=650,
        size_max=35,
        color_discrete_sequence=[
            "#C6A052",
            "#E8D28A",
            "#A9843C",
            "#7D6838"
        ]
    )

    geo_fig.update_layout(
        mapbox_style="carto-positron",
        paper_bgcolor="rgba(255,255,255,0.92)",
        plot_bgcolor="rgba(255,255,255,0.92)",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            bgcolor="rgba(255,255,255,0.75)"
        )
    )

    st.plotly_chart(geo_fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    top_geo = comparison_df.iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Geographic Expansion Insight</div>
        <div class="insight-body">
            <b>{top_geo["City"]}</b> currently represents the strongest geographic expansion opportunity
            based on combined demographic attractiveness, financial viability, and competitive market signals.
            <br><br>
            Markets with larger bubbles indicate higher overall expansion attractiveness under the selected scenario assumptions.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab11:
    st.markdown('<div class="section-title">Data Quality & Assumptions</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">Current Data Sources</div>
            <div class="insight-body">
                Census demographic data, competitive market data, rent assumptions, and operating assumptions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-title">Current Limitations</div>
            <div class="insight-body">
                Market-level data should be validated with ZIP-level, trade-area, lease, and internal performance data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
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
