import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import requests
import matplotlib.pyplot as plt
import gspread

from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from math import radians, sin, cos, sqrt, atan2
import os

st.set_page_config(
    page_title="Strategic Expansion Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

GOLD = "#C6A052"
GOLD_LIGHT = "#E8D28A"

logo_path = Path("logo.png")

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp {{
    background: linear-gradient(135deg, #F7F3EA 0%, #FFFFFF 45%, #EFE6D1 100%);
    color: #111111;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em;
}}

    .block-container {{
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1450px;
    }}

    section.main > div {{
    padding-top: 1.5rem;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #F7F1E4 0%, #EFE2BD 100%);
        border-right: 1px solid #D8C28A;
    }}

    section[data-testid="stSidebar"] * {{
        color: #111111 !important;
    }}

    .hero-title {{
    font-family: 'Inter', sans-serif !important;
    font-size: 1.85rem;
    font-weight: 900;
    color: #111111;
    letter-spacing: -0.04em;
    line-height: 1.08;
    max-width: 100%;
    white-space: normal;
    }}

    .hero-subtitle {{
    font-family: 'Inter', sans-serif !important;
    margin-top: 0.55rem;
    font-size: 0.98rem;
    color: #7A6330;
    font-weight: 600;
    letter-spacing: -0.01em;
    max-width: 980px;
    line-height: 1.45;
    }}

    div[data-testid="stMetric"] {{
        background: rgba(255,255,255,0.92);
        border: 1px solid #E5D6AF;
        border-radius: 22px;
        padding: 0.9rem;
        min-height: 115px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
        overflow: visible !important;
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

    .metric-caption {{
        font-size: 0.72rem;
        color: #6F6A60;
        margin-top: -0.45rem;
        margin-bottom: 0.8rem;
        line-height: 1.25;
    }}

    .score-caption {{
        font-size: 0.76rem;
        font-weight: 700;
        padding: 0.35rem 0.55rem;
        border-radius: 10px;
        margin-top: -0.45rem;
        display: inline-block;
    }}

    .score-low {{
        background: #FDECEC;
        color: #A30000;
        border: 1px solid #E4A2A2;
    }}

    .score-moderate {{
        background: #FFF7D6;
        color: #8A6A00;
        border: 1px solid #E3C85C;
    }}

    .score-strong {{
        background: #EAF7EA;
        color: #1D6B2A;
        border: 1px solid #8ACB8A;
    }}

    .score-high {{
        background: #FFF1C2;
        color: #8A5A00;
        border: 1px solid #D8A800;
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

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}}

section[data-testid="stSidebar"] label {{
    font-size: 0.9rem !important;
    font-weight: 650 !important;
    letter-spacing: -0.01em !important;
}}

section[data-testid="stSidebar"] p {{
    font-size: 0.88rem !important;
    line-height: 1.45 !important;
    color: #6F6A60 !important;
}}

div[data-testid="stMarkdownContainer"] {{
    font-family: 'Inter', sans-serif !important;
}}

/* FIX STREAMLIT ICONS */
[data-testid="stSidebarCollapseButton"] *,
button[kind="header"] *,
span[class*="material"],
span[class*="icon"] {{
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    letter-spacing: normal !important;
}}

</style>
""", unsafe_allow_html=True)

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRlzu0foii8Px9Kajtdoa84Cy3rYy9VdCG3tBa-Hwt7rmisBrXF_x8dYdrn2RgHIhimS0YJNQFAoZVD/pub?gid=0&single=true&output=csv"

GOOGLE_CACHE_FILE = "google_places_cache.csv"
GOOGLE_CACHE_SHEET_CSV_URL = st.secrets.get("GOOGLE_CACHE_SHEET_CSV_URL", "")

# ---------------------------------
# GOOGLE SHEETS CONNECTION
# ---------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def connect_google_sheets():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    return client

def save_cache_to_google_sheet(df_to_save):
    client = connect_google_sheets()

    spreadsheet = client.open_by_key("1TDEk0iVLmS4506y5W1m5OSZynvbGEpF_NhkQXqMwspM")
    worksheet = spreadsheet.worksheet("google_places_cache")

    worksheet.clear()

    set_with_dataframe(
        worksheet,
        df_to_save,
        include_index=False,
        resize=True
    )

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

TRADE_AREAS = {
    "Miami": {
        "Brickell": {"zip": "33131", "lat": 25.7602, "lon": -80.1959},
        "Wynwood": {"zip": "33127", "lat": 25.8043, "lon": -80.1995},
        "Design District": {"zip": "33137", "lat": 25.8130, "lon": -80.1920},
        "Coconut Grove": {"zip": "33133", "lat": 25.7280, "lon": -80.2418},
    },
    "Coral Gables": {
        "Coral Gables Core": {"zip": "33134", "lat": 25.7215, "lon": -80.2684},
    },
    "Doral": {
        "Doral Core": {"zip": "33166", "lat": 25.8195, "lon": -80.3553},
    },
    "Aventura": {
        "Aventura Core": {"zip": "33180", "lat": 25.9565, "lon": -80.1392},
    },
    "Sunny Isles Beach": {
        "Sunny Isles Core": {"zip": "33160", "lat": 25.9429, "lon": -80.1234},
    },
    "Fort Lauderdale": {
        "Fort Lauderdale Core": {"zip": "33301", "lat": 26.1224, "lon": -80.1373},
    }
}

@st.cache_data(ttl=2592000)
def get_google_places_competitors(lat, lon, radius_miles, keyword="hair salon beauty salon"):
    api_key = st.secrets["GOOGLE_PLACES_API_KEY"]
    radius_meters = int(radius_miles * 1609.34)

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": f"{lat},{lon}",
        "radius": radius_meters,
        "keyword": keyword,
        "key": api_key
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if data.get("status") not in ["OK", "ZERO_RESULTS"]:
        st.error(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")
        return pd.DataFrame()

    rows = []

    for place in data.get("results", []):
        rows.append({
            "title": place.get("name"),
            "totalScore": place.get("rating"),
            "reviewsCount": place.get("user_ratings_total", 0),
            "street": place.get("vicinity"),
            "city": selected_city,
            "state": "",
            "categoryName": ", ".join(place.get("types", [])),
            "website": "",
            "url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
            "lat": place.get("geometry", {}).get("location", {}).get("lat"),
            "lng": place.get("geometry", {}).get("location", {}).get("lng"),
            "source": "Google Places API"
        })

    return pd.DataFrame(rows)

@st.cache_data(ttl=300)
def load_google_cache():
    if GOOGLE_CACHE_SHEET_CSV_URL:
        try:
            return pd.read_csv(GOOGLE_CACHE_SHEET_CSV_URL)
        except Exception as e:
            st.warning("Could not load Google Places cache from Google Sheet.")
            st.write(e)
            return pd.DataFrame()

    return pd.DataFrame()
    
@st.cache_data(ttl=3600)
def get_census_place_data(year=2022, state_fips_list=None):
    if state_fips_list is None:
        state_fips_list = ["12"]

    census_key = st.secrets["CENSUS_API_KEY"]
    all_rows = []

    for state_fips in state_fips_list:
        url = (
            f"https://api.census.gov/data/{year}/acs/acs5"
            f"?get=NAME,B01003_001E,B19013_001E"
            f"&for=place:*"
            f"&in=state:{state_fips}"
            f"&key={census_key}"
        )

        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            st.error(f"Census API error {response.status_code}: {response.text[:300]}")
            st.stop()

        try:
            data = response.json()
        except Exception:
            st.error("Census API did not return JSON. Response preview:")
            st.code(response.text[:500])
            st.stop()

        cols = data[0]
        rows = data[1:]

        temp_df = pd.DataFrame(rows, columns=cols)
        all_rows.append(temp_df)

    census_df = pd.concat(all_rows, ignore_index=True)

    census_df = census_df.rename(columns={
        "NAME": "Census_Name",
        "B01003_001E": "Population",
        "B19013_001E": "Median_Income",
        "state": "State_FIPS"
    })

    census_df["Population"] = pd.to_numeric(census_df["Population"], errors="coerce")
    census_df["Median_Income"] = pd.to_numeric(census_df["Median_Income"], errors="coerce")

    return census_df


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


state_fips_needed = df["State"].map(STATE_FIPS).dropna().unique().tolist()
census_df = get_census_place_data(year=2022, state_fips_list=state_fips_needed)

census_df["City_Key"] = census_df["Census_Name"].apply(extract_city_from_census_name)
df["City_Key"] = df["City"].apply(normalize_city_name)
df["State_FIPS"] = df["State"].map(STATE_FIPS)

df = df.merge(
    census_df[["City_Key", "State_FIPS", "Population", "Median_Income"]],
    on=["City_Key", "State_FIPS"],
    how="left"
)

# -----------------------------
# AUTO SCORES FOR SELECTED MARKET
# -----------------------------
def normalize_selected(value, series):
    min_value = series.min()
    max_value = series.max()
    if pd.isna(value) or pd.isna(min_value) or pd.isna(max_value) or max_value == min_value:
        return 0
    return max(0, min(100, ((value - min_value) / (max_value - min_value)) * 100))

# -----------------------------
# USER INPUTS
# -----------------------------
st.sidebar.markdown("## Expansion Scenario Engine")
st.sidebar.caption(
    "Adjust market, revenue, cost, and competitor assumptions to simulate expansion viability."
)

st.sidebar.markdown("""
<div style="
    background: rgba(255,255,255,0.68);
    border: 1px solid #E1C982;
    border-radius: 18px;
    padding: 0.9rem;
    margin: 0.9rem 0 1.1rem 0;
    font-size: 0.82rem;
    line-height: 1.45;
    color: #4A3A16;
">
<b>How this engine works</b><br>
The model combines market demographics, scenario assumptions, competitor signals,
and financial projections to support expansion decision-making.
</div>
""", unsafe_allow_html=True)

df["City"] = df["City"].astype(str).str.strip()

selected_city = st.sidebar.selectbox(
    "Select Market",
    sorted(df["City"].unique())
)

selected_city = selected_city.strip()

rent_change = st.sidebar.slider(
    "Rent Cost Scenario Change %",
    -50,
    100,
    0
)
st.sidebar.caption("Impacts profitability and ROI.")

ticket_change = st.sidebar.slider(
    "Average Ticket Growth Assumption %",
    -50,
    100,
    0
)
st.sidebar.caption("Impacts projected revenue, financial viability, and expansion opportunity scoring.")

customer_change = st.sidebar.slider(
    "Customer Volume Growth Assumption %",
    -50,
    100,
    0
)
st.sidebar.caption("Impacts demand forecasting, revenue projections, and market viability scoring.")

selected_city_clean = selected_city.strip()

trade_area_options = TRADE_AREAS.get(selected_city_clean, {})

if trade_area_options:
    selected_trade_area = st.sidebar.selectbox(
        "Select Trade Area / Neighborhood",
        list(trade_area_options.keys())
    )

    radius_miles = st.sidebar.slider(
        "Radius Around Trade Area (Miles)",
        1,
        10,
        3
    )
else:
    selected_trade_area = None
    radius_miles = 3

use_google_places = st.sidebar.checkbox(
    "Activate live competitor market scanning",
    value=True
)

competitor_keyword = st.sidebar.selectbox(
    "Competitor Classification Query",
    [
        "hair salon beauty salon",
        "luxury hair salon",
        "beauty salon",
        "blow dry bar",
        "hair extensions salon",
        "med spa beauty"
    ]
)

if GOOGLE_CACHE_SHEET_CSV_URL:
    st.sidebar.success("Competitor intelligence data synchronized")
else:
    st.sidebar.warning("Competitor intelligence source not configured")

# ---------------------------------
# GOOGLE PLACES CACHE SYSTEM
# ---------------------------------

if st.sidebar.button("Refresh Live Market Intelligence"):

    if selected_trade_area:

        trade_area_data = TRADE_AREAS[selected_city_clean][selected_trade_area]

        fresh_google_data = get_google_places_competitors(
            lat=trade_area_data["lat"],
            lon=trade_area_data["lon"],
            radius_miles=radius_miles,
            keyword=competitor_keyword
        )

        if not fresh_google_data.empty:

            fresh_google_data["selected_market"] = selected_city_clean
            fresh_google_data["selected_trade_area"] = selected_trade_area
            fresh_google_data["selected_radius"] = radius_miles
            fresh_google_data["selected_keyword"] = competitor_keyword

            existing_cache = load_google_cache()

            if not existing_cache.empty:

                existing_cache.columns = existing_cache.columns.str.strip()

                existing_cache["selected_radius"] = pd.to_numeric(
                    existing_cache["selected_radius"],
                    errors="coerce"
                )

                existing_cache = existing_cache[
                    ~(
                        (existing_cache["selected_market"] == selected_city_clean)
                        &
                        (existing_cache["selected_trade_area"] == selected_trade_area)
                        &
                        (existing_cache["selected_radius"] == radius_miles)
                        &
                        (existing_cache["selected_keyword"] == competitor_keyword)
                    )
                ]

                updated_cache = pd.concat(
                    [existing_cache, fresh_google_data],
                    ignore_index=True
                )

            else:
                updated_cache = fresh_google_data.copy()

            updated_cache.to_csv(GOOGLE_CACHE_FILE, index=False)

            save_cache_to_google_sheet(updated_cache)

            load_google_cache.clear()

            st.success("Google Places data refreshed and synced to Google Sheets.")

        else:
            st.warning("No Google Places results returned.")

    else:
        st.warning("Select a trade area first.")
    
# -----------------------------
# FILTERED DATA
# -----------------------------
filtered = df[df["City"] == selected_city].copy()

google_cache_df = load_google_cache()

if not google_cache_df.empty:
    google_cache_df.columns = google_cache_df.columns.str.strip()
    google_cache_df["city"] = google_cache_df["city"].astype(str).str.strip()
    google_cache_df["totalScore"] = pd.to_numeric(google_cache_df["totalScore"], errors="coerce")
    google_cache_df["reviewsCount"] = pd.to_numeric(google_cache_df["reviewsCount"], errors="coerce").fillna(0)
    google_cache_df["selected_radius"] = pd.to_numeric(google_cache_df["selected_radius"], errors="coerce")

if use_google_places and not google_cache_df.empty:

    filtered_cache = google_cache_df[
        (google_cache_df["selected_market"] == selected_city_clean)
        &
        (google_cache_df["selected_trade_area"] == selected_trade_area)
        &
        (google_cache_df["selected_radius"] == radius_miles)
        &
        (google_cache_df["selected_keyword"] == competitor_keyword)
    ]

    city_competitors = filtered_cache.copy()

else:
    city_competitors = pd.DataFrame()

competitor_count = len(city_competitors)

if not city_competitors.empty and "totalScore" in city_competitors.columns:
    avg_rating = city_competitors["totalScore"].mean()
else:
    avg_rating = 0

if not city_competitors.empty and "reviewsCount" in city_competitors.columns:
    total_reviews = city_competitors["reviewsCount"].sum()
else:
    total_reviews = 0

def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


trade_area_competitors = pd.DataFrame()
trade_area_competitor_count = 0
trade_area_avg_rating = 0
trade_area_total_reviews = 0
trade_area_density = 0
trade_area_zip = None

if selected_trade_area:
    trade_area_data = TRADE_AREAS[selected_city_clean][selected_trade_area]

    trade_area_zip = trade_area_data["zip"]
    trade_area_lat = trade_area_data["lat"]
    trade_area_lon = trade_area_data["lon"]

    possible_lat_cols = ["lat", "latitude", "location.lat"]
    possible_lon_cols = ["lng", "lon", "longitude", "location.lng"]

    lat_col = next((col for col in possible_lat_cols if col in city_competitors.columns), None)
    lon_col = next((col for col in possible_lon_cols if col in city_competitors.columns), None)

    if lat_col and lon_col:
        city_competitors[lat_col] = pd.to_numeric(city_competitors[lat_col], errors="coerce")
        city_competitors[lon_col] = pd.to_numeric(city_competitors[lon_col], errors="coerce")

        competitors_with_location = city_competitors.dropna(subset=[lat_col, lon_col]).copy()

        competitors_with_location["Distance_Miles"] = competitors_with_location.apply(
            lambda row: haversine_miles(
                trade_area_lat,
                trade_area_lon,
                row[lat_col],
                row[lon_col]
            ),
            axis=1
        )

        trade_area_competitors = competitors_with_location[
            competitors_with_location["Distance_Miles"] <= radius_miles
        ].copy()
    else:
        trade_area_competitors = city_competitors.copy()

    trade_area_competitor_count = len(trade_area_competitors)

    if not trade_area_competitors.empty:
        trade_area_avg_rating = trade_area_competitors["totalScore"].mean()
        trade_area_total_reviews = trade_area_competitors["reviewsCount"].sum()
    else:
        trade_area_avg_rating = 0
        trade_area_total_reviews = 0

    radius_area = 3.1416 * (radius_miles ** 2)
    trade_area_density = trade_area_competitor_count / radius_area if radius_area > 0 else 0


filtered["Scenario_Rent"] = (
    filtered["Estimated_Monthly_Rent"]
    * (1 + rent_change / 100)
)

filtered["Scenario_Revenue"] = (
    filtered["Estimated_Monthly_Revenue"]
    * (1 + ticket_change / 100)
    * (1 + customer_change / 100)
)

filtered["Non_Rent_Cost"] = (
    filtered["Estimated_Monthly_Cost"]
    - filtered["Estimated_Monthly_Rent"]
)

filtered["Scenario_Cost"] = (
    filtered["Non_Rent_Cost"]
    + filtered["Scenario_Rent"]
)

filtered["Scenario_Profit"] = (
    filtered["Scenario_Revenue"]
    - filtered["Scenario_Cost"]
)

filtered["Scenario_ROI"] = filtered.apply(
    lambda row: row["Scenario_Profit"] / row["Scenario_Cost"]
    if row["Scenario_Cost"] != 0 else 0,
    axis=1
)
selected_population_score = normalize_selected(
    filtered.iloc[0]["Population"],
    df["Population"]
)

selected_income_score = normalize_selected(
    filtered.iloc[0]["Median_Income"],
    df["Median_Income"]
)

selected_roi_score = max(0, min(100, filtered.iloc[0]["Scenario_ROI"] * 100))

if not google_cache_df.empty:
    review_baseline = google_cache_df.groupby("selected_market")["reviewsCount"].sum()
    saturation_baseline = google_cache_df.groupby("selected_market").size()
else:
    review_baseline = pd.Series([total_reviews])
    saturation_baseline = pd.Series([competitor_count])

selected_review_score = normalize_selected(total_reviews, review_baseline)
selected_saturation_score = normalize_selected(competitor_count, saturation_baseline)

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

if not google_cache_df.empty:
    review_max = google_cache_df.groupby("selected_market")["reviewsCount"].sum().max()
    saturation_max = google_cache_df.groupby("selected_market").size().max()
else:
    review_max = total_reviews
    saturation_max = competitor_count

review_score = normalize_score(
    total_reviews,
    0,
    review_max
)

saturation_score = normalize_score(
    competitor_count,
    0,
    saturation_max
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
def opportunity_score_class(score):
    if score < 50:
        return "score-low", "🔴 Lower Priority"
    elif score < 65:
        return "score-moderate", "🟡 Moderate Opportunity"
    elif score < 80:
        return "score-strong", "🟢 Strong Opportunity"
    else:
        return "score-high", "🌟 High-Priority Expansion Candidate"

score_css_class, score_label = opportunity_score_class(final_opportunity_score)

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
competitor_summary = google_cache_df.copy()
if not competitor_summary.empty:
    competitor_summary["city_key"] = competitor_summary["selected_market"].str.lower()
else:
    competitor_summary = pd.DataFrame(columns=["city_key", "title", "totalScore", "reviewsCount"])

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
comparison_df["Scenario_ROI"] = comparison_df.apply(
    lambda row: row["Scenario_Profit"] / row["Scenario_Cost"]
    if row["Scenario_Cost"] != 0 else 0,
    axis=1
)

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

# -----------------------------
# AI / SUPPLY CHAIN / DATA GOVERNANCE LAYERS
# -----------------------------

comparison_df["Forecasted_Demand_Index"] = (
    comparison_df["Beauty_Demand_Signal"] * 0.50
    + comparison_df["Population_Score"] * 0.25
    + comparison_df["Income_Score"] * 0.25
).clip(0, 100)

comparison_df["Inventory_Risk_Score"] = (
    comparison_df["Forecasted_Demand_Index"] * 0.45
    + comparison_df["Saturation_Score"] * 0.35
    + (100 - comparison_df["ROI_Score"]) * 0.20
).clip(0, 100)

max_competitors = comparison_df["Competitor_Count"].max()

if max_competitors == 0:
    competitor_complexity = 0
else:
    competitor_complexity = comparison_df["Competitor_Count"] / max_competitors * 40

comparison_df["Supply_Chain_Complexity_Score"] = (
    competitor_complexity
    + comparison_df["Population_Score"] * 0.30
    + comparison_df["Forecasted_Demand_Index"] * 0.30
).clip(0, 100)

comparison_df["Data_Governance_Score"] = (
    comparison_df[["Population", "Median_Income", "Estimated_Monthly_Rent", "Estimated_Monthly_Revenue", "Estimated_Monthly_Cost"]]
    .notna()
    .mean(axis=1) * 100
)

comparison_df["Change_Readiness_Score"] = (
    comparison_df["Financial_Viability_Score"] * 0.35
    + comparison_df["Data_Governance_Score"] * 0.35
    + (100 - comparison_df["Supply_Chain_Complexity_Score"]) * 0.30
).clip(0, 100)

def implementation_priority(row):
    if row["Final_Opportunity_Score"] >= 70 and row["Change_Readiness_Score"] >= 70:
        return "Ready for Implementation"
    elif row["Final_Opportunity_Score"] >= 60:
        return "Requires Data and Operations Validation"
    elif row["Inventory_Risk_Score"] >= 70:
        return "High Inventory and Supply Chain Risk"
    else:
        return "Monitor / Lower Priority"

comparison_df["Implementation_Priority"] = comparison_df.apply(implementation_priority, axis=1)

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

    elements.append(Paragraph("AI-Driven Supply Chain & Retail Technology Strategy Report", title_style))
    elements.append(Paragraph(f"{selected_city} Market Expansion, Demand Forecasting, Supply Chain, and Data Governance Analysis"))

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
        ["Forecasted Demand Index", f"{comparison_df.iloc[0]['Forecasted_Demand_Index']:.1f}/100"],
        ["Inventory Risk Score", f"{comparison_df.iloc[0]['Inventory_Risk_Score']:.1f}/100"],
        ["Supply Chain Complexity", f"{comparison_df.iloc[0]['Supply_Chain_Complexity_Score']:.1f}/100"],
        ["Data Governance Score", f"{comparison_df.iloc[0]['Data_Governance_Score']:.1f}/100"],
        ["Change Readiness Score", f"{comparison_df.iloc[0]['Change_Readiness_Score']:.1f}/100"],
        ["Implementation Priority", comparison_df.iloc[0]["Implementation_Priority"]],
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
st.markdown("""
<div class="hero-wrapper">
    <img src="app/static/logo.png" class="hero-logo">
    <div>
        <div class="hero-title">
            AI-DRIVEN SUPPLY CHAIN & RETAIL TECHNOLOGY<br>
            STRATEGY PLATFORM
        </div>
        <div class="hero-subtitle">
            AI analytics, data governance, supply chain optimization, market expansion, and change readiness intelligence
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

top_market = filtered.iloc[0]["City"]
population = filtered.iloc[0]["Population"]
median_income = filtered.iloc[0]["Median_Income"]
avg_roi = filtered["Scenario_ROI"].mean()
total_profit = filtered["Scenario_Profit"].sum()

k1, k2, k3 = st.columns([1.4, 1, 1])
k4, k5, k6 = st.columns([1.2, 1.2, 1.2])
k7, k8, k9 = st.columns([1, 1.3, 1.6])

with k1:
    st.metric("Selected Market", top_market)

with k2:
    st.metric("Population", f"{population:,.0f}" if pd.notna(population) else "Not found")

with k3:
    st.metric("Median Income", f"${median_income:,.0f}" if pd.notna(median_income) else "Not found")

with k4:
    st.metric("Scenario ROI", f"{avg_roi:.1%}")
    st.markdown(
        '<div class="metric-caption">Estimated monthly ROI under current scenario assumptions</div>',
        unsafe_allow_html=True
    )

with k5:
    st.metric("Avg Rating", f"{avg_rating:.1f} / 5.0")
    st.markdown(
        f'<div class="metric-caption">Based on {int(total_reviews):,} total reviews</div>',
        unsafe_allow_html=True
    )

with k6:
    st.metric("Competitors", f"{competitor_count:,}")
    st.markdown(
        '<div class="metric-caption">Active competitors identified within the trade area</div>',
        unsafe_allow_html=True
    )

with k7:
    st.metric("Total Reviews", f"{int(total_reviews):,}")

with k8:
    st.metric("Opportunity Score", f"{final_opportunity_score:.1f} / 100")
    st.markdown(
        f'<div class="score-caption {score_css_class}">{score_label}</div>',
        unsafe_allow_html=True
    )

with k9:
    st.metric("Decision Status", decision_readiness)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18 = st.tabs([
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
    "Data Quality & Assumptions",
    "Market Diagnostics",
    "Trade Area Intelligence", 
    "AI Demand Forecasting",
    "Supply Chain Optimization",
    "Data Governance",
    "Change Management Readiness",
    "Role Alignment Evidence"
    ])

with tab1:
    left, right = st.columns([1, 2])

    general_ranking = comparison_df.sort_values(
        "Final_Opportunity_Score",
        ascending=False
    ).reset_index(drop=True)

    top = general_ranking.iloc[0]
    second = general_ranking.iloc[1] if len(general_ranking) > 1 else top

    with left:
        st.markdown('<div class="section-title">Executive Snapshot</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-note">High-level view of the strongest expansion opportunities.</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Top Recommended Market</div>
            <div class="insight-body">
                <b>{top["City"]}</b> currently ranks highest across all markets.
                <br><br>
                Score: <b>{top["Final_Opportunity_Score"]:.1f}/100</b>
                <br>
                Recommendation: <b>{top["Opportunity_Label"]}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Second Strongest Market</div>
            <div class="insight-body">
                <b>{second["City"]}</b> is the second strongest market in the full ranking.
                <br><br>
                Score: <b>{second["Final_Opportunity_Score"]:.1f}/100</b>
                <br>
                Recommendation: <b>{second["Opportunity_Label"]}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">Expansion Score by Market</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-note">Scores range from 0 to 100. A score of 50 is the minimum validation threshold.</div>',
            unsafe_allow_html=True
        )

        expansion_chart_df = general_ranking.copy()

        expansion_chart_df["Score_Range"] = expansion_chart_df["Final_Opportunity_Score"].apply(
            lambda score: (
                "Lower Priority" if score < 50
                else "Moderate Opportunity" if score < 65
                else "Strong Opportunity"
            )
        )

        color_map = {
            "Lower Priority": "#C94C4C",
            "Moderate Opportunity": "#D8B84E",
            "Strong Opportunity": "#4F9D69"
        }

        fig = px.bar(
            expansion_chart_df,
            x="City",
            y="Final_Opportunity_Score",
            color="Score_Range",
            text="Final_Opportunity_Score",
            category_orders={
                "City": expansion_chart_df["City"].tolist()
            },
            color_discrete_map=color_map
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig.add_hline(
            y=50,
            line_dash="dash",
            line_color="#7A6330",
            annotation_text="Minimum recommended threshold: 50",
            annotation_position="top left"
        )

        fig.update_layout(
            yaxis=dict(range=[0, 110]),
            xaxis_title="Market",
            yaxis_title="Expansion Score",
            showlegend=True
        )

        st.plotly_chart(chart_layout(fig, 560), use_container_width=True)

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

        # CLEAN DATA FOR SCATTER PLOT
        scatter_df = comparison_df.copy()

        numeric_cols = [
            "Median_Income",
            "Population",
            "Final_Opportunity_Score",
            "Scenario_ROI",
            "Competitor_Count",
            "Total_Reviews"
        ]

        for col in numeric_cols:
            scatter_df[col] = pd.to_numeric(scatter_df[col], errors="coerce")

        scatter_df = scatter_df.replace([float("inf"), float("-inf")], pd.NA)

        scatter_df = scatter_df.dropna(
            subset=[
                "Median_Income",
                "Population",
                "Final_Opportunity_Score"
            ]
        )

        scatter_df["Opportunity_Label"] = scatter_df["Opportunity_Label"].fillna("Unknown")

        if scatter_df.empty:
            st.warning("Not enough valid data to display the Market Attractiveness Matrix.")
        else:
            fig4 = px.scatter(
                scatter_df,
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

    # CLEAN DATA FOR GEO MAP
    geo_map_df = map_df.copy()

    geo_numeric_cols = [
        "Latitude",
        "Longitude",
        "Final_Opportunity_Score",
        "Population",
        "Median_Income",
        "Scenario_ROI",
        "Competitor_Count"
    ]

    for col in geo_numeric_cols:
        geo_map_df[col] = pd.to_numeric(geo_map_df[col], errors="coerce")

    geo_map_df = geo_map_df.replace([float("inf"), float("-inf")], pd.NA)

    geo_map_df = geo_map_df.dropna(
        subset=["Latitude", "Longitude", "Final_Opportunity_Score"]
    )

    geo_map_df = geo_map_df[
        (geo_map_df["Latitude"].between(-90, 90))
        &
        (geo_map_df["Longitude"].between(-180, 180))
        &
        (geo_map_df["Final_Opportunity_Score"] > 0)
    ].copy()

    geo_map_df["Opportunity_Label"] = geo_map_df["Opportunity_Label"].fillna("Unknown")

    if geo_map_df.empty:
        st.warning("Not enough valid geographic data to display the Geo Intelligence map.")
    else:
        geo_fig = px.scatter_mapbox(
            geo_map_df,
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

        top_geo = geo_map_df.iloc[0]

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

with tab12:

    st.markdown(
        '<div class="section-title">Market Diagnostics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Executive diagnostic layer explaining market strengths, risks, confidence level, and strategic readiness.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # STRENGTHS
    # -----------------------------
    strengths = []

    if income_score >= 70:
        strengths.append("High-income demographic profile")

    if population_score >= 70:
        strengths.append("Large population base")

    if avg_roi >= 0.15:
        strengths.append("Strong financial viability")

    if total_reviews >= 10000:
        strengths.append("Very high customer activity")

    if avg_rating >= 4.3:
        strengths.append("Strong customer satisfaction signal")

    # -----------------------------
    # RISKS
    # -----------------------------
    risks = []

    if competitor_count >= 100:
        risks.append("High competitive saturation")

    if avg_roi < 0.15:
        risks.append("ROI below priority threshold")

    if total_reviews < 3000:
        risks.append("Limited review volume")

    if pd.isna(population):
        risks.append("Population data unavailable")

    if pd.isna(median_income):
        risks.append("Income data unavailable")

    # -----------------------------
    # CONFIDENCE LEVEL
    # -----------------------------
    if data_completeness_score >= 80:
        confidence_level = "High Confidence"
    elif data_completeness_score >= 60:
        confidence_level = "Moderate Confidence"
    else:
        confidence_level = "Low Confidence"

    # -----------------------------
    # EXECUTIVE VERDICT
    # -----------------------------
    if final_opportunity_score >= 80:
        executive_verdict = "Aggressive Expansion Candidate"

    elif final_opportunity_score >= 65:
        executive_verdict = "Expansion Recommended With Validation"

    elif final_opportunity_score >= 50:
        executive_verdict = "Requires Additional Due Diligence"

    else:
        executive_verdict = "Lower Priority Under Current Assumptions"

    # -----------------------------
    # LAYOUT
    # -----------------------------
    d1, d2 = st.columns(2)

    with d1:

        strengths_html = "<br>".join([f"• {s}" for s in strengths]) if strengths else "No major strengths detected."

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Market Strengths</div>
            <div class="insight-body">
                {strengths_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Confidence Assessment</div>
            <div class="insight-body">
                <b>{confidence_level}</b>
                <br><br>
                Data completeness score:
                <b>{data_completeness_score}/100</b>
                <br><br>
                The confidence assessment reflects whether the current market intelligence is sufficient for leadership-level decision making.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with d2:

        risks_html = "<br>".join([f"• {r}" for r in risks]) if risks else "No major risks detected."

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Market Risks</div>
            <div class="insight-body">
                {risks_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Executive Verdict</div>
            <div class="insight-body">
                <b>{executive_verdict}</b>
                <br><br>
                Final opportunity score:
                <b>{final_opportunity_score:.1f}/100</b>
                <br><br>
                Recommendation:
                <b>{opportunity_recommendation}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # DIAGNOSTIC SCORE BREAKDOWN
    # -----------------------------
    diagnostic_df = pd.DataFrame({
        "Diagnostic Component": [
            "Population Strength",
            "Income Strength",
            "Demand Signal",
            "Financial Viability",
            "Competitive Pressure"
        ],
        "Score": [
            population_score,
            income_score,
            manual_demand_value,
            financial_viability_score,
            saturation_score
        ]
    })

    fig_diag = px.bar(
        diagnostic_df,
        x="Diagnostic Component",
        y="Score",
        text="Score",
        color="Diagnostic Component",
        color_discrete_sequence=[
            GOLD_LIGHT,
            GOLD,
            "#A9843C",
            "#D8C28A",
            "#7D6838"
        ]
    )

    fig_diag.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_diag.update_layout(
        showlegend=False
    )

    st.plotly_chart(
        chart_layout(fig_diag, 520),
        use_container_width=True
    )

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

with tab13:

    st.markdown(
        '<div class="section-title">Trade Area Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Neighborhood-level expansion view using ZIP, radius, competitor concentration, and local demand signals.</div>',
        unsafe_allow_html=True
    )

    if selected_trade_area is None:
        st.warning("No trade area configuration available for this selected market yet.")

    else:
        t1, t2, t3, t4, t5 = st.columns(5)

        t1.metric("Trade Area", selected_trade_area)
        t2.metric("ZIP Code", trade_area_zip)
        t3.metric("Radius", f"{radius_miles} mi")
        t4.metric("Competitors in Radius", f"{trade_area_competitor_count:,}")
        t5.metric("Competitor Density", f"{trade_area_density:.1f} / sq mi")

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Trade Area Signal</div>
                <div class="insight-body">
                    <b>{selected_trade_area}</b> is being evaluated as a local expansion trade area within
                    <b>{selected_city}</b>.
                    <br><br>
                    The current radius analysis identifies <b>{trade_area_competitor_count:,}</b> competitors
                    within approximately <b>{radius_miles} miles</b>.
                    <br><br>
                    Average rating in this trade area:
                    <b>{trade_area_avg_rating:.2f}</b>
                    <br>
                    Total review volume:
                    <b>{int(trade_area_total_reviews):,}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            if trade_area_density >= 10:
                density_interpretation = "High saturation. This area may require strong differentiation, premium positioning, or a very selective real estate strategy."
            elif trade_area_density >= 4:
                density_interpretation = "Moderate saturation. This area may still be attractive if the concept has a clear positioning advantage."
            else:
                density_interpretation = "Lower visible saturation. This may indicate whitespace opportunity, but demand should be validated further."

            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Strategic Interpretation</div>
                <div class="insight-body">
                    <b>{density_interpretation}</b>
                    <br><br>
                    This trade-area layer helps move the analysis beyond city-level expansion and closer to
                    real site-selection decision making.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not trade_area_competitors.empty:
            top_trade_competitors = trade_area_competitors.sort_values(
                "reviewsCount",
                ascending=False
            ).head(10)

            fig_trade = px.bar(
                top_trade_competitors,
                x="reviewsCount",
                y="title",
                orientation="h",
                color="totalScore",
                color_continuous_scale=["#EFE2BD", "#C6A052", "#7D6838"],
                text="reviewsCount"
            )

            fig_trade.update_layout(
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False
            )

            st.plotly_chart(
                chart_layout(fig_trade, 540),
                use_container_width=True
            )

            trade_cols = [
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

            if "Distance_Miles" in trade_area_competitors.columns:
                trade_cols.insert(1, "Distance_Miles")

            available_trade_cols = [
                col for col in trade_cols
                if col in trade_area_competitors.columns
            ]

            st.markdown("### Trade Area Competitor Detail")

            st.dataframe(
                trade_area_competitors[available_trade_cols].sort_values(
                    "reviewsCount",
                    ascending=False
                ),
                use_container_width=True,
                height=420
            )

        else:
            st.warning("No competitor records were found for this trade area under the selected radius.")

with tab14:
    st.markdown('<div class="section-title">AI Demand Forecasting & Inventory Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Predictive layer estimating demand strength and inventory risk by market.</div>', unsafe_allow_html=True)

    fig_ai = px.bar(
        comparison_df.sort_values("Forecasted_Demand_Index", ascending=False),
        x="City",
        y="Forecasted_Demand_Index",
        color="Implementation_Priority",
        text="Forecasted_Demand_Index",
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
    )
    fig_ai.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    st.plotly_chart(chart_layout(fig_ai, 540), use_container_width=True)

    st.dataframe(
        comparison_df[[
            "City",
            "Forecasted_Demand_Index",
            "Inventory_Risk_Score",
            "Beauty_Demand_Signal",
            "Total_Reviews",
            "Implementation_Priority"
        ]],
        use_container_width=True,
        height=420
    )

with tab15:
    st.markdown('<div class="section-title">Supply Chain Optimization Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Evaluates expansion markets through logistics, inventory, and operational complexity signals.</div>', unsafe_allow_html=True)

    fig_supply = px.scatter(
        comparison_df,
        x="Forecasted_Demand_Index",
        y="Supply_Chain_Complexity_Score",
        size="Final_Opportunity_Score",
        color="Implementation_Priority",
        hover_name="City",
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
    )

    st.plotly_chart(chart_layout(fig_supply, 540), use_container_width=True)

    st.dataframe(
        comparison_df[[
            "City",
            "Forecasted_Demand_Index",
            "Inventory_Risk_Score",
            "Supply_Chain_Complexity_Score",
            "Scenario_ROI",
            "Implementation_Priority"
        ]],
        use_container_width=True,
        height=420
    )

with tab16:
    st.markdown('<div class="section-title">Data Governance & Master Data Quality</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Assesses whether market data is complete and reliable enough for executive decision-making.</div>', unsafe_allow_html=True)

    governance_cols = [
        "City",
        "Population",
        "Median_Income",
        "Estimated_Monthly_Rent",
        "Estimated_Monthly_Revenue",
        "Estimated_Monthly_Cost",
        "Data_Governance_Score"
    ]

    st.dataframe(
        comparison_df[governance_cols],
        use_container_width=True,
        height=450
    )

    avg_governance = comparison_df["Data_Governance_Score"].mean()

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Governance Interpretation</div>
        <div class="insight-body">
            Average data governance score across all markets is <b>{avg_governance:.1f}/100</b>.
            This score reflects completeness of demographic, financial, and operational planning data.
            Higher data quality improves confidence in AI-assisted expansion recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab17:
    st.markdown('<div class="section-title">Change Management & Technology Adoption Readiness</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Evaluates implementation readiness based on data quality, financial viability, and operational complexity.</div>', unsafe_allow_html=True)

    fig_change = px.bar(
        comparison_df.sort_values("Change_Readiness_Score", ascending=False),
        x="City",
        y="Change_Readiness_Score",
        color="Implementation_Priority",
        text="Change_Readiness_Score",
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
    )
    fig_change.update_traces(texttemplate="%{text:.1f}", textposition="outside")

    st.plotly_chart(chart_layout(fig_change, 540), use_container_width=True)

    st.dataframe(
        comparison_df[[
            "City",
            "Change_Readiness_Score",
            "Data_Governance_Score",
            "Supply_Chain_Complexity_Score",
            "Financial_Viability_Score",
            "Implementation_Priority"
        ]],
        use_container_width=True,
        height=420
    )

with tab18:
    st.markdown('<div class="section-title">Role Alignment Evidence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">How this platform supports the Management Analyst role in supply chain and retail technology strategy.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">AI-Driven Analytics</div>
        <div class="insight-body">
            The platform uses structured scoring logic, demand signals, competitor intelligence, and scenario modeling to support data-driven decision-making.
        </div>
    </div>
    <br>
    <div class="insight-card">
        <div class="insight-title">Supply Chain Optimization</div>
        <div class="insight-body">
            The platform evaluates inventory risk, demand intensity, market complexity, and operational readiness across expansion markets.
        </div>
    </div>
    <br>
    <div class="insight-card">
        <div class="insight-title">Data Governance</div>
        <div class="insight-body">
            The platform measures data completeness and highlights whether demographic, financial, and operational data is reliable enough for executive decisions.
        </div>
    </div>
    <br>
    <div class="insight-card">
        <div class="insight-title">Change Management & Technology Adoption</div>
        <div class="insight-body">
            The platform estimates implementation readiness by combining data quality, financial viability, and operational complexity.
        </div>
    </div>
    """, unsafe_allow_html=True)
