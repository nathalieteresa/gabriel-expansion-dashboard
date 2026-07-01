import streamlit as st
import pandas as pd
import numpy as np
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

    .hero-wrapper {{
        width: 100%;
        margin-top: 3rem;
        margin-bottom: 2rem;
    }}

    .hero-logo-row {{
        margin-bottom: 1.4rem;
    }}

    .hero-logo-large {{
        width: 110px;
        height: auto;
        display: block;
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

# ---------------------------------
# PRODUCT SALES & INVENTORY DATA
# ---------------------------------

product_file = Path("Gabriel_Samra_Inventory.xlsx")

# Support the corrected uploaded workbook name during local testing while keeping
# the deployment filename as the primary source.
if not product_file.exists():
    alternate_product_file = Path("Gabriel_Samra_Inventory-3.xlsx")
    if alternate_product_file.exists():
        product_file = alternate_product_file
    else:
        st.error(f"Product file not found: {product_file.resolve()}")
        st.stop()

sales_df = pd.read_excel(product_file, sheet_name="Sales_Transactions")
products_df = pd.read_excel(product_file, sheet_name="Products")
inventory_df = pd.read_excel(product_file, sheet_name="Inventory")
stores_df = pd.read_excel(product_file, sheet_name="Stores")

# ---------------------------------
# PRODUCT / STORE DATA GOVERNANCE
# ---------------------------------
# Gabriel Samra currently has two real salon retail locations in this model.
# Candidate expansion markets such as Brickell, Coral Gables, and Miami Design
# District should not be treated as existing stores in Product & Inventory Intelligence.
REAL_STORE_NAME_MAP = {
    "CG-001": "Gabriel Samra Coral Way",
    "DR-001": "Gabriel Samra Doral"
}
REAL_STORE_IDS = list(REAL_STORE_NAME_MAP.keys())
VALID_PRODUCT_BRANDS = sorted(
    products_df["Brand"].dropna().astype(str).str.strip().unique().tolist()
)

def clean_product_operational_data(df_to_clean):
    df_to_clean = df_to_clean.copy()
    if "Store_ID" in df_to_clean.columns:
        df_to_clean = df_to_clean[df_to_clean["Store_ID"].isin(REAL_STORE_IDS)].copy()
        if "Salon_Location" in df_to_clean.columns:
            df_to_clean["Salon_Location"] = df_to_clean["Store_ID"].map(REAL_STORE_NAME_MAP)
    if "Brand" in df_to_clean.columns:
        df_to_clean["Brand"] = df_to_clean["Brand"].astype(str).str.strip()
        df_to_clean = df_to_clean[df_to_clean["Brand"].isin(VALID_PRODUCT_BRANDS)].copy()
    return df_to_clean

sales_df = clean_product_operational_data(sales_df)
inventory_df = clean_product_operational_data(inventory_df)
stores_df = stores_df[stores_df["Store_ID"].isin(REAL_STORE_IDS)].copy()
stores_df["Salon_Location"] = stores_df["Store_ID"].map(REAL_STORE_NAME_MAP)

# ---------------------------------
# ACADEMY ANALYTICS DATA
# ---------------------------------

academy_file = Path("Gabriel_Samra_Academy.xlsx")

if not academy_file.exists():
    st.error(f"Academy file not found: {academy_file.resolve()}")
    st.stop()

academy_students = pd.read_excel(
    academy_file,
    sheet_name="Students"
)

academy_students["Attendance_Rate"] = pd.to_numeric(
    academy_students["Attendance_Rate"],
    errors="coerce"
).fillna(0)

academy_students["Tuition_Paid"] = pd.to_numeric(
    academy_students["Tuition_Paid"],
    errors="coerce"
).fillna(0)

academy_students["Graduated"] = pd.to_numeric(
    academy_students["Graduated"],
    errors="coerce"
).fillna(0)

academy_students["Enrollment_Date"] = pd.to_datetime(
    academy_students["Enrollment_Date"],
    errors="coerce"
)

# ---------------------------------
# ACADEMY KPI CALCULATIONS
# ---------------------------------

total_students = len(academy_students)

completion_rate = (
    len(
        academy_students[
            academy_students["Completion_Status"] == "Completed"
        ]
    ) / total_students
) * 100

avg_attendance = academy_students["Attendance_Rate"].mean()

academy_revenue = academy_students["Tuition_Paid"].sum()

graduation_rate = (
    academy_students["Graduated"].mean()
) * 100

course_summary = academy_students.groupby(
    "Course",
    as_index=False
).agg(
    Students=("Student_ID", "count"),
    Avg_Attendance=("Attendance_Rate", "mean"),
    Revenue=("Tuition_Paid", "sum"),
    Graduation_Rate=("Graduated", "mean")
)

course_summary["Graduation_Rate"] = (
    course_summary["Graduation_Rate"] * 100
)

instructor_summary = academy_students.groupby(
    "Instructor",
    as_index=False
).agg(
    Students=("Student_ID", "count"),
    Avg_Attendance=("Attendance_Rate", "mean"),
    Revenue=("Tuition_Paid", "sum"),
    Graduation_Rate=("Graduated", "mean")
)

instructor_summary["Graduation_Rate"] = (
    instructor_summary["Graduation_Rate"] * 100
)


# ---------------------------------
# FRANCHISE OPERATIONAL INTELLIGENCE DATA
# ---------------------------------

franchise_file = Path("Gabriel_Samra_Franchise.xlsx")

if franchise_file.exists():
    franchise_ops_df = pd.read_excel(
        franchise_file,
        sheet_name="Franchise_Operations"
    )
else:
    # Fallback dataset so the dashboard can run before the real franchise file is connected.
    # Replace this by uploading Gabriel_Samra_Franchise.xlsx with sheet Franchise_Operations.
    salon_base = store_summary.copy() if "store_summary" in globals() else pd.DataFrame()

    if not salon_base.empty:
        franchise_ops_df = salon_base.rename(columns={
            "Salon_Location": "Location_Name",
            "Revenue": "Monthly_Revenue",
            "Gross_Profit": "Gross_Profit"
        })
        franchise_ops_df["Location_Type"] = "Salon"
        franchise_ops_df["Monthly_Cost"] = franchise_ops_df["Monthly_Revenue"] - franchise_ops_df["Gross_Profit"]
        franchise_ops_df["Chairs"] = 8
        franchise_ops_df["Stylists"] = 6
        franchise_ops_df["Months_Open"] = 36
        franchise_ops_df["Customer_Count"] = (franchise_ops_df["Units_Sold"] * 1.8).round(0)
        franchise_ops_df["Owner_Type"] = "Company-Owned"
    else:
        franchise_ops_df = pd.DataFrame(columns=[
            "Location_Name", "Location_Type", "Monthly_Revenue", "Monthly_Cost",
            "Chairs", "Stylists", "Months_Open", "Customer_Count", "Owner_Type"
        ])

    demo_franchise_rows = pd.DataFrame([
        {
            "Location_Name": "Franchise - Doral",
            "Location_Type": "Franchise",
            "Monthly_Revenue": 82000,
            "Monthly_Cost": 61000,
            "Chairs": 9,
            "Stylists": 7,
            "Months_Open": 18,
            "Customer_Count": 520,
            "Owner_Type": "Franchise-Owned"
        },
        {
            "Location_Name": "Franchise - Aventura",
            "Location_Type": "Franchise",
            "Monthly_Revenue": 94000,
            "Monthly_Cost": 69000,
            "Chairs": 10,
            "Stylists": 8,
            "Months_Open": 30,
            "Customer_Count": 610,
            "Owner_Type": "Franchise-Owned"
        }
    ])

    academy_row = pd.DataFrame([{
        "Location_Name": "Gabriel Samra Academy",
        "Location_Type": "Academy",
        "Monthly_Revenue": academy_revenue,
        "Monthly_Cost": academy_revenue * 0.58,
        "Chairs": 0,
        "Stylists": 0,
        "Months_Open": 24,
        "Customer_Count": total_students,
        "Owner_Type": "Company-Owned"
    }])

    franchise_ops_df = pd.concat(
        [franchise_ops_df, demo_franchise_rows, academy_row],
        ignore_index=True
    )

franchise_ops_df.columns = franchise_ops_df.columns.str.strip()

franchise_required_cols = {
    "Location_Name": "Unknown Location",
    "Location_Type": "Franchise",
    "Monthly_Revenue": 0,
    "Monthly_Cost": 0,
    "Chairs": 1,
    "Stylists": 1,
    "Months_Open": 1,
    "Customer_Count": 0,
    "Owner_Type": "Unknown"
}

for col, default_value in franchise_required_cols.items():
    if col not in franchise_ops_df.columns:
        franchise_ops_df[col] = default_value

franchise_numeric_cols = [
    "Monthly_Revenue",
    "Monthly_Cost",
    "Chairs",
    "Stylists",
    "Months_Open",
    "Customer_Count"
]

for col in franchise_numeric_cols:
    franchise_ops_df[col] = pd.to_numeric(
        franchise_ops_df[col],
        errors="coerce"
    ).fillna(0)

franchise_ops_df["Monthly_Profit"] = (
    franchise_ops_df["Monthly_Revenue"] - franchise_ops_df["Monthly_Cost"]
)

franchise_ops_df["Profit_Margin_%"] = franchise_ops_df.apply(
    lambda row: (row["Monthly_Profit"] / row["Monthly_Revenue"] * 100)
    if row["Monthly_Revenue"] > 0 else 0,
    axis=1
).round(1)

franchise_ops_df["Revenue_Per_Chair"] = franchise_ops_df.apply(
    lambda row: row["Monthly_Revenue"] / row["Chairs"]
    if row["Chairs"] > 0 else 0,
    axis=1
).round(0)

franchise_ops_df["Revenue_Per_Stylist"] = franchise_ops_df.apply(
    lambda row: row["Monthly_Revenue"] / row["Stylists"]
    if row["Stylists"] > 0 else 0,
    axis=1
).round(0)

franchise_ops_df["Revenue_Per_Customer"] = franchise_ops_df.apply(
    lambda row: row["Monthly_Revenue"] / row["Customer_Count"]
    if row["Customer_Count"] > 0 else 0,
    axis=1
).round(0)

franchise_ops_df["Location_Maturity"] = franchise_ops_df["Months_Open"].apply(
    lambda x: "Mature" if x >= 36 else "Scaling" if x >= 18 else "New"
)

franchise_ops_df["Location_Maturity_Score"] = franchise_ops_df["Months_Open"].apply(
    lambda x: min(100, (x / 36) * 100)
).round(1)

def normalize_franchise_metric(series):
    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or max_value == min_value:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_value) / (max_value - min_value) * 100).clip(0, 100)

franchise_ops_df["Revenue_Score"] = normalize_franchise_metric(franchise_ops_df["Monthly_Revenue"])
franchise_ops_df["Profitability_Score"] = normalize_franchise_metric(franchise_ops_df["Profit_Margin_%"])
franchise_ops_df["Productivity_Score"] = normalize_franchise_metric(franchise_ops_df["Revenue_Per_Stylist"])
franchise_ops_df["Maturity_Score"] = franchise_ops_df["Location_Maturity_Score"]

franchise_ops_df["Franchise_Operational_Score"] = (
    franchise_ops_df["Revenue_Score"] * 0.30
    + franchise_ops_df["Profitability_Score"] * 0.30
    + franchise_ops_df["Productivity_Score"] * 0.25
    + franchise_ops_df["Maturity_Score"] * 0.15
).round(1)

franchise_ops_df["Performance_Tier"] = franchise_ops_df["Franchise_Operational_Score"].apply(
    lambda score: "Top Performer" if score >= 80
    else "Strong Performer" if score >= 65
    else "Needs Validation" if score >= 50
    else "Operational Risk"
)

franchise_type_summary = franchise_ops_df.groupby(
    "Location_Type",
    as_index=False
).agg(
    Locations=("Location_Name", "count"),
    Monthly_Revenue=("Monthly_Revenue", "sum"),
    Monthly_Cost=("Monthly_Cost", "sum"),
    Monthly_Profit=("Monthly_Profit", "sum"),
    Avg_Profit_Margin=("Profit_Margin_%", "mean"),
    Avg_Revenue_Per_Chair=("Revenue_Per_Chair", "mean"),
    Avg_Revenue_Per_Stylist=("Revenue_Per_Stylist", "mean"),
    Avg_Operational_Score=("Franchise_Operational_Score", "mean")
)

franchise_type_summary["Avg_Profit_Margin"] = franchise_type_summary["Avg_Profit_Margin"].round(1)
franchise_type_summary["Avg_Operational_Score"] = franchise_type_summary["Avg_Operational_Score"].round(1)

# ---------------------------------
# CRM / CUSTOMER INTELLIGENCE DATA
# ---------------------------------

crm_file = Path("Gabriel_Samra_CRM.xlsx")

if crm_file.exists():
    crm_df = pd.read_excel(
        crm_file,
        sheet_name="Customer_Transactions"
    )
else:
    # Fallback CRM dataset so the dashboard can run before the real CRM file is connected.
    # Replace by uploading Gabriel_Samra_CRM.xlsx with sheet Customer_Transactions.
    crm_rows = []
    location_options = (
        sales_df["Salon_Location"].dropna().unique().tolist()
        if "Salon_Location" in sales_df.columns and not sales_df.empty
        else ["Miami Salon", "Doral Salon", "Aventura Salon"]
    )
    service_options = [
        "Color", "Haircut", "Blow Dry", "Extensions", "Treatment", "Retail Product"
    ]
    channel_options = ["Online Booking", "Phone", "Walk-In", "Instagram", "Referral"]
    campaign_options = ["Organic", "Instagram Ads", "Email Campaign", "Referral Program", "Google Search"]

    np.random.seed(42)

    customer_names = [
        "Customer 001", "Customer 002", "Customer 003", "Customer 004", "Customer 005",
        "Customer 006", "Customer 007", "Customer 008", "Customer 009", "Customer 010",
        "Customer 011", "Customer 012", "Customer 013", "Customer 014", "Customer 015",
        "Customer 016", "Customer 017", "Customer 018", "Customer 019", "Customer 020",
        "Customer 021", "Customer 022", "Customer 023", "Customer 024", "Customer 025"
    ]

    start_date = pd.Timestamp.today().normalize() - pd.DateOffset(months=12)

    visit_id = 1
    for customer_index, customer_name in enumerate(customer_names, start=1):
        visit_count = np.random.randint(1, 9)
        preferred_location = np.random.choice(location_options)

        for _ in range(visit_count):
            visit_date = start_date + pd.DateOffset(days=int(np.random.randint(0, 365)))
            service = np.random.choice(service_options)

            if service == "Extensions":
                revenue = np.random.randint(450, 1200)
            elif service == "Color":
                revenue = np.random.randint(180, 520)
            elif service == "Treatment":
                revenue = np.random.randint(120, 350)
            elif service == "Retail Product":
                revenue = np.random.randint(35, 180)
            else:
                revenue = np.random.randint(65, 220)

            crm_rows.append({
                "Visit_ID": f"V{visit_id:04d}",
                "Customer_ID": f"C{customer_index:03d}",
                "Customer_Name": customer_name,
                "Visit_Date": visit_date,
                "Salon_Location": preferred_location,
                "Service_Category": service,
                "Booking_Channel": np.random.choice(channel_options),
                "Campaign_Source": np.random.choice(campaign_options),
                "Revenue": revenue,
                "Discount_Amount": np.random.choice([0, 0, 0, 10, 20, 30]),
                "Satisfaction_Score": np.random.choice([3, 4, 4, 5, 5, 5])
            })
            visit_id += 1

    crm_df = pd.DataFrame(crm_rows)

crm_df.columns = crm_df.columns.str.strip()

crm_required_cols = {
    "Visit_ID": "Unknown Visit",
    "Customer_ID": "Unknown Customer",
    "Customer_Name": "Unknown Customer",
    "Visit_Date": pd.Timestamp.today(),
    "Salon_Location": "Unknown Location",
    "Service_Category": "Unknown Service",
    "Booking_Channel": "Unknown Channel",
    "Campaign_Source": "Unknown Campaign",
    "Revenue": 0,
    "Discount_Amount": 0,
    "Satisfaction_Score": 0
}

for col, default_value in crm_required_cols.items():
    if col not in crm_df.columns:
        crm_df[col] = default_value

crm_df["Visit_Date"] = pd.to_datetime(crm_df["Visit_Date"], errors="coerce")
crm_df = crm_df.dropna(subset=["Visit_Date"])

crm_numeric_cols = ["Revenue", "Discount_Amount", "Satisfaction_Score"]

for col in crm_numeric_cols:
    crm_df[col] = pd.to_numeric(crm_df[col], errors="coerce").fillna(0)

crm_df["Net_Revenue"] = crm_df["Revenue"] - crm_df["Discount_Amount"]
crm_df["Visit_Month"] = crm_df["Visit_Date"].dt.to_period("M").dt.to_timestamp()

analysis_date = crm_df["Visit_Date"].max() + pd.Timedelta(days=1) if not crm_df.empty else pd.Timestamp.today()

customer_summary_df = crm_df.groupby(
    ["Customer_ID", "Customer_Name"],
    as_index=False
).agg(
    Total_Revenue=("Net_Revenue", "sum"),
    Total_Visits=("Visit_ID", "count"),
    First_Visit=("Visit_Date", "min"),
    Last_Visit=("Visit_Date", "max"),
    Avg_Ticket=("Net_Revenue", "mean"),
    Avg_Satisfaction=("Satisfaction_Score", "mean"),
    Favorite_Location=("Salon_Location", lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown"),
    Primary_Channel=("Booking_Channel", lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown"),
    Primary_Campaign=("Campaign_Source", lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown")
)

customer_summary_df["Customer_Tenure_Days"] = (
    customer_summary_df["Last_Visit"] - customer_summary_df["First_Visit"]
).dt.days.clip(lower=1)

customer_summary_df["Days_Since_Last_Visit"] = (
    analysis_date - customer_summary_df["Last_Visit"]
).dt.days

customer_summary_df["Booking_Frequency_Per_Month"] = (
    customer_summary_df["Total_Visits"] / (customer_summary_df["Customer_Tenure_Days"] / 30)
).replace([np.inf, -np.inf], 0).fillna(0).round(2)

customer_summary_df["Estimated_CLV"] = (
    customer_summary_df["Avg_Ticket"]
    * customer_summary_df["Booking_Frequency_Per_Month"]
    * 12
).round(0)

customer_summary_df["Retention_Status"] = customer_summary_df["Days_Since_Last_Visit"].apply(
    lambda x: "Active" if x <= 60
    else "At Risk" if x <= 120
    else "Likely Churned"
)

customer_summary_df["Churn_Risk_%"] = customer_summary_df.apply(
    lambda row: min(
        95,
        max(
            5,
            row["Days_Since_Last_Visit"] * 0.55
            - row["Total_Visits"] * 4
            - row["Avg_Satisfaction"] * 3
        )
    ),
    axis=1
).round(1)

# RFM-style customer segmentation
customer_summary_df["Recency_Score"] = normalize_franchise_metric(
    -customer_summary_df["Days_Since_Last_Visit"]
)
customer_summary_df["Frequency_Score"] = normalize_franchise_metric(
    customer_summary_df["Total_Visits"]
)
customer_summary_df["Monetary_Score"] = normalize_franchise_metric(
    customer_summary_df["Total_Revenue"]
)

customer_summary_df["Customer_Value_Score"] = (
    customer_summary_df["Recency_Score"] * 0.30
    + customer_summary_df["Frequency_Score"] * 0.30
    + customer_summary_df["Monetary_Score"] * 0.40
).round(1)

customer_summary_df["Customer_Segment"] = customer_summary_df.apply(
    lambda row: "VIP / High Value" if row["Customer_Value_Score"] >= 80
    else "Loyal Repeat Customer" if row["Total_Visits"] >= 4 and row["Days_Since_Last_Visit"] <= 90
    else "At-Risk Valuable Customer" if row["Total_Revenue"] >= customer_summary_df["Total_Revenue"].median() and row["Days_Since_Last_Visit"] > 90
    else "New / Developing Customer" if row["Total_Visits"] <= 2 and row["Days_Since_Last_Visit"] <= 90
    else "Low Engagement Customer",
    axis=1
)

customer_segment_summary_df = customer_summary_df.groupby(
    "Customer_Segment",
    as_index=False
).agg(
    Customers=("Customer_ID", "count"),
    Total_Revenue=("Total_Revenue", "sum"),
    Avg_CLV=("Estimated_CLV", "mean"),
    Avg_Churn_Risk=("Churn_Risk_%", "mean"),
    Avg_Visits=("Total_Visits", "mean")
)

customer_segment_summary_df["Avg_CLV"] = customer_segment_summary_df["Avg_CLV"].round(0)
customer_segment_summary_df["Avg_Churn_Risk"] = customer_segment_summary_df["Avg_Churn_Risk"].round(1)
customer_segment_summary_df["Avg_Visits"] = customer_segment_summary_df["Avg_Visits"].round(1)

campaign_attribution_df = crm_df.groupby(
    "Campaign_Source",
    as_index=False
).agg(
    Customers=("Customer_ID", "nunique"),
    Visits=("Visit_ID", "count"),
    Revenue=("Net_Revenue", "sum"),
    Avg_Ticket=("Net_Revenue", "mean"),
    Avg_Satisfaction=("Satisfaction_Score", "mean")
)

campaign_attribution_df["Revenue_Per_Customer"] = campaign_attribution_df.apply(
    lambda row: row["Revenue"] / row["Customers"] if row["Customers"] > 0 else 0,
    axis=1
).round(0)

location_customer_df = crm_df.groupby(
    "Salon_Location",
    as_index=False
).agg(
    Customers=("Customer_ID", "nunique"),
    Visits=("Visit_ID", "count"),
    Revenue=("Net_Revenue", "sum"),
    Avg_Ticket=("Net_Revenue", "mean"),
    Avg_Satisfaction=("Satisfaction_Score", "mean")
)

location_customer_df["Revenue_Per_Customer"] = location_customer_df.apply(
    lambda row: row["Revenue"] / row["Customers"] if row["Customers"] > 0 else 0,
    axis=1
).round(0)

monthly_customer_trend_df = crm_df.groupby(
    "Visit_Month",
    as_index=False
).agg(
    Visits=("Visit_ID", "count"),
    Unique_Customers=("Customer_ID", "nunique"),
    Revenue=("Net_Revenue", "sum")
)


# ---------------------------------
# AUTOMATED DATA VALIDATION ENGINE
# ---------------------------------

validation_results = []

def add_validation_issue(dataset, field, issue_type, issue_count, severity, recommendation):
    validation_results.append({
        "Dataset": dataset,
        "Field": field,
        "Issue_Type": issue_type,
        "Issue_Count": issue_count,
        "Severity": severity,
        "Recommendation": recommendation
    })

# Market data validation
for col in ["City", "State", "Estimated_Monthly_Rent", "Estimated_Monthly_Revenue", "Estimated_Monthly_Cost"]:
    missing_count = df[col].isna().sum()
    if missing_count > 0:
        add_validation_issue(
            "Market Expansion Data",
            col,
            "Missing Values",
            missing_count,
            "High",
            f"Review and complete missing values in {col} before executive decision-making."
        )

# Product sales validation
for col in ["Date", "Units_Sold", "Retail_Price", "Unit_Cost"]:
    missing_count = sales_df[col].isna().sum()
    if missing_count > 0:
        add_validation_issue(
            "Sales Transactions",
            col,
            "Missing or Invalid Values",
            missing_count,
            "High",
            f"Clean or validate {col} to improve demand forecasting accuracy."
        )

negative_sales = len(sales_df[sales_df["Units_Sold"] < 0])
if negative_sales > 0:
    add_validation_issue(
        "Sales Transactions",
        "Units_Sold",
        "Negative Sales Quantity",
        negative_sales,
        "High",
        "Review negative unit sales and confirm if they represent returns or data entry errors."
    )

# Inventory validation
negative_stock = len(inventory_df[inventory_df["Current_Stock"] < 0])
if negative_stock > 0:
    add_validation_issue(
        "Inventory",
        "Current_Stock",
        "Negative Inventory",
        negative_stock,
        "High",
        "Correct inventory records with negative stock levels."
    )

# Academy validation
low_attendance_records = len(academy_students[academy_students["Attendance_Rate"] < 70])
if low_attendance_records > 0:
    add_validation_issue(
        "Academy",
        "Attendance_Rate",
        "Low Attendance",
        low_attendance_records,
        "Medium",
        "Flag students or courses with attendance below 70% for follow-up."
    )

missing_payment_records = len(academy_students[academy_students["Tuition_Paid"] <= 0])
if missing_payment_records > 0:
    add_validation_issue(
        "Academy",
        "Tuition_Paid",
        "Missing or Zero Payment",
        missing_payment_records,
        "Medium",
        "Review student payment records and confirm whether tuition is pending, waived, or incorrectly entered."
    )

validation_df = pd.DataFrame(validation_results)

if validation_df.empty:
    data_validation_score = 100
else:
    high_issues = validation_df[validation_df["Severity"] == "High"]["Issue_Count"].sum()
    medium_issues = validation_df[validation_df["Severity"] == "Medium"]["Issue_Count"].sum()
    data_validation_score = max(0, 100 - high_issues * 5 - medium_issues * 2)

# ---------------------------------
# PRODUCT ANALYTICS CALCULATIONS
# ---------------------------------

if pd.api.types.is_numeric_dtype(sales_df["Date"]):
    sales_df["Date"] = pd.to_datetime(
        sales_df["Date"],
        errors="coerce",
        unit="D",
        origin="1899-12-30"
    )
else:
    sales_df["Date"] = pd.to_datetime(
        sales_df["Date"],
        errors="coerce"
    )
sales_df = sales_df.dropna(subset=["Date"])
sales_df["Units_Sold"] = pd.to_numeric(
    sales_df["Units_Sold"],
    errors="coerce"
).fillna(0)

sales_df["Retail_Price"] = pd.to_numeric(
    sales_df["Retail_Price"],
    errors="coerce"
).fillna(0)

sales_df["Unit_Cost"] = pd.to_numeric(
    sales_df["Unit_Cost"],
    errors="coerce"
).fillna(0)

sales_df["Revenue"] = (
    sales_df["Units_Sold"]
    * sales_df["Retail_Price"]
)

sales_df["COGS_Calculated"] = (
    sales_df["Units_Sold"]
    * sales_df["Unit_Cost"]
)

sales_df["Gross_Profit_Calculated"] = (
    sales_df["Revenue"]
    - sales_df["COGS_Calculated"]
)

sales_df["Gross_Margin_Calculated"] = sales_df.apply(
    lambda row:
    row["Gross_Profit_Calculated"] / row["Revenue"]
    if row["Revenue"] != 0 else 0,
    axis=1
)

product_summary = sales_df.groupby(
    ["Brand", "Product_ID", "Product_Name"],
    as_index=False
).agg(
    Units_Sold=("Units_Sold", "sum"),
    Revenue=("Revenue", "sum"),
    Gross_Profit=("Gross_Profit_Calculated", "sum"),
    Avg_Margin=("Gross_Margin_Calculated", "mean")
)

store_summary = sales_df.groupby(
    ["Store_ID", "Salon_Location"],
    as_index=False
).agg(
    Units_Sold=("Units_Sold", "sum"),
    Revenue=("Revenue", "sum"),
    Gross_Profit=("Gross_Profit_Calculated", "sum")
)

# ---------------------------------
# PRODUCT DEMAND FORECASTING
# ---------------------------------

monthly_product_sales = (
    sales_df
    .dropna(subset=["Date"])
    .groupby([
        pd.Grouper(key="Date", freq="MS"),
        "Salon_Location",
        "Brand",
        "Product_ID",
        "Product_Name"
    ], as_index=False)
    .agg(
        Monthly_Units_Sold=("Units_Sold", "sum"),
        Monthly_Revenue=("Revenue", "sum"),
        Monthly_Gross_Profit=("Gross_Profit_Calculated", "sum")
    )
)

forecast_base = (
    monthly_product_sales
    .sort_values("Date")
    .groupby(["Salon_Location", "Brand", "Product_ID", "Product_Name"])
    .tail(3)
)

product_forecast = (
    forecast_base
    .groupby(["Salon_Location", "Brand", "Product_ID", "Product_Name"], as_index=False)
    .agg(
        Forecast_Next_Month_Units=("Monthly_Units_Sold", "mean"),
        Forecast_Next_Month_Revenue=("Monthly_Revenue", "mean"),
        Forecast_Next_Month_Gross_Profit=("Monthly_Gross_Profit", "mean")
    )
)

product_forecast["Forecast_Next_Month_Units"] = product_forecast["Forecast_Next_Month_Units"].round(0)
product_forecast["Forecast_Next_Month_Revenue"] = product_forecast["Forecast_Next_Month_Revenue"].round(2)
product_forecast["Forecast_Next_Month_Gross_Profit"] = product_forecast["Forecast_Next_Month_Gross_Profit"].round(2)

# ---------------------------------
# ADVANCED AI FORECASTING ENGINE
# ---------------------------------

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import numpy as np

def create_forecast_features(data):
    data = data.copy()
    data["Month_Number"] = data["Date"].dt.month
    data["Year"] = data["Date"].dt.year
    data["Time_Index"] = np.arange(len(data))
    data["Lag_1"] = data["Monthly_Units_Sold"].shift(1)
    data["Lag_2"] = data["Monthly_Units_Sold"].shift(2)
    data["Rolling_3M_Avg"] = data["Monthly_Units_Sold"].rolling(3).mean()
    data["Rolling_3M_Std"] = data["Monthly_Units_Sold"].rolling(3).std()
    return data

forecast_results = []
forecast_accuracy_results = []
forecast_anomalies = []

for keys, group in monthly_product_sales.groupby(
    ["Salon_Location", "Brand", "Product_ID", "Product_Name"]
):
    group = group.sort_values("Date").copy()

    if len(group) < 6:
        continue

    group = create_forecast_features(group)
    model_data = group.dropna().copy()

    if len(model_data) < 4:
        continue

    feature_cols = [
        "Month_Number",
        "Year",
        "Time_Index",
        "Lag_1",
        "Lag_2",
        "Rolling_3M_Avg",
        "Rolling_3M_Std"
    ]

    X = model_data[feature_cols]
    y = model_data["Monthly_Units_Sold"]

    train_size = max(3, int(len(model_data) * 0.75))

    X_train = X.iloc[:train_size]
    X_test = X.iloc[train_size:]
    y_train = y.iloc[:train_size]
    y_test = y.iloc[train_size:]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=5
    )

    model.fit(X_train, y_train)

    if len(X_test) > 0:
        y_pred = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        try:
            mape = mean_absolute_percentage_error(y_test, y_pred) * 100
        except:
            mape = np.nan

        forecast_confidence = max(0, min(100, 100 - mape)) if not pd.isna(mape) else 0
    else:
        rmse = np.nan
        mape = np.nan
        forecast_confidence = 0

    last_row = group.iloc[-1].copy()
    last_date = group["Date"].max()

    future_rows = []

    recent_values = group["Monthly_Units_Sold"].tail(3).tolist()

    for i in range(1, 7):
        future_date = last_date + pd.DateOffset(months=i)

        lag_1 = recent_values[-1] if len(recent_values) >= 1 else 0
        lag_2 = recent_values[-2] if len(recent_values) >= 2 else lag_1
        rolling_avg = np.mean(recent_values[-3:]) if len(recent_values) >= 3 else np.mean(recent_values)
        rolling_std = np.std(recent_values[-3:]) if len(recent_values) >= 3 else 0

        future_features = pd.DataFrame([{
            "Month_Number": future_date.month,
            "Year": future_date.year,
            "Time_Index": len(group) + i,
            "Lag_1": lag_1,
            "Lag_2": lag_2,
            "Rolling_3M_Avg": rolling_avg,
            "Rolling_3M_Std": rolling_std
        }])

        forecast_units = max(0, model.predict(future_features)[0])

        recent_values.append(forecast_units)

        lower_bound = max(0, forecast_units - rmse) if not pd.isna(rmse) else forecast_units * 0.85
        upper_bound = forecast_units + rmse if not pd.isna(rmse) else forecast_units * 1.15

        future_rows.append({
            "Salon_Location": keys[0],
            "Brand": keys[1],
            "Product_ID": keys[2],
            "Product_Name": keys[3],
            "Forecast_Month": future_date,
            "AI_Forecast_Units": round(forecast_units, 0),
            "Forecast_Lower_Bound": round(lower_bound, 0),
            "Forecast_Upper_Bound": round(upper_bound, 0),
            "Forecast_RMSE": round(rmse, 2) if not pd.isna(rmse) else None,
            "Forecast_MAPE": round(mape, 2) if not pd.isna(mape) else None,
            "Forecast_Confidence": round(forecast_confidence, 1)
        })

    forecast_results.extend(future_rows)

    last_3_avg = group["Monthly_Units_Sold"].tail(3).mean()
    previous_3_avg = group["Monthly_Units_Sold"].tail(6).head(3).mean()

    if previous_3_avg == 0:
        trend_direction = "Insufficient History"
        trend_change = 0
    else:
        trend_change = ((last_3_avg - previous_3_avg) / previous_3_avg) * 100

        if trend_change >= 15:
            trend_direction = "Increasing Demand"
        elif trend_change <= -15:
            trend_direction = "Declining Demand"
        else:
            trend_direction = "Stable Demand"

    forecast_accuracy_results.append({
        "Salon_Location": keys[0],
        "Brand": keys[1],
        "Product_ID": keys[2],
        "Product_Name": keys[3],
        "Forecast_RMSE": round(rmse, 2) if not pd.isna(rmse) else None,
        "Forecast_MAPE": round(mape, 2) if not pd.isna(mape) else None,
        "Forecast_Confidence": round(forecast_confidence, 1),
        "Trend_Direction": trend_direction,
        "Trend_Change_%": round(trend_change, 1)
    })

    group["Historical_Avg"] = group["Monthly_Units_Sold"].rolling(3).mean()
    group["Historical_Std"] = group["Monthly_Units_Sold"].rolling(3).std()
    group["Anomaly_Threshold_High"] = group["Historical_Avg"] + 2 * group["Historical_Std"]
    group["Anomaly_Threshold_Low"] = group["Historical_Avg"] - 2 * group["Historical_Std"]

    anomaly_rows = group[
        (group["Monthly_Units_Sold"] > group["Anomaly_Threshold_High"])
        |
        (group["Monthly_Units_Sold"] < group["Anomaly_Threshold_Low"])
    ].copy()

    for _, anomaly in anomaly_rows.iterrows():
        forecast_anomalies.append({
            "Salon_Location": keys[0],
            "Brand": keys[1],
            "Product_ID": keys[2],
            "Product_Name": keys[3],
            "Date": anomaly["Date"],
            "Monthly_Units_Sold": anomaly["Monthly_Units_Sold"],
            "Expected_Avg": round(anomaly["Historical_Avg"], 1),
            "Anomaly_Type": "Demand Spike" if anomaly["Monthly_Units_Sold"] > anomaly["Anomaly_Threshold_High"] else "Demand Drop"
        })

ai_forecast_df = pd.DataFrame(forecast_results)
forecast_accuracy_df = pd.DataFrame(forecast_accuracy_results)
forecast_anomaly_df = pd.DataFrame(forecast_anomalies)
    
brand_summary = sales_df.groupby(
    "Brand",
    as_index=False
).agg(
    Units_Sold=("Units_Sold", "sum"),
    Revenue=("Revenue", "sum"),
    Gross_Profit=("Gross_Profit_Calculated", "sum")
)

inventory_df["Current_Stock"] = pd.to_numeric(
    inventory_df["Current_Stock"],
    errors="coerce"
).fillna(0)

inventory_df["Reorder_Point"] = pd.to_numeric(
    inventory_df["Reorder_Point"],
    errors="coerce"
).fillna(0)

inventory_df["Inventory_Status"] = inventory_df.apply(
    lambda row:
    "Reorder Needed"
    if row["Current_Stock"] <= row["Reorder_Point"]
    else "Healthy Stock",
    axis=1
)

# ---------------------------------
# REORDER RECOMMENDATION ENGINE
# ---------------------------------

reorder_df = inventory_df.merge(
    product_forecast,
    on=["Salon_Location", "Brand", "Product_ID", "Product_Name"],
    how="left"
)

reorder_df["Forecast_Next_Month_Units"] = reorder_df["Forecast_Next_Month_Units"].fillna(0)

reorder_df["Projected_Ending_Stock"] = (
    reorder_df["Current_Stock"] - reorder_df["Forecast_Next_Month_Units"]
)

reorder_df["Recommended_Reorder_Qty"] = reorder_df.apply(
    lambda row: max(
        0,
        (row["Forecast_Next_Month_Units"] + row["Reorder_Point"]) - row["Current_Stock"]
    ),
    axis=1
).round(0)

reorder_df["Reorder_Recommendation"] = reorder_df.apply(
    lambda row:
    "Urgent Reorder"
    if row["Projected_Ending_Stock"] <= 0
    else "Reorder Soon"
    if row["Projected_Ending_Stock"] <= row["Reorder_Point"]
    else "No Reorder Needed",
    axis=1
)

# ---------------------------------
# ADVANCED SUPPLY CHAIN OPTIMIZATION ENGINE
# ---------------------------------

import numpy as np

# Ensure required supply chain columns exist
default_supply_chain_values = {
    "Supplier": "Default Supplier",
    "Lead_Time_Days": 14,
    "Lead_Time_Std_Days": 3,
    "Supplier_Reliability": 0.90,
    "On_Time_Delivery_Rate": 0.88,
    "Fill_Rate": 0.92,
    "Shipping_Cost_Per_Unit": 1.25,
    "Warehouse_Cost_Per_Unit": 0.40,
    "Fulfillment_Cost_Per_Unit": 0.85
}

for col, default_value in default_supply_chain_values.items():
    if col not in inventory_df.columns:
        inventory_df[col] = default_value

# Clean numeric columns
supply_numeric_cols = [
    "Lead_Time_Days",
    "Lead_Time_Std_Days",
    "Supplier_Reliability",
    "On_Time_Delivery_Rate",
    "Fill_Rate",
    "Shipping_Cost_Per_Unit",
    "Warehouse_Cost_Per_Unit",
    "Fulfillment_Cost_Per_Unit"
]

for col in supply_numeric_cols:
    inventory_df[col] = pd.to_numeric(
        inventory_df[col],
        errors="coerce"
    ).fillna(default_supply_chain_values[col])

# Merge inventory with forecast
supply_chain_df = inventory_df.merge(
    product_forecast,
    on=["Salon_Location", "Brand", "Product_ID", "Product_Name"],
    how="left"
)

supply_chain_df["Forecast_Next_Month_Units"] = supply_chain_df["Forecast_Next_Month_Units"].fillna(0)

# Estimate daily demand
supply_chain_df["Avg_Daily_Demand"] = (
    supply_chain_df["Forecast_Next_Month_Units"] / 30
).replace([np.inf, -np.inf], 0).fillna(0)

# Demand variability based on monthly sales history
demand_variability = (
    monthly_product_sales
    .groupby(["Salon_Location", "Brand", "Product_ID", "Product_Name"], as_index=False)
    .agg(
        Demand_Std_Monthly=("Monthly_Units_Sold", "std"),
        Avg_Monthly_Demand=("Monthly_Units_Sold", "mean")
    )
)

demand_variability["Demand_Std_Daily"] = (
    demand_variability["Demand_Std_Monthly"] / 30
).fillna(0)

supply_chain_df = supply_chain_df.merge(
    demand_variability[
        ["Salon_Location", "Brand", "Product_ID", "Product_Name", "Demand_Std_Daily", "Avg_Monthly_Demand"]
    ],
    on=["Salon_Location", "Brand", "Product_ID", "Product_Name"],
    how="left"
)

supply_chain_df["Demand_Std_Daily"] = supply_chain_df["Demand_Std_Daily"].fillna(0)
supply_chain_df["Avg_Monthly_Demand"] = supply_chain_df["Avg_Monthly_Demand"].fillna(0)

# Service level selector later will update Z value in tab, but default here is 95%
service_level_z = 1.65

# Safety Stock = Z * sigma_d * sqrt(lead time)
supply_chain_df["Safety_Stock"] = (
    service_level_z
    * supply_chain_df["Demand_Std_Daily"]
    * np.sqrt(supply_chain_df["Lead_Time_Days"])
).round(0)

# Reorder Point = demand during lead time + safety stock
supply_chain_df["Optimized_Reorder_Point"] = (
    supply_chain_df["Avg_Daily_Demand"] * supply_chain_df["Lead_Time_Days"]
    + supply_chain_df["Safety_Stock"]
).round(0)

# Stockout risk logic
supply_chain_df["Projected_Stock_During_Lead_Time"] = (
    supply_chain_df["Current_Stock"]
    - (supply_chain_df["Avg_Daily_Demand"] * supply_chain_df["Lead_Time_Days"])
)

supply_chain_df["Stockout_Risk_%"] = supply_chain_df.apply(
    lambda row:
    95 if row["Projected_Stock_During_Lead_Time"] <= 0
    else max(
        0,
        min(
            95,
            100 - ((row["Projected_Stock_During_Lead_Time"] / max(row["Optimized_Reorder_Point"], 1)) * 100)
        )
    ),
    axis=1
).round(1)

# Optimized reorder quantity
supply_chain_df["Optimized_Reorder_Qty"] = supply_chain_df.apply(
    lambda row: max(
        0,
        (row["Optimized_Reorder_Point"] + row["Forecast_Next_Month_Units"]) - row["Current_Stock"]
    ),
    axis=1
).round(0)

# Inventory value and turnover
supply_chain_df["Inventory_Value"] = (
    supply_chain_df["Current_Stock"]
    * supply_chain_df.get("Unit_Cost", 0)
)

if "Unit_Cost" not in supply_chain_df.columns:
    unit_cost_lookup = sales_df.groupby(
        ["Brand", "Product_ID", "Product_Name"],
        as_index=False
    ).agg(Unit_Cost=("Unit_Cost", "mean"))

    supply_chain_df = supply_chain_df.merge(
        unit_cost_lookup,
        on=["Brand", "Product_ID", "Product_Name"],
        how="left"
    )

supply_chain_df["Unit_Cost"] = supply_chain_df["Unit_Cost"].fillna(0)

supply_chain_df["Inventory_Value"] = (
    supply_chain_df["Current_Stock"] * supply_chain_df["Unit_Cost"]
)

supply_chain_df["Annualized_COGS"] = (
    supply_chain_df["Forecast_Next_Month_Units"] * 12 * supply_chain_df["Unit_Cost"]
)

supply_chain_df["Inventory_Turnover"] = supply_chain_df.apply(
    lambda row: row["Annualized_COGS"] / row["Inventory_Value"]
    if row["Inventory_Value"] > 0 else 0,
    axis=1
).round(2)

# ABC classification based on revenue contribution
abc_base = product_summary.copy()
abc_base = abc_base.sort_values("Revenue", ascending=False)
abc_base["Revenue_Share"] = abc_base["Revenue"] / abc_base["Revenue"].sum()
abc_base["Cumulative_Revenue_Share"] = abc_base["Revenue_Share"].cumsum()

abc_base["ABC_Class"] = abc_base["Cumulative_Revenue_Share"].apply(
    lambda x: "A" if x <= 0.80 else "B" if x <= 0.95 else "C"
)

supply_chain_df = supply_chain_df.merge(
    abc_base[["Brand", "Product_ID", "Product_Name", "ABC_Class"]],
    on=["Brand", "Product_ID", "Product_Name"],
    how="left"
)

supply_chain_df["ABC_Class"] = supply_chain_df["ABC_Class"].fillna("C")

# Supplier performance score
supply_chain_df["Supplier_Performance_Score"] = (
    supply_chain_df["Supplier_Reliability"] * 0.40
    + supply_chain_df["On_Time_Delivery_Rate"] * 0.35
    + supply_chain_df["Fill_Rate"] * 0.25
) * 100

supply_chain_df["Supplier_Performance_Score"] = supply_chain_df["Supplier_Performance_Score"].round(1)

# Logistics cost
supply_chain_df["Total_Logistics_Cost_Per_Unit"] = (
    supply_chain_df["Shipping_Cost_Per_Unit"]
    + supply_chain_df["Warehouse_Cost_Per_Unit"]
    + supply_chain_df["Fulfillment_Cost_Per_Unit"]
).round(2)

supply_chain_df["Projected_Logistics_Cost"] = (
    supply_chain_df["Optimized_Reorder_Qty"]
    * supply_chain_df["Total_Logistics_Cost_Per_Unit"]
).round(2)

# Supply chain risk classification
supply_chain_df["Supply_Chain_Risk_Level"] = supply_chain_df.apply(
    lambda row:
    "High Risk"
    if row["Stockout_Risk_%"] >= 70 or row["Supplier_Performance_Score"] < 75
    else "Medium Risk"
    if row["Stockout_Risk_%"] >= 40 or row["Supplier_Performance_Score"] < 85
    else "Low Risk",
    axis=1
)

# Supplier scorecard
supplier_scorecard_df = supply_chain_df.groupby(
    "Supplier",
    as_index=False
).agg(
    Avg_Lead_Time=("Lead_Time_Days", "mean"),
    Avg_Supplier_Reliability=("Supplier_Reliability", "mean"),
    Avg_OTIF=("On_Time_Delivery_Rate", "mean"),
    Avg_Fill_Rate=("Fill_Rate", "mean"),
    Avg_Performance_Score=("Supplier_Performance_Score", "mean"),
    Total_Projected_Logistics_Cost=("Projected_Logistics_Cost", "sum"),
    High_Risk_Items=("Supply_Chain_Risk_Level", lambda x: (x == "High Risk").sum())
)

supplier_scorecard_df["Avg_Supplier_Reliability"] = supplier_scorecard_df["Avg_Supplier_Reliability"] * 100
supplier_scorecard_df["Avg_OTIF"] = supplier_scorecard_df["Avg_OTIF"] * 100
supplier_scorecard_df["Avg_Fill_Rate"] = supplier_scorecard_df["Avg_Fill_Rate"] * 100

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
        (
            (google_cache_df["selected_radius"] == radius_miles)
            | (google_cache_df["selected_radius"].isna())
        )
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
        city_competitors[lat_col] = pd.to_numeric(
            city_competitors[lat_col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce"
        )
        city_competitors[lon_col] = pd.to_numeric(
            city_competitors[lon_col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce"
        )

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
st.markdown('<div class="hero-wrapper">', unsafe_allow_html=True)

if logo_path.exists():
    st.image("logo.png", width=125)

st.markdown("""
<div class="hero-title">
AI-DRIVEN SUPPLY CHAIN & RETAIL TECHNOLOGY<br>
STRATEGY PLATFORM
</div>
<div class="hero-subtitle">
AI analytics, data governance, supply chain optimization, market expansion, and change readiness intelligence
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18, tab19, tab20, tab21, tab22, tab23, tab24, tab25, tab26, tab27, tab28, tab29, tab30, tab31, tab32, tab33, tab34, tab35, tab36, tab37, tab38, tab39, tab40, tab41, tab42, tab43, tab44, tab45 = st.tabs([
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
    "Role Alignment Evidence",
    "Product & Inventory Intelligence",
    "Product Demand Forecasting",
    "Reorder Recommendation Engine", 
    "Academy & Training Intelligence",
    "Automated Data Validation",
    "Advanced AI Forecasting",
    "Advanced Supply Chain Optimization",
    "Franchise Performance Dashboard",
    "Franchise Profitability",
    "Multi-Location Benchmarking",
    "Customer Intelligence",
    "Retention & Churn Analytics",
    "Campaign Attribution",
    "Transformation Governance",
    "Data Governance Maturity",
    "Executive Simulation Engine",
    "Real AI Recommendations",
    "Workforce & Labor Optimization",
    "Executive Architecture Documentation",
    "Security & Enterprise Readiness",
    "KPI Drill-Down Center",
    "Real-Time Operational Alerts",
    "Workflow Automation",
    "Strategic Consulting Layer",
    "Adoption KPI Center",
    "Staff Data Literacy",
    "Supply Chain Traceability"
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

with tab19:

    st.markdown(
        '<div class="section-title">Product & Inventory Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">AI-driven product analytics, inventory visibility, and retail performance intelligence for existing Gabriel Samra salon retail locations: Coral Way and Doral.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # KPI ROW
    # -----------------------------

    total_revenue = product_summary["Revenue"].sum()
    total_units = product_summary["Units_Sold"].sum()
    total_profit_products = product_summary["Gross_Profit"].sum()

    low_stock_count = len(
        inventory_df[
            inventory_df["Inventory_Status"] == "Reorder Needed"
        ]
    )

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Total Revenue",
        f"${total_revenue:,.0f}"
    )

    p2.metric(
        "Units Sold",
        f"{total_units:,.0f}"
    )

    p3.metric(
        "Gross Profit",
        f"${total_profit_products:,.0f}"
    )

    p4.metric(
        "Low Stock Alerts",
        f"{low_stock_count:,}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "Product & Inventory Intelligence is filtered to the current Gabriel Samra salon retail footprint: "
        "Gabriel Samra Coral Way and Gabriel Samra Doral. Candidate expansion markets such as Brickell, "
        "Coral Gables, and Miami Design District are excluded from store performance reporting."
    )

    # -----------------------------
    # TOP PRODUCTS
    # -----------------------------

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "### Top Selling Products"
        )

        top_products = product_summary.sort_values(
            "Revenue",
            ascending=False
        ).head(10)

        fig_products = px.bar(
            top_products,
            x="Revenue",
            y="Product_Name",
            orientation="h",
            color="Brand",
            text="Revenue",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838"
            ]
        )

        fig_products.update_layout(
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(
            chart_layout(fig_products, 520),
            use_container_width=True
        )

    with c2:

        st.markdown(
            "### Retail Revenue by Product Brand"
        )

        fig_brand = px.pie(
            brand_summary,
            names="Brand",
            values="Revenue",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838"
            ]
        )

        st.plotly_chart(
            chart_layout(fig_brand, 520),
            use_container_width=True
        )

    # -----------------------------
    # INVENTORY RISK
    # -----------------------------

    st.markdown("### Inventory Risk Intelligence")

    inventory_risk = inventory_df.copy()

    fig_inventory = px.bar(
        inventory_risk.sort_values(
            "Current_Stock"
        ),
        x="Product_Name",
        y="Current_Stock",
        color="Inventory_Status",
        text="Current_Stock",
        color_discrete_map={
            "Healthy Stock": "#C6A052",
            "Reorder Needed": "#B22222"
        }
    )

    st.plotly_chart(
        chart_layout(fig_inventory, 540),
        use_container_width=True
    )

    st.dataframe(
        inventory_df[[
            "Salon_Location",
            "Brand",
            "Product_Name",
            "Current_Stock",
            "Reorder_Point",
            "Inventory_Status"
        ]],
        use_container_width=True,
        height=420
    )

    # -----------------------------
    # STORE PERFORMANCE
    # -----------------------------

    st.markdown("### Store Performance Intelligence")

    fig_store = px.bar(
        store_summary.sort_values(
            "Revenue",
            ascending=False
        ),
        x="Salon_Location",
        y="Revenue",
        color="Gross_Profit",
        text="Revenue",
        color_continuous_scale=[
            "#EFE2BD",
            "#C6A052",
            "#7D6838"
        ]
    )

    st.plotly_chart(
        chart_layout(fig_store, 520),
        use_container_width=True
    )

    st.dataframe(
        store_summary,
        use_container_width=True,
        height=320
    )

    # -----------------------------
    # EXECUTIVE INTERPRETATION
    # -----------------------------

    top_product = top_products.iloc[0]["Product_Name"]
    top_brand = brand_summary.sort_values(
        "Revenue",
        ascending=False
    ).iloc[0]["Brand"]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Product Intelligence Summary</div>
        <div class="insight-body">
            Among retail product brands sold through Gabriel Samra salon locations, <b>{top_brand}</b> currently represents the strongest revenue-driving product brand.
            <br><br>
            The top-performing product is <b>{top_product}</b>, based on total sales revenue.
            <br><br>
            Inventory analysis identified <b>{low_stock_count}</b> products requiring replenishment attention.
            <br><br>
            This intelligence layer supports retail optimization, demand forecasting, inventory planning,
            and AI-assisted operational decision-making for existing salon retail operations only. Candidate expansion markets are analyzed separately in the market-expansion modules.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab20:

    st.markdown(
        '<div class="section-title">Product Demand Forecasting</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Monthly demand forecast by product, brand, and salon location based on recent sales patterns.</div>',
        unsafe_allow_html=True
    )

    f1, f2, f3 = st.columns(3)

    total_forecast_units = product_forecast["Forecast_Next_Month_Units"].sum()
    total_forecast_revenue = product_forecast["Forecast_Next_Month_Revenue"].sum()
    total_forecast_profit = product_forecast["Forecast_Next_Month_Gross_Profit"].sum()

    f1.metric("Forecasted Units Next Month", f"{total_forecast_units:,.0f}")
    f2.metric("Forecasted Revenue Next Month", f"${total_forecast_revenue:,.0f}")
    f3.metric("Forecasted Gross Profit Next Month", f"${total_forecast_profit:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Forecast by Product")

        top_forecast_products = product_forecast.sort_values(
            "Forecast_Next_Month_Revenue",
            ascending=False
        ).head(10)

        fig_forecast_product = px.bar(
            top_forecast_products,
            x="Forecast_Next_Month_Revenue",
            y="Product_Name",
            orientation="h",
            color="Brand",
            text="Forecast_Next_Month_Revenue",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838"
            ]
        )

        fig_forecast_product.update_layout(
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(
            chart_layout(fig_forecast_product, 520),
            use_container_width=True
        )

    with c2:
        st.markdown("### Forecast by Salon")

        salon_forecast = product_forecast.groupby(
            "Salon_Location",
            as_index=False
        ).agg(
            Forecast_Next_Month_Units=("Forecast_Next_Month_Units", "sum"),
            Forecast_Next_Month_Revenue=("Forecast_Next_Month_Revenue", "sum"),
            Forecast_Next_Month_Gross_Profit=("Forecast_Next_Month_Gross_Profit", "sum")
        )

        fig_forecast_salon = px.bar(
            salon_forecast,
            x="Salon_Location",
            y="Forecast_Next_Month_Revenue",
            color="Forecast_Next_Month_Gross_Profit",
            text="Forecast_Next_Month_Revenue",
            color_continuous_scale=[
                "#EFE2BD",
                "#C6A052",
                "#7D6838"
            ]
        )

        st.plotly_chart(
            chart_layout(fig_forecast_salon, 520),
            use_container_width=True
        )

    st.markdown("### Forecast Detail Table")

    st.dataframe(
        product_forecast.sort_values(
            "Forecast_Next_Month_Revenue",
            ascending=False
        ),
        use_container_width=True,
        height=450
    )

    top_forecast_product = product_forecast.sort_values(
        "Forecast_Next_Month_Revenue",
        ascending=False
    ).iloc[0]["Product_Name"]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Forecasting Summary</div>
        <div class="insight-body">
            Based on the most recent monthly sales behavior, the next-month forecast estimates
            <b>{total_forecast_units:,.0f}</b> units sold and approximately
            <b>${total_forecast_revenue:,.0f}</b> in product revenue.
            <br><br>
            The strongest forecasted product is <b>{top_forecast_product}</b>.
            <br><br>
            This forecasting layer supports demand planning, inventory optimization,
            replenishment decisions, and AI-assisted retail operations.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab21:

    st.markdown(
        '<div class="section-title">Reorder Recommendation Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">AI-assisted replenishment recommendations based on forecasted demand, current stock, and reorder thresholds.</div>',
        unsafe_allow_html=True
    )

    urgent_count = len(reorder_df[reorder_df["Reorder_Recommendation"] == "Urgent Reorder"])
    reorder_soon_count = len(reorder_df[reorder_df["Reorder_Recommendation"] == "Reorder Soon"])
    total_reorder_units = reorder_df["Recommended_Reorder_Qty"].sum()

    r1, r2, r3 = st.columns(3)

    r1.metric("Urgent Reorder Items", f"{urgent_count:,}")
    r2.metric("Reorder Soon Items", f"{reorder_soon_count:,}")
    r3.metric("Recommended Units to Order", f"{total_reorder_units:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    fig_reorder = px.bar(
        reorder_df.sort_values("Recommended_Reorder_Qty", ascending=False),
        x="Product_Name",
        y="Recommended_Reorder_Qty",
        color="Reorder_Recommendation",
        text="Recommended_Reorder_Qty",
        color_discrete_map={
            "Urgent Reorder": "#B22222",
            "Reorder Soon": "#C6A052",
            "No Reorder Needed": "#8A8A8A"
        }
    )

    st.plotly_chart(
        chart_layout(fig_reorder, 540),
        use_container_width=True
    )

    st.markdown("### Reorder Detail Table")

    st.dataframe(
        reorder_df[[
            "Salon_Location",
            "Brand",
            "Product_Name",
            "Current_Stock",
            "Reorder_Point",
            "Forecast_Next_Month_Units",
            "Projected_Ending_Stock",
            "Recommended_Reorder_Qty",
            "Reorder_Recommendation"
        ]].sort_values("Recommended_Reorder_Qty", ascending=False),
        use_container_width=True,
        height=450
    )

    top_reorder = reorder_df.sort_values(
        "Recommended_Reorder_Qty",
        ascending=False
    ).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Replenishment Summary</div>
        <div class="insight-body">
            The product with the highest recommended reorder quantity is
            <b>{top_reorder["Product_Name"]}</b> in <b>{top_reorder["Salon_Location"]}</b>.
            <br><br>
            Recommended reorder quantity:
            <b>{top_reorder["Recommended_Reorder_Qty"]:,.0f}</b> units.
            <br><br>
            This engine connects product demand forecasting with inventory planning, helping the business reduce stockout risk and improve replenishment decisions.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab22:

    st.markdown(
        '<div class="section-title">Academy & Training Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Training program analytics for students, attendance, course completion, revenue, and instructor performance.</div>',
        unsafe_allow_html=True
    )

    a1, a2, a3, a4 = st.columns(4)

    a1.metric("Total Students", f"{total_students:,}")
    a2.metric("Completion Rate", f"{completion_rate:.1f}%")
    a3.metric("Average Attendance", f"{avg_attendance:.1f}%")
    a4.metric("Academy Revenue", f"${academy_revenue:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Students by Course")

        fig_course = px.bar(
            course_summary.sort_values("Students", ascending=False),
            x="Course",
            y="Students",
            color="Graduation_Rate",
            text="Students",
            color_continuous_scale=[
                "#EFE2BD",
                "#C6A052",
                "#7D6838"
            ]
        )

        st.plotly_chart(
            chart_layout(fig_course, 520),
            use_container_width=True
        )

    with c2:
        st.markdown("### Revenue by Course")

        fig_course_revenue = px.bar(
            course_summary.sort_values("Revenue", ascending=False),
            x="Course",
            y="Revenue",
            color="Avg_Attendance",
            text="Revenue",
            color_continuous_scale=[
                "#EFE2BD",
                "#C6A052",
                "#7D6838"
            ]
        )

        st.plotly_chart(
            chart_layout(fig_course_revenue, 520),
            use_container_width=True
        )

    st.markdown("### Instructor Performance")

    fig_instructor = px.bar(
        instructor_summary.sort_values("Graduation_Rate", ascending=False),
        x="Instructor",
        y="Graduation_Rate",
        color="Avg_Attendance",
        text="Graduation_Rate",
        color_continuous_scale=[
            "#EFE2BD",
            "#C6A052",
            "#7D6838"
        ]
    )

    fig_instructor.update_traces(
        texttemplate="%{text:.1f}%"
    )

    st.plotly_chart(
        chart_layout(fig_instructor, 540),
        use_container_width=True
    )

    st.markdown("### Academy Detail Table")

    st.dataframe(
        academy_students,
        use_container_width=True,
        height=450
    )

    top_course = course_summary.sort_values(
        "Revenue",
        ascending=False
    ).iloc[0]["Course"]

    top_instructor = instructor_summary.sort_values(
        "Graduation_Rate",
        ascending=False
    ).iloc[0]["Instructor"]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Academy Summary</div>
        <div class="insight-body">
            The academy currently tracks <b>{total_students:,}</b> students across training programs.
            <br><br>
            The strongest revenue-generating course is <b>{top_course}</b>.
            <br><br>
            The strongest instructor by graduation rate is <b>{top_instructor}</b>.
            <br><br>
            This layer supports training program optimization, student lifecycle tracking,
            instructor performance analysis, and Academy operational decision-making.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab23:

    st.markdown(
        '<div class="section-title">Automated Data Validation & Governance Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Automated validation layer designed to detect missing, inconsistent, or risky data across market, sales, inventory, and academy operations.</div>',
        unsafe_allow_html=True
    )

    v1, v2, v3 = st.columns(3)

    v1.metric("Data Validation Score", f"{data_validation_score:.0f}/100")

    if validation_df.empty:
        total_issues = 0
        high_priority_issues = 0
    else:
        total_issues = validation_df["Issue_Count"].sum()
        high_priority_issues = validation_df[validation_df["Severity"] == "High"]["Issue_Count"].sum()

    v2.metric("Total Data Issues", f"{total_issues:,.0f}")
    v3.metric("High Priority Issues", f"{high_priority_issues:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    if validation_df.empty:
        st.success("No major data validation issues detected.")
    else:
        fig_validation = px.bar(
            validation_df,
            x="Dataset",
            y="Issue_Count",
            color="Severity",
            text="Issue_Count",
            color_discrete_map={
                "High": "#B22222",
                "Medium": "#C6A052",
                "Low": "#8A8A8A"
            }
        )

        st.plotly_chart(
            chart_layout(fig_validation, 520),
            use_container_width=True
        )

        st.markdown("### Data Validation Detail Table")

        st.dataframe(
            validation_df.sort_values("Issue_Count", ascending=False),
            use_container_width=True,
            height=420
        )

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Governance Interpretation</div>
        <div class="insight-body">
            This engine supports automated data validation across expansion, sales, inventory, and academy datasets.
            <br><br>
            Current data validation score: <b>{data_validation_score:.0f}/100</b>.
            <br><br>
            This directly supports data governance, master data quality, operational consistency, and scalable franchise decision-making.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab24:

    st.markdown(
        '<div class="section-title">Advanced AI Forecasting Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Machine learning demand forecasting with six-month predictions, confidence intervals, trend detection, anomaly detection, and forecast accuracy metrics.</div>',
        unsafe_allow_html=True
    )

    if ai_forecast_df.empty:
        st.warning("Not enough historical sales data to generate advanced AI forecasts. At least 6 months of product-level sales history is recommended.")

    else:
        avg_confidence = ai_forecast_df["Forecast_Confidence"].mean()
        avg_mape = forecast_accuracy_df["Forecast_MAPE"].mean()
        avg_rmse = forecast_accuracy_df["Forecast_RMSE"].mean()
        anomaly_count = len(forecast_anomaly_df)

        f1, f2, f3, f4 = st.columns(4)

        f1.metric("Avg Forecast Confidence", f"{avg_confidence:.1f}%")
        f2.metric("Avg MAPE", f"{avg_mape:.1f}%")
        f3.metric("Avg RMSE", f"{avg_rmse:.1f}")
        f4.metric("Detected Anomalies", f"{anomaly_count:,}")

        st.markdown("<br>", unsafe_allow_html=True)

        selected_forecast_product = st.selectbox(
            "Select Product for AI Forecast",
            sorted(ai_forecast_df["Product_Name"].unique())
        )

        product_ai_forecast = ai_forecast_df[
            ai_forecast_df["Product_Name"] == selected_forecast_product
        ].copy()

        fig_ai_forecast = px.line(
            product_ai_forecast,
            x="Forecast_Month",
            y="AI_Forecast_Units",
            color="Salon_Location",
            markers=True,
            title=f"6-Month AI Demand Forecast: {selected_forecast_product}"
        )

        fig_ai_forecast.update_traces(mode="lines+markers")

        st.plotly_chart(
            chart_layout(fig_ai_forecast, 540),
            use_container_width=True
        )

        st.markdown("### Forecast Detail with Confidence Intervals")

        st.dataframe(
            product_ai_forecast[[
                "Salon_Location",
                "Brand",
                "Product_Name",
                "Forecast_Month",
                "AI_Forecast_Units",
                "Forecast_Lower_Bound",
                "Forecast_Upper_Bound",
                "Forecast_MAPE",
                "Forecast_RMSE",
                "Forecast_Confidence"
            ]],
            use_container_width=True,
            height=420
        )

        st.markdown("### Forecast Accuracy & Trend Detection")

        st.dataframe(
            forecast_accuracy_df.sort_values(
                "Forecast_Confidence",
                ascending=False
            ),
            use_container_width=True,
            height=420
        )

        st.markdown("### Demand Anomaly Detection")

        if forecast_anomaly_df.empty:
            st.success("No major demand anomalies detected.")
        else:
            st.dataframe(
                forecast_anomaly_df.sort_values("Date", ascending=False),
                use_container_width=True,
                height=380
            )

        strongest_forecast = ai_forecast_df.sort_values(
            "AI_Forecast_Units",
            ascending=False
        ).iloc[0]

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Executive AI Forecasting Summary</div>
            <div class="insight-body">
                The advanced forecasting engine uses machine learning to estimate product demand for the next six months.
                <br><br>
                The strongest forecasted demand signal is for <b>{strongest_forecast["Product_Name"]}</b>
                at <b>{strongest_forecast["Salon_Location"]}</b>, with an expected demand of
                <b>{strongest_forecast["AI_Forecast_Units"]:,.0f}</b> units.
                <br><br>
                Average forecast confidence across available products is <b>{avg_confidence:.1f}%</b>.
                <br><br>
                This layer strengthens the platform’s alignment with AI-driven analytics, predictive modeling,
                inventory optimization, and data-driven supply chain decision-making.
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab25:

    st.markdown(
        '<div class="section-title">Advanced Supply Chain Optimization Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Enterprise supply chain logic with safety stock, service level optimization, lead time intelligence, supplier scorecards, ABC classification, stockout risk, inventory turnover, and logistics cost analysis.</div>',
        unsafe_allow_html=True
    )

    service_level_option = st.selectbox(
        "Select Target Service Level",
        ["95%", "98%", "99%"]
    )

    z_score_map = {
        "95%": 1.65,
        "98%": 2.05,
        "99%": 2.33
    }

    selected_z = z_score_map[service_level_option]

    temp_supply_df = supply_chain_df.copy()

    temp_supply_df["Safety_Stock"] = (
        selected_z
        * temp_supply_df["Demand_Std_Daily"]
        * np.sqrt(temp_supply_df["Lead_Time_Days"])
    ).round(0)

    temp_supply_df["Optimized_Reorder_Point"] = (
        temp_supply_df["Avg_Daily_Demand"] * temp_supply_df["Lead_Time_Days"]
        + temp_supply_df["Safety_Stock"]
    ).round(0)

    temp_supply_df["Optimized_Reorder_Qty"] = temp_supply_df.apply(
        lambda row: max(
            0,
            (row["Optimized_Reorder_Point"] + row["Forecast_Next_Month_Units"]) - row["Current_Stock"]
        ),
        axis=1
    ).round(0)

    temp_supply_df["Projected_Logistics_Cost"] = (
        temp_supply_df["Optimized_Reorder_Qty"]
        * temp_supply_df["Total_Logistics_Cost_Per_Unit"]
    ).round(2)

    high_risk_items = len(temp_supply_df[temp_supply_df["Supply_Chain_Risk_Level"] == "High Risk"])
    avg_stockout_risk = temp_supply_df["Stockout_Risk_%"].mean()
    total_safety_stock = temp_supply_df["Safety_Stock"].sum()
    total_logistics_cost = temp_supply_df["Projected_Logistics_Cost"].sum()

    s1, s2, s3, s4 = st.columns(4)

    s1.metric("High Risk Items", f"{high_risk_items:,}")
    s2.metric("Avg Stockout Risk", f"{avg_stockout_risk:.1f}%")
    s3.metric("Total Safety Stock", f"{total_safety_stock:,.0f}")
    s4.metric("Projected Logistics Cost", f"${total_logistics_cost:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Safety Stock by Product")

        fig_safety = px.bar(
            temp_supply_df.sort_values("Safety_Stock", ascending=False).head(15),
            x="Product_Name",
            y="Safety_Stock",
            color="ABC_Class",
            text="Safety_Stock",
            color_discrete_sequence=[
                GOLD,
                GOLD_LIGHT,
                "#7D6838"
            ]
        )

        st.plotly_chart(
            chart_layout(fig_safety, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### Stockout Risk by Product")

        fig_stockout = px.bar(
            temp_supply_df.sort_values("Stockout_Risk_%", ascending=False).head(15),
            x="Product_Name",
            y="Stockout_Risk_%",
            color="Supply_Chain_Risk_Level",
            text="Stockout_Risk_%",
            color_discrete_map={
                "High Risk": "#B22222",
                "Medium Risk": "#C6A052",
                "Low Risk": "#8A8A8A"
            }
        )

        st.plotly_chart(
            chart_layout(fig_stockout, 540),
            use_container_width=True
        )

    st.markdown("### Supplier Performance Scorecard")

    fig_supplier = px.bar(
        supplier_scorecard_df.sort_values("Avg_Performance_Score", ascending=False),
        x="Supplier",
        y="Avg_Performance_Score",
        color="High_Risk_Items",
        text="Avg_Performance_Score",
        color_continuous_scale=[
            "#EFE2BD",
            "#C6A052",
            "#7D6838"
        ]
    )

    st.plotly_chart(
        chart_layout(fig_supplier, 520),
        use_container_width=True
    )

    st.dataframe(
        supplier_scorecard_df,
        use_container_width=True,
        height=360
    )

    st.markdown("### ABC Inventory Classification")

    abc_summary = temp_supply_df.groupby(
        "ABC_Class",
        as_index=False
    ).agg(
        Products=("Product_ID", "count"),
        Total_Current_Stock=("Current_Stock", "sum"),
        Total_Safety_Stock=("Safety_Stock", "sum"),
        Total_Optimized_Reorder_Qty=("Optimized_Reorder_Qty", "sum"),
        Avg_Stockout_Risk=("Stockout_Risk_%", "mean"),
        Avg_Inventory_Turnover=("Inventory_Turnover", "mean")
    )

    fig_abc = px.pie(
        abc_summary,
        names="ABC_Class",
        values="Products",
        color_discrete_sequence=[
            GOLD,
            GOLD_LIGHT,
            "#7D6838"
        ]
    )

    st.plotly_chart(
        chart_layout(fig_abc, 480),
        use_container_width=True
    )

    st.dataframe(
        abc_summary,
        use_container_width=True,
        height=280
    )

    st.markdown("### Advanced Supply Chain Detail Table")

    detail_cols = [
        "Salon_Location",
        "Supplier",
        "Brand",
        "Product_Name",
        "ABC_Class",
        "Current_Stock",
        "Forecast_Next_Month_Units",
        "Lead_Time_Days",
        "Safety_Stock",
        "Optimized_Reorder_Point",
        "Optimized_Reorder_Qty",
        "Stockout_Risk_%",
        "Inventory_Turnover",
        "Supplier_Performance_Score",
        "Total_Logistics_Cost_Per_Unit",
        "Projected_Logistics_Cost",
        "Supply_Chain_Risk_Level"
    ]

    available_detail_cols = [
        col for col in detail_cols
        if col in temp_supply_df.columns
    ]

    st.dataframe(
        temp_supply_df[available_detail_cols].sort_values(
            "Stockout_Risk_%",
            ascending=False
        ),
        use_container_width=True,
        height=480
    )

    highest_risk_item = temp_supply_df.sort_values(
        "Stockout_Risk_%",
        ascending=False
    ).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Supply Chain Optimization Summary</div>
        <div class="insight-body">
            Under a <b>{service_level_option}</b> target service level, the engine recommends a total safety stock of
            <b>{total_safety_stock:,.0f}</b> units across the analyzed product portfolio.
            <br><br>
            The highest stockout risk item is <b>{highest_risk_item["Product_Name"]}</b>,
            with a stockout risk of <b>{highest_risk_item["Stockout_Risk_%"]:.1f}%</b>.
            <br><br>
            This layer strengthens the platform’s alignment with enterprise supply chain optimization,
            supplier performance analytics, lead time intelligence, inventory risk management,
            and logistics cost optimization.
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab26:

    st.markdown(
        '<div class="section-title">Franchise Performance Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Operational intelligence for franchise locations, salons, and academy performance alignment.</div>',
        unsafe_allow_html=True
    )

    fp1, fp2, fp3, fp4 = st.columns(4)

    total_franchise_locations = len(franchise_ops_df)
    total_franchise_revenue = franchise_ops_df["Monthly_Revenue"].sum()
    total_franchise_profit = franchise_ops_df["Monthly_Profit"].sum()
    avg_franchise_score = franchise_ops_df["Franchise_Operational_Score"].mean()

    fp1.metric("Locations Tracked", f"{total_franchise_locations:,}")
    fp2.metric("Monthly Revenue", f"${total_franchise_revenue:,.0f}")
    fp3.metric("Monthly Profit", f"${total_franchise_profit:,.0f}")
    fp4.metric("Avg Operational Score", f"{avg_franchise_score:.1f}/100")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Operational Score by Location")

        fig_franchise_score = px.bar(
            franchise_ops_df.sort_values("Franchise_Operational_Score", ascending=False),
            x="Location_Name",
            y="Franchise_Operational_Score",
            color="Performance_Tier",
            text="Franchise_Operational_Score",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
        )

        fig_franchise_score.update_traces(texttemplate="%{text:.1f}", textposition="outside")

        st.plotly_chart(
            chart_layout(fig_franchise_score, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### Location Maturity")

        maturity_summary = franchise_ops_df.groupby(
            "Location_Maturity",
            as_index=False
        ).agg(
            Locations=("Location_Name", "count"),
            Avg_Operational_Score=("Franchise_Operational_Score", "mean")
        )

        fig_maturity = px.pie(
            maturity_summary,
            names="Location_Maturity",
            values="Locations",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838"]
        )

        st.plotly_chart(
            chart_layout(fig_maturity, 540),
            use_container_width=True
        )

    st.markdown("### Franchise Operational Detail")

    franchise_display_cols = [
        "Location_Name",
        "Location_Type",
        "Owner_Type",
        "Monthly_Revenue",
        "Monthly_Cost",
        "Monthly_Profit",
        "Profit_Margin_%",
        "Chairs",
        "Stylists",
        "Revenue_Per_Chair",
        "Revenue_Per_Stylist",
        "Months_Open",
        "Location_Maturity",
        "Franchise_Operational_Score",
        "Performance_Tier"
    ]

    st.dataframe(
        franchise_ops_df[franchise_display_cols].sort_values(
            "Franchise_Operational_Score",
            ascending=False
        ),
        use_container_width=True,
        height=460
    )

    best_franchise_location = franchise_ops_df.sort_values(
        "Franchise_Operational_Score",
        ascending=False
    ).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Franchise Performance Summary</div>
        <div class="insight-body">
            <b>{best_franchise_location["Location_Name"]}</b> is currently the strongest operating location based on the composite operational score.
            <br><br>
            The score combines revenue performance, profitability, productivity per stylist, and location maturity.
            <br><br>
            This layer helps Gabriel Samra compare company-owned salons, franchise locations, and the Academy using one consistent operational intelligence framework.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab27:

    st.markdown(
        '<div class="section-title">Franchise Profitability Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Profitability, revenue per chair, revenue per stylist, and margin benchmarking by location.</div>',
        unsafe_allow_html=True
    )

    pr1, pr2, pr3, pr4 = st.columns(4)

    avg_profit_margin = franchise_ops_df["Profit_Margin_%"].mean()
    avg_revenue_per_chair = franchise_ops_df[franchise_ops_df["Chairs"] > 0]["Revenue_Per_Chair"].mean()
    avg_revenue_per_stylist = franchise_ops_df[franchise_ops_df["Stylists"] > 0]["Revenue_Per_Stylist"].mean()
    profitable_locations = len(franchise_ops_df[franchise_ops_df["Monthly_Profit"] > 0])

    pr1.metric("Avg Profit Margin", f"{avg_profit_margin:.1f}%")
    pr2.metric("Avg Revenue / Chair", f"${avg_revenue_per_chair:,.0f}")
    pr3.metric("Avg Revenue / Stylist", f"${avg_revenue_per_stylist:,.0f}")
    pr4.metric("Profitable Locations", f"{profitable_locations:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Monthly Revenue vs Cost")

        revenue_cost_franchise = franchise_ops_df.melt(
            id_vars="Location_Name",
            value_vars=["Monthly_Revenue", "Monthly_Cost"],
            var_name="Metric",
            value_name="Amount"
        )

        fig_franchise_revenue_cost = px.bar(
            revenue_cost_franchise,
            x="Location_Name",
            y="Amount",
            color="Metric",
            barmode="group",
            text="Amount",
            color_discrete_sequence=[GOLD_LIGHT, "#8C6F2F"]
        )

        st.plotly_chart(
            chart_layout(fig_franchise_revenue_cost, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### Profit Margin by Location")

        fig_margin = px.bar(
            franchise_ops_df.sort_values("Profit_Margin_%", ascending=False),
            x="Location_Name",
            y="Profit_Margin_%",
            color="Performance_Tier",
            text="Profit_Margin_%",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
        )

        fig_margin.update_traces(texttemplate="%{text:.1f}%", textposition="outside")

        st.plotly_chart(
            chart_layout(fig_margin, 540),
            use_container_width=True
        )

    st.markdown("### Productivity Benchmarking")

    productivity_df = franchise_ops_df[
        franchise_ops_df["Location_Type"].isin(["Salon", "Franchise"])
    ].copy()

    if productivity_df.empty:
        st.warning("No salon or franchise locations available for productivity benchmarking.")
    else:
        fig_productivity = px.scatter(
            productivity_df,
            x="Revenue_Per_Chair",
            y="Revenue_Per_Stylist",
            size="Monthly_Revenue",
            color="Location_Type",
            hover_name="Location_Name",
            hover_data={
                "Profit_Margin_%": ":.1f",
                "Franchise_Operational_Score": ":.1f"
            },
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838"]
        )

        st.plotly_chart(
            chart_layout(fig_productivity, 560),
            use_container_width=True
        )

    st.dataframe(
        franchise_ops_df[[
            "Location_Name",
            "Location_Type",
            "Monthly_Revenue",
            "Monthly_Cost",
            "Monthly_Profit",
            "Profit_Margin_%",
            "Revenue_Per_Chair",
            "Revenue_Per_Stylist",
            "Revenue_Per_Customer",
            "Performance_Tier"
        ]].sort_values("Monthly_Profit", ascending=False),
        use_container_width=True,
        height=430
    )

with tab28:

    st.markdown(
        '<div class="section-title">Multi-Location Benchmarking</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Compares salons, academy, and franchise locations under one executive benchmarking view.</div>',
        unsafe_allow_html=True
    )

    b1, b2 = st.columns([1, 1])

    with b1:
        st.markdown("### Performance by Business Type")

        fig_type_score = px.bar(
            franchise_type_summary.sort_values("Avg_Operational_Score", ascending=False),
            x="Location_Type",
            y="Avg_Operational_Score",
            color="Location_Type",
            text="Avg_Operational_Score",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
        )

        fig_type_score.update_traces(texttemplate="%{text:.1f}", textposition="outside")

        st.plotly_chart(
            chart_layout(fig_type_score, 520),
            use_container_width=True
        )

    with b2:
        st.markdown("### Profit by Business Type")

        fig_type_profit = px.bar(
            franchise_type_summary.sort_values("Monthly_Profit", ascending=False),
            x="Location_Type",
            y="Monthly_Profit",
            color="Location_Type",
            text="Monthly_Profit",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
        )

        st.plotly_chart(
            chart_layout(fig_type_profit, 520),
            use_container_width=True
        )

    st.markdown("### Business Type Benchmark Table")

    st.dataframe(
        franchise_type_summary.sort_values("Avg_Operational_Score", ascending=False),
        use_container_width=True,
        height=320
    )

    st.markdown("### Location Benchmark Matrix")

    fig_benchmark_matrix = px.scatter(
        franchise_ops_df,
        x="Profit_Margin_%",
        y="Franchise_Operational_Score",
        size="Monthly_Revenue",
        color="Location_Type",
        hover_name="Location_Name",
        hover_data={
            "Revenue_Per_Chair": ":,.0f",
            "Revenue_Per_Stylist": ":,.0f",
            "Location_Maturity": True,
            "Performance_Tier": True
        },
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
    )

    fig_benchmark_matrix.add_hline(
        y=65,
        line_dash="dash",
        line_color="#7A6330",
        annotation_text="Strong performance threshold",
        annotation_position="top left"
    )

    st.plotly_chart(
        chart_layout(fig_benchmark_matrix, 560),
        use_container_width=True
    )

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Multi-Location Benchmarking Summary</div>
        <div class="insight-body">
            This benchmarking layer creates a single comparison view across salons, franchise locations, and the Academy.
            <br><br>
            It helps leadership identify which business model is generating stronger revenue, profitability, productivity, and operational maturity.
            <br><br>
            For Gabriel Samra alignment, this strengthens the platform beyond market expansion by connecting strategy with real franchise operating performance.
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab29:

    st.markdown(
        '<div class="section-title">CRM / Customer Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Customer segmentation, repeat visit behavior, lifetime value, booking frequency, and customer value scoring.</div>',
        unsafe_allow_html=True
    )

    total_customers = customer_summary_df["Customer_ID"].nunique()
    repeat_customers = len(customer_summary_df[customer_summary_df["Total_Visits"] >= 2])
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    avg_clv = customer_summary_df["Estimated_CLV"].mean() if not customer_summary_df.empty else 0
    avg_booking_frequency = customer_summary_df["Booking_Frequency_Per_Month"].mean() if not customer_summary_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Customers", f"{total_customers:,}")
    c2.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")
    c3.metric("Avg Estimated CLV", f"${avg_clv:,.0f}")
    c4.metric("Avg Booking Frequency", f"{avg_booking_frequency:.2f} / month")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown("### Customer Segments")

        fig_segments = px.bar(
            customer_segment_summary_df.sort_values("Total_Revenue", ascending=False),
            x="Customer_Segment",
            y="Total_Revenue",
            color="Customer_Segment",
            text="Total_Revenue",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838", "#8A8A8A"]
        )

        st.plotly_chart(
            chart_layout(fig_segments, 520),
            use_container_width=True
        )

    with right:
        st.markdown("### Customer Value vs Churn Risk")

        fig_value_risk = px.scatter(
            customer_summary_df,
            x="Customer_Value_Score",
            y="Churn_Risk_%",
            size="Total_Revenue",
            color="Customer_Segment",
            hover_name="Customer_Name",
            hover_data={
                "Total_Visits": True,
                "Estimated_CLV": ":,.0f",
                "Days_Since_Last_Visit": True,
                "Favorite_Location": True
            },
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838", "#8A8A8A"]
        )

        st.plotly_chart(
            chart_layout(fig_value_risk, 520),
            use_container_width=True
        )

    st.markdown("### Customer Segment Summary")

    st.dataframe(
        customer_segment_summary_df.sort_values("Total_Revenue", ascending=False),
        use_container_width=True,
        height=320
    )

    st.markdown("### Customer Detail Table")

    customer_detail_cols = [
        "Customer_ID",
        "Customer_Name",
        "Customer_Segment",
        "Total_Revenue",
        "Total_Visits",
        "Avg_Ticket",
        "Estimated_CLV",
        "Booking_Frequency_Per_Month",
        "Days_Since_Last_Visit",
        "Churn_Risk_%",
        "Retention_Status",
        "Favorite_Location",
        "Primary_Channel"
    ]

    st.dataframe(
        customer_summary_df
            .sort_values("Customer_Value_Score", ascending=False)
            [customer_detail_cols],
        use_container_width=True,
        height=460
    )

    top_customer = customer_summary_df.sort_values("Estimated_CLV", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Customer Intelligence Summary</div>
        <div class="insight-body">
            The CRM intelligence layer identifies <b>{total_customers:,}</b> customers with a repeat customer rate of
            <b>{repeat_rate:.1f}%</b>.
            <br><br>
            The highest estimated lifetime value customer is <b>{top_customer["Customer_Name"]}</b>, with an estimated CLV of
            <b>${top_customer["Estimated_CLV"]:,.0f}</b>.
            <br><br>
            This layer strengthens digital transformation alignment by connecting operating data to customer behavior,
            retention, segmentation, booking patterns, and revenue quality.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab30:

    st.markdown(
        '<div class="section-title">Retention & Churn Analytics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Repeat visit analysis, churn risk, retention status, days since last visit, and booking frequency intelligence.</div>',
        unsafe_allow_html=True
    )

    active_customers = len(customer_summary_df[customer_summary_df["Retention_Status"] == "Active"])
    at_risk_customers = len(customer_summary_df[customer_summary_df["Retention_Status"] == "At Risk"])
    churned_customers = len(customer_summary_df[customer_summary_df["Retention_Status"] == "Likely Churned"])
    avg_churn_risk = customer_summary_df["Churn_Risk_%"].mean() if not customer_summary_df.empty else 0

    r1, r2, r3, r4 = st.columns(4)

    r1.metric("Active Customers", f"{active_customers:,}")
    r2.metric("At-Risk Customers", f"{at_risk_customers:,}")
    r3.metric("Likely Churned", f"{churned_customers:,}")
    r4.metric("Avg Churn Risk", f"{avg_churn_risk:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Retention Status Mix")

        retention_summary = customer_summary_df.groupby(
            "Retention_Status",
            as_index=False
        ).agg(
            Customers=("Customer_ID", "count"),
            Revenue=("Total_Revenue", "sum"),
            Avg_Churn_Risk=("Churn_Risk_%", "mean")
        )

        fig_retention = px.pie(
            retention_summary,
            names="Retention_Status",
            values="Customers",
            color_discrete_sequence=[GOLD, GOLD_LIGHT, "#B22222"]
        )

        st.plotly_chart(
            chart_layout(fig_retention, 500),
            use_container_width=True
        )

    with c2:
        st.markdown("### Monthly Visits and Customer Activity")

        fig_monthly_customers = px.line(
            monthly_customer_trend_df,
            x="Visit_Month",
            y=["Visits", "Unique_Customers"],
            markers=True
        )

        st.plotly_chart(
            chart_layout(fig_monthly_customers, 500),
            use_container_width=True
        )

    st.markdown("### Highest Churn Risk Customers")

    st.dataframe(
        customer_summary_df[[
            "Customer_ID",
            "Customer_Name",
            "Customer_Segment",
            "Retention_Status",
            "Total_Revenue",
            "Total_Visits",
            "Days_Since_Last_Visit",
            "Booking_Frequency_Per_Month",
            "Avg_Satisfaction",
            "Churn_Risk_%",
            "Favorite_Location",
            "Primary_Campaign"
        ]].sort_values("Churn_Risk_%", ascending=False),
        use_container_width=True,
        height=460
    )

    high_risk_value = customer_summary_df[
        customer_summary_df["Churn_Risk_%"] >= 60
    ]["Total_Revenue"].sum()

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Retention Summary</div>
        <div class="insight-body">
            The model currently identifies <b>{at_risk_customers + churned_customers:,}</b> customers requiring retention attention.
            <br><br>
            Revenue historically associated with customers above 60% churn risk is approximately
            <b>${high_risk_value:,.0f}</b>.
            <br><br>
            Recommended management action: prioritize reactivation campaigns for high-value customers with high churn risk,
            especially those with strong prior spend but long time since last visit.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab31:

    st.markdown(
        '<div class="section-title">Campaign Attribution & Booking Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Campaign attribution, booking channel performance, revenue per customer, and location-level customer analytics.</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Revenue by Campaign Source")

        fig_campaign = px.bar(
            campaign_attribution_df.sort_values("Revenue", ascending=False),
            x="Campaign_Source",
            y="Revenue",
            color="Campaign_Source",
            text="Revenue",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838", "#8A8A8A"]
        )

        st.plotly_chart(
            chart_layout(fig_campaign, 520),
            use_container_width=True
        )

    with c2:
        st.markdown("### Booking Channel Revenue")

        booking_channel_df = crm_df.groupby(
            "Booking_Channel",
            as_index=False
        ).agg(
            Visits=("Visit_ID", "count"),
            Customers=("Customer_ID", "nunique"),
            Revenue=("Net_Revenue", "sum"),
            Avg_Ticket=("Net_Revenue", "mean")
        )

        fig_channel = px.bar(
            booking_channel_df.sort_values("Revenue", ascending=False),
            x="Booking_Channel",
            y="Revenue",
            color="Booking_Channel",
            text="Revenue",
            color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838", "#8A8A8A"]
        )

        st.plotly_chart(
            chart_layout(fig_channel, 520),
            use_container_width=True
        )

    st.markdown("### Location-Level Customer Intelligence")

    fig_location_customer = px.scatter(
        location_customer_df,
        x="Customers",
        y="Revenue_Per_Customer",
        size="Revenue",
        color="Salon_Location",
        hover_name="Salon_Location",
        hover_data={
            "Visits": True,
            "Revenue": ":,.0f",
            "Avg_Ticket": ":,.0f",
            "Avg_Satisfaction": ":.1f"
        },
        color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838", "#8A8A8A"]
    )

    st.plotly_chart(
        chart_layout(fig_location_customer, 540),
        use_container_width=True
    )

    st.markdown("### Campaign Attribution Table")

    st.dataframe(
        campaign_attribution_df.sort_values("Revenue", ascending=False),
        use_container_width=True,
        height=320
    )

    st.markdown("### Booking Channel Table")

    st.dataframe(
        booking_channel_df.sort_values("Revenue", ascending=False),
        use_container_width=True,
        height=280
    )

    best_campaign = campaign_attribution_df.sort_values("Revenue", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Campaign Attribution Summary</div>
        <div class="insight-body">
            The strongest campaign source is <b>{best_campaign["Campaign_Source"]}</b>, generating approximately
            <b>${best_campaign["Revenue"]:,.0f}</b> in attributed revenue.
            <br><br>
            This layer supports enterprise CRM intelligence by connecting marketing campaigns, booking behavior,
            customer value, retention risk, and location-level revenue performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab32:

    st.markdown(
        '<div class="section-title">Transformation Governance & Change Management Framework</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Enterprise change management layer tracking adoption KPIs, organizational readiness, resistance, change velocity, and executive implementation roadmap.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # SAMPLE TRANSFORMATION GOVERNANCE DATA
    # -----------------------------

    transformation_df = pd.DataFrame({
        "Department": [
            "Salon Operations",
            "Academy",
            "Franchise Operations",
            "Marketing",
            "Finance",
            "Leadership"
        ],
        "System_Adoption_Rate": [82, 76, 69, 88, 73, 91],
        "Active_Users": [34, 18, 22, 12, 9, 6],
        "Training_Completion": [79, 84, 65, 92, 71, 100],
        "Process_Compliance": [74, 81, 62, 86, 77, 94],
        "Stakeholder_Alignment": [80, 78, 66, 89, 75, 95],
        "Implementation_Resistance": [28, 22, 41, 18, 30, 10],
        "Change_Velocity": [72, 69, 58, 84, 64, 90]
    })

    transformation_df["Transformation_Maturity_Score"] = (
        transformation_df["System_Adoption_Rate"] * 0.20
        + transformation_df["Training_Completion"] * 0.20
        + transformation_df["Process_Compliance"] * 0.20
        + transformation_df["Stakeholder_Alignment"] * 0.20
        + transformation_df["Change_Velocity"] * 0.15
        + (100 - transformation_df["Implementation_Resistance"]) * 0.05
    ).round(1)

    transformation_df["Readiness_Level"] = transformation_df["Transformation_Maturity_Score"].apply(
        lambda score:
        "High Readiness" if score >= 80
        else "Moderate Readiness" if score >= 65
        else "Needs Intervention"
    )

    avg_adoption = transformation_df["System_Adoption_Rate"].mean()
    avg_training = transformation_df["Training_Completion"].mean()
    avg_maturity = transformation_df["Transformation_Maturity_Score"].mean()
    avg_resistance = transformation_df["Implementation_Resistance"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("System Adoption Rate", f"{avg_adoption:.1f}%")
    c2.metric("Training Completion", f"{avg_training:.1f}%")
    c3.metric("Transformation Maturity", f"{avg_maturity:.1f}/100")
    c4.metric("Implementation Resistance", f"{avg_resistance:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # ADOPTION KPI DASHBOARD
    # -----------------------------

    left, right = st.columns(2)

    with left:
        st.markdown("### Adoption KPIs by Department")

        fig_adoption = px.bar(
            transformation_df,
            x="Department",
            y="System_Adoption_Rate",
            color="Readiness_Level",
            text="System_Adoption_Rate",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#7D6838"
            ]
        )

        fig_adoption.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_adoption, 520),
            use_container_width=True
        )

    with right:
        st.markdown("### Transformation Maturity Score")

        fig_maturity = px.bar(
            transformation_df.sort_values("Transformation_Maturity_Score", ascending=False),
            x="Department",
            y="Transformation_Maturity_Score",
            color="Readiness_Level",
            text="Transformation_Maturity_Score",
            color_discrete_sequence=[
                GOLD,
                GOLD_LIGHT,
                "#7D6838"
            ]
        )

        fig_maturity.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_maturity, 520),
            use_container_width=True
        )

    # -----------------------------
    # ORGANIZATIONAL READINESS
    # -----------------------------

    st.markdown("### Organizational Readiness & Resistance Analysis")

    readiness_cols = [
        "Department",
        "Stakeholder_Alignment",
        "Training_Completion",
        "Process_Compliance",
        "Implementation_Resistance",
        "Change_Velocity",
        "Transformation_Maturity_Score",
        "Readiness_Level"
    ]

    st.dataframe(
        transformation_df[readiness_cols].sort_values(
            "Transformation_Maturity_Score",
            ascending=False
        ),
        use_container_width=True,
        height=380
    )

    st.markdown("<br>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("### Resistance by Department")

        fig_resistance = px.bar(
            transformation_df.sort_values("Implementation_Resistance", ascending=False),
            x="Department",
            y="Implementation_Resistance",
            color="Readiness_Level",
            text="Implementation_Resistance",
            color_discrete_sequence=[
                "#B22222",
                GOLD,
                GOLD_LIGHT
            ]
        )

        fig_resistance.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_resistance, 500),
            use_container_width=True
        )

    with r2:
        st.markdown("### Change Velocity")

        fig_velocity = px.bar(
            transformation_df.sort_values("Change_Velocity", ascending=False),
            x="Department",
            y="Change_Velocity",
            color="Readiness_Level",
            text="Change_Velocity",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#7D6838"
            ]
        )

        fig_velocity.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_velocity, 500),
            use_container_width=True
        )

    # -----------------------------
    # EXECUTIVE ROADMAP
    # -----------------------------

    st.markdown("### Executive Transformation Roadmap")

    roadmap_df = pd.DataFrame({
        "Phase": [
            "Phase 1",
            "Phase 2",
            "Phase 3"
        ],
        "Focus": [
            "Foundation & Alignment",
            "Adoption & Process Integration",
            "Scale, Governance & Continuous Improvement"
        ],
        "Milestones": [
            "Define ownership, confirm KPIs, train department leaders, validate data readiness.",
            "Increase active users, standardize process compliance, monitor resistance, improve reporting cadence.",
            "Scale governance routines, automate executive dashboards, benchmark locations, institutionalize continuous improvement."
        ],
        "Target_Timeframe": [
            "0–30 Days",
            "31–90 Days",
            "90–180 Days"
        ],
        "Success_Metric": [
            "Leadership alignment above 85%",
            "System adoption above 80%",
            "Transformation maturity above 85/100"
        ]
    })

    st.dataframe(
        roadmap_df,
        use_container_width=True,
        height=260
    )

    weakest_department = transformation_df.sort_values(
        "Transformation_Maturity_Score",
        ascending=True
    ).iloc[0]

    strongest_department = transformation_df.sort_values(
        "Transformation_Maturity_Score",
        ascending=False
    ).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Transformation Governance Summary</div>
        <div class="insight-body">
            The strongest transformation readiness signal is currently in
            <b>{strongest_department["Department"]}</b>, with a maturity score of
            <b>{strongest_department["Transformation_Maturity_Score"]:.1f}/100</b>.
            <br><br>
            The department requiring the most change management attention is
            <b>{weakest_department["Department"]}</b>, with a maturity score of
            <b>{weakest_department["Transformation_Maturity_Score"]:.1f}/100</b>.
            <br><br>
            This governance layer strengthens the platform by moving beyond a simple change readiness score
            into adoption KPIs, organizational readiness, resistance tracking, change velocity,
            and an executive transformation roadmap.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab33:

    st.markdown(
        '<div class="section-title">Data Governance Maturity Model</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Enterprise governance layer evaluating ownership, stewardship, master data consistency, duplicates, policy maturity, lineage, auditability, and source trust.</div>',
        unsafe_allow_html=True
    )

    governance_maturity_df = pd.DataFrame({
        "Domain": [
            "Market Expansion Data",
            "Sales Transactions",
            "Inventory Master Data",
            "Academy Data",
            "Franchise Data",
            "CRM / Customer Data"
        ],
        "Data_Ownership": [78, 72, 69, 75, 66, 62],
        "Data_Stewardship": [74, 70, 68, 73, 61, 59],
        "Master_Data_Consistency": [82, 76, 71, 79, 64, 60],
        "Duplicate_Control": [80, 73, 70, 76, 62, 58],
        "Governance_Policy_Score": [76, 69, 67, 72, 60, 57],
        "Lineage": [71, 66, 63, 68, 55, 52],
        "Auditability": [79, 74, 70, 77, 63, 61],
        "Source_Trust": [84, 78, 72, 80, 65, 62]
    })

    governance_maturity_df["Governance_Maturity_Score"] = (
        governance_maturity_df["Data_Ownership"] * 0.15
        + governance_maturity_df["Data_Stewardship"] * 0.15
        + governance_maturity_df["Master_Data_Consistency"] * 0.15
        + governance_maturity_df["Duplicate_Control"] * 0.12
        + governance_maturity_df["Governance_Policy_Score"] * 0.13
        + governance_maturity_df["Lineage"] * 0.10
        + governance_maturity_df["Auditability"] * 0.10
        + governance_maturity_df["Source_Trust"] * 0.10
    ).round(1)

    governance_maturity_df["Maturity_Level"] = governance_maturity_df["Governance_Maturity_Score"].apply(
        lambda score:
        "Optimized" if score >= 85
        else "Managed" if score >= 75
        else "Developing" if score >= 65
        else "Foundational"
    )

    avg_governance_maturity = governance_maturity_df["Governance_Maturity_Score"].mean()
    avg_ownership = governance_maturity_df["Data_Ownership"].mean()
    avg_lineage = governance_maturity_df["Lineage"].mean()
    avg_source_trust = governance_maturity_df["Source_Trust"].mean()

    g1, g2, g3, g4 = st.columns(4)

    g1.metric("Governance Maturity", f"{avg_governance_maturity:.1f}/100")
    g2.metric("Data Ownership", f"{avg_ownership:.1f}%")
    g3.metric("Lineage Score", f"{avg_lineage:.1f}%")
    g4.metric("Source Trust", f"{avg_source_trust:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Governance Maturity by Data Domain")

        fig_gov = px.bar(
            governance_maturity_df.sort_values("Governance_Maturity_Score", ascending=False),
            x="Domain",
            y="Governance_Maturity_Score",
            color="Maturity_Level",
            text="Governance_Maturity_Score",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838"
            ]
        )

        fig_gov.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_gov, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### Source Trust Scoring")

        fig_trust = px.bar(
            governance_maturity_df.sort_values("Source_Trust", ascending=False),
            x="Domain",
            y="Source_Trust",
            color="Maturity_Level",
            text="Source_Trust",
            color_discrete_sequence=[
                GOLD,
                GOLD_LIGHT,
                "#7D6838",
                "#A9843C"
            ]
        )

        fig_trust.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_trust, 540),
            use_container_width=True
        )

    st.markdown("### Data Governance Detail Table")

    st.dataframe(
        governance_maturity_df.sort_values(
            "Governance_Maturity_Score",
            ascending=False
        ),
        use_container_width=True,
        height=420
    )

    st.markdown("### Governance Risk Register")

    governance_risks_df = pd.DataFrame({
        "Governance_Risk": [
            "Unclear data ownership",
            "Weak stewardship routines",
            "Inconsistent master data",
            "Duplicate customer or product records",
            "Limited data lineage",
            "Low auditability",
            "Untrusted source systems"
        ],
        "Business_Impact": [
            "No clear accountability for fixing data issues.",
            "Data issues may repeat because no one owns monitoring routines.",
            "Reports may conflict across departments.",
            "Customer, inventory, or franchise reporting may be overstated or duplicated.",
            "Leadership cannot easily trace where numbers came from.",
            "Difficult to prove data quality during executive reviews.",
            "Decisions may rely on incomplete or unreliable source data."
        ],
        "Recommended_Action": [
            "Assign a business owner for each key data domain.",
            "Create data steward responsibilities and recurring review cadence.",
            "Define master data rules for products, locations, customers, and franchise entities.",
            "Create duplicate detection logic and monthly cleanup review.",
            "Document source-to-report data flow.",
            "Maintain change logs, validation checks, and approval history.",
            "Score each source by completeness, freshness, and reliability."
        ]
    })

    st.dataframe(
        governance_risks_df,
        use_container_width=True,
        height=360
    )

    weakest_domain = governance_maturity_df.sort_values(
        "Governance_Maturity_Score",
        ascending=True
    ).iloc[0]

    strongest_domain = governance_maturity_df.sort_values(
        "Governance_Maturity_Score",
        ascending=False
    ).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Data Governance Summary</div>
        <div class="insight-body">
            The strongest data governance domain is <b>{strongest_domain["Domain"]}</b>,
            with a maturity score of <b>{strongest_domain["Governance_Maturity_Score"]:.1f}/100</b>.
            <br><br>
            The weakest governance domain is <b>{weakest_domain["Domain"]}</b>,
            with a maturity score of <b>{weakest_domain["Governance_Maturity_Score"]:.1f}/100</b>.
            <br><br>
            This layer moves the platform beyond simple completeness scoring by adding data ownership,
            stewardship, master data consistency, duplicate control, governance policy scoring,
            lineage, auditability, and source trust scoring.
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab34:

    st.markdown(
        '<div class="section-title">Executive Simulation Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Monte Carlo risk analytics for best case, worst case, volatility scenarios, probabilistic ROI, and executive what-if simulation.</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">Simulation Question</div>
        <div class="insight-body">
            This engine answers questions like:
            <br><br>
            <b>What happens if rent increases, customer volume decreases, and revenue becomes volatile?</b>
            <br><br>
            Instead of showing one fixed result, it runs thousands of possible outcomes and estimates the probability of positive ROI, downside risk, upside potential, and expected profit.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    selected_market_row = filtered.iloc[0].copy()

    base_rent = float(selected_market_row["Estimated_Monthly_Rent"])
    base_revenue = float(selected_market_row["Estimated_Monthly_Revenue"])
    base_cost = float(selected_market_row["Estimated_Monthly_Cost"])
    base_non_rent_cost = max(0, base_cost - base_rent)

    s_col1, s_col2, s_col3 = st.columns(3)

    with s_col1:
        simulated_rent_change = st.slider(
            "Simulated Rent Change %",
            -50,
            100,
            30,
            key="simulated_rent_change"
        )

    with s_col2:
        simulated_customer_volume_change = st.slider(
            "Simulated Customer Volume Change %",
            -50,
            100,
            -15,
            key="simulated_customer_volume_change"
        )

    with s_col3:
        simulated_ticket_change = st.slider(
            "Simulated Ticket / Pricing Change %",
            -50,
            100,
            0,
            key="simulated_ticket_change"
        )

    v_col1, v_col2, v_col3 = st.columns(3)

    with v_col1:
        revenue_volatility = st.slider(
            "Revenue Volatility %",
            0,
            50,
            12,
            key="revenue_volatility"
        )

    with v_col2:
        cost_volatility = st.slider(
            "Cost Volatility %",
            0,
            50,
            8,
            key="cost_volatility"
        )

    with v_col3:
        simulation_runs = st.selectbox(
            "Simulation Runs",
            [1000, 5000, 10000],
            index=1,
            key="simulation_runs"
        )

    np.random.seed(42)

    expected_revenue = (
        base_revenue
        * (1 + simulated_ticket_change / 100)
        * (1 + simulated_customer_volume_change / 100)
    )

    expected_rent = base_rent * (1 + simulated_rent_change / 100)
    expected_cost = base_non_rent_cost + expected_rent

    simulated_revenue = np.random.normal(
        loc=expected_revenue,
        scale=max(1, expected_revenue * revenue_volatility / 100),
        size=simulation_runs
    )

    simulated_rent = np.random.normal(
        loc=expected_rent,
        scale=max(1, expected_rent * cost_volatility / 100),
        size=simulation_runs
    )

    simulated_non_rent_cost = np.random.normal(
        loc=base_non_rent_cost,
        scale=max(1, base_non_rent_cost * cost_volatility / 100),
        size=simulation_runs
    )

    simulated_revenue = np.maximum(simulated_revenue, 0)
    simulated_rent = np.maximum(simulated_rent, 0)
    simulated_non_rent_cost = np.maximum(simulated_non_rent_cost, 0)

    simulated_total_cost = simulated_rent + simulated_non_rent_cost
    simulated_profit = simulated_revenue - simulated_total_cost

    simulated_roi = np.where(
        simulated_total_cost > 0,
        simulated_profit / simulated_total_cost,
        0
    )

    simulation_df = pd.DataFrame({
        "Scenario_Revenue": simulated_revenue,
        "Scenario_Rent": simulated_rent,
        "Scenario_Cost": simulated_total_cost,
        "Scenario_Profit": simulated_profit,
        "Scenario_ROI": simulated_roi
    })

    probability_positive_profit = (simulation_df["Scenario_Profit"] > 0).mean() * 100
    probability_roi_above_15 = (simulation_df["Scenario_ROI"] >= 0.15).mean() * 100
    expected_profit = simulation_df["Scenario_Profit"].mean()
    expected_roi = simulation_df["Scenario_ROI"].mean()

    worst_case_profit = simulation_df["Scenario_Profit"].quantile(0.05)
    best_case_profit = simulation_df["Scenario_Profit"].quantile(0.95)
    downside_roi = simulation_df["Scenario_ROI"].quantile(0.05)
    upside_roi = simulation_df["Scenario_ROI"].quantile(0.95)

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Expected Profit", f"${expected_profit:,.0f}")
    m2.metric("Expected ROI", f"{expected_roi:.1%}")
    m3.metric("Probability of Profit", f"{probability_positive_profit:.1f}%")
    m4.metric("Probability ROI ≥ 15%", f"{probability_roi_above_15:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    m5, m6, m7, m8 = st.columns(4)

    m5.metric("Worst Case Profit", f"${worst_case_profit:,.0f}")
    m6.metric("Best Case Profit", f"${best_case_profit:,.0f}")
    m7.metric("Downside ROI", f"{downside_roi:.1%}")
    m8.metric("Upside ROI", f"{upside_roi:.1%}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Profit Distribution")

        fig_profit_sim = px.histogram(
            simulation_df,
            x="Scenario_Profit",
            nbins=45,
            title="Monte Carlo Profit Outcomes",
            color_discrete_sequence=[GOLD]
        )

        fig_profit_sim.add_vline(
            x=0,
            line_dash="dash",
            line_color="#B22222",
            annotation_text="Break-even",
            annotation_position="top left"
        )

        fig_profit_sim.add_vline(
            x=expected_profit,
            line_dash="dash",
            line_color="#7D6838",
            annotation_text="Expected Profit",
            annotation_position="top right"
        )

        st.plotly_chart(
            chart_layout(fig_profit_sim, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### ROI Distribution")

        fig_roi_sim = px.histogram(
            simulation_df,
            x="Scenario_ROI",
            nbins=45,
            title="Monte Carlo ROI Outcomes",
            color_discrete_sequence=[GOLD_LIGHT]
        )

        fig_roi_sim.add_vline(
            x=0.15,
            line_dash="dash",
            line_color="#7D6838",
            annotation_text="15% ROI Target",
            annotation_position="top right"
        )

        st.plotly_chart(
            chart_layout(fig_roi_sim, 540),
            use_container_width=True
        )

    st.markdown("### Best / Base / Worst Case Scenario Table")

    base_case_profit = expected_revenue - expected_cost
    base_case_roi = base_case_profit / expected_cost if expected_cost > 0 else 0

    scenario_summary_df = pd.DataFrame({
        "Scenario": [
            "Worst Case",
            "Base Case",
            "Best Case"
        ],
        "Revenue": [
            simulation_df["Scenario_Revenue"].quantile(0.05),
            expected_revenue,
            simulation_df["Scenario_Revenue"].quantile(0.95)
        ],
        "Cost": [
            simulation_df["Scenario_Cost"].quantile(0.95),
            expected_cost,
            simulation_df["Scenario_Cost"].quantile(0.05)
        ],
        "Profit": [
            worst_case_profit,
            base_case_profit,
            best_case_profit
        ],
        "ROI": [
            downside_roi,
            base_case_roi,
            upside_roi
        ],
        "Executive_Interpretation": [
            "Downside case under high cost pressure and lower revenue realization.",
            "Expected case using the selected simulation assumptions.",
            "Upside case under stronger revenue realization and lower cost pressure."
        ]
    })

    st.dataframe(
        scenario_summary_df.style.format({
            "Revenue": "${:,.0f}",
            "Cost": "${:,.0f}",
            "Profit": "${:,.0f}",
            "ROI": "{:.1%}"
        }),
        use_container_width=True,
        height=240
    )

    st.markdown("### Simulation Detail Table")

    simulation_sample = simulation_df.sample(
        min(500, len(simulation_df)),
        random_state=42
    ).copy()

    st.dataframe(
        simulation_sample.style.format({
            "Scenario_Revenue": "${:,.0f}",
            "Scenario_Rent": "${:,.0f}",
            "Scenario_Cost": "${:,.0f}",
            "Scenario_Profit": "${:,.0f}",
            "Scenario_ROI": "{:.1%}"
        }),
        use_container_width=True,
        height=420
    )

    if probability_roi_above_15 >= 70:
        simulation_verdict = "Strong risk-adjusted expansion case"
    elif probability_roi_above_15 >= 45:
        simulation_verdict = "Moderate risk-adjusted case requiring validation"
    else:
        simulation_verdict = "High-risk scenario under current assumptions"

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Simulation Summary</div>
        <div class="insight-body">
            For <b>{selected_city}</b>, this Monte Carlo simulation tested <b>{simulation_runs:,}</b> possible outcomes.
            <br><br>
            Under the selected assumptions, expected profit is <b>${expected_profit:,.0f}</b> and expected ROI is
            <b>{expected_roi:.1%}</b>.
            <br><br>
            The probability of achieving at least <b>15% ROI</b> is <b>{probability_roi_above_15:.1f}%</b>.
            <br><br>
            <b>Executive verdict:</b> {simulation_verdict}.
            <br><br>
            This layer elevates the platform from basic sliders into executive risk analytics by adding probabilistic ROI,
            downside risk, upside potential, volatility scenarios, and Monte Carlo simulation.
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab35:

    st.markdown(
        '<div class="section-title">Real AI Recommendation Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Machine learning recommendation layer using clustering, anomaly detection, predictive scoring, weighted opportunity ranking, and recommendation confidence.</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">Why this is different from rules-based recommendations</div>
        <div class="insight-body">
            The earlier recommendation logic uses fixed thresholds such as ROI above a target.
            This layer adds machine learning signals by grouping similar markets, detecting unusual market patterns,
            estimating recommendation confidence, and creating a weighted AI score across financial, demand, competition,
            data quality, and implementation readiness variables.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import MinMaxScaler

    ai_rec_df = comparison_df.copy()

    ai_feature_cols = [
        "Population_Score",
        "Income_Score",
        "Beauty_Demand_Signal",
        "Premium_Fit_Score",
        "Financial_Viability_Score",
        "Competitive_Market_Signal",
        "Saturation_Score",
        "Forecasted_Demand_Index",
        "Inventory_Risk_Score",
        "Supply_Chain_Complexity_Score",
        "Data_Governance_Score",
        "Change_Readiness_Score",
        "Scenario_ROI",
        "Scenario_Profit"
    ]

    available_ai_features = [
        col for col in ai_feature_cols
        if col in ai_rec_df.columns
    ]

    for col in available_ai_features:
        ai_rec_df[col] = pd.to_numeric(
            ai_rec_df[col],
            errors="coerce"
        )

    ai_rec_df[available_ai_features] = ai_rec_df[available_ai_features].replace(
        [np.inf, -np.inf],
        np.nan
    )

    ai_rec_df[available_ai_features] = ai_rec_df[available_ai_features].fillna(
        ai_rec_df[available_ai_features].median(numeric_only=True)
    ).fillna(0)

    if len(ai_rec_df) < 3 or len(available_ai_features) < 4:
        st.warning("Not enough data to run the AI recommendation engine. Add more markets and operational fields to improve machine learning recommendations.")

    else:
        scaler = MinMaxScaler()
        X_ai = scaler.fit_transform(ai_rec_df[available_ai_features])

        # -----------------------------
        # CLUSTERING
        # -----------------------------
        cluster_count = min(3, len(ai_rec_df))

        kmeans = KMeans(
            n_clusters=cluster_count,
            random_state=42,
            n_init=10
        )

        ai_rec_df["AI_Cluster"] = kmeans.fit_predict(X_ai)

        cluster_profile = ai_rec_df.groupby(
            "AI_Cluster",
            as_index=False
        ).agg(
            Avg_Opportunity_Score=("Final_Opportunity_Score", "mean"),
            Avg_ROI=("Scenario_ROI", "mean"),
            Avg_Demand=("Forecasted_Demand_Index", "mean"),
            Avg_Data_Readiness=("Data_Governance_Score", "mean"),
            Markets=("City", "count")
        )

        best_cluster = cluster_profile.sort_values(
            "Avg_Opportunity_Score",
            ascending=False
        ).iloc[0]["AI_Cluster"]

        ai_rec_df["Cluster_Strategy"] = ai_rec_df["AI_Cluster"].apply(
            lambda cluster: "High-Potential Peer Group"
            if cluster == best_cluster
            else "Validation Peer Group"
        )

        # -----------------------------
        # ANOMALY DETECTION
        # -----------------------------
        contamination_rate = min(0.25, max(0.08, 1 / len(ai_rec_df)))

        anomaly_model = IsolationForest(
            contamination=contamination_rate,
            random_state=42
        )

        ai_rec_df["Anomaly_Flag_Raw"] = anomaly_model.fit_predict(X_ai)
        ai_rec_df["AI_Anomaly_Status"] = ai_rec_df["Anomaly_Flag_Raw"].apply(
            lambda value: "Unusual Pattern" if value == -1 else "Normal Pattern"
        )

        anomaly_scores = anomaly_model.decision_function(X_ai)
        anomaly_scaled = MinMaxScaler().fit_transform(
            anomaly_scores.reshape(-1, 1)
        ).flatten()

        ai_rec_df["Pattern_Normality_Score"] = (anomaly_scaled * 100).round(1)

        # -----------------------------
        # PREDICTIVE RECOMMENDATION PROBABILITY
        # -----------------------------
        ai_rec_df["AI_Target_Label"] = (
            (ai_rec_df["Final_Opportunity_Score"] >= 65)
            &
            (ai_rec_df["Scenario_ROI"] >= 0.15)
        ).astype(int)

        if ai_rec_df["AI_Target_Label"].nunique() >= 2 and len(ai_rec_df) >= 6:
            clf = RandomForestClassifier(
                n_estimators=250,
                random_state=42,
                max_depth=4,
                class_weight="balanced"
            )

            clf.fit(X_ai, ai_rec_df["AI_Target_Label"])
            ai_rec_df["Predictive_Recommendation_Probability"] = (
                clf.predict_proba(X_ai)[:, 1] * 100
            ).round(1)

        else:
            # Fallback when there are too few markets/classes for a classifier.
            ai_rec_df["Predictive_Recommendation_Probability"] = (
                ai_rec_df["Final_Opportunity_Score"] * 0.65
                + ai_rec_df["Financial_Viability_Score"] * 0.20
                + ai_rec_df["Change_Readiness_Score"] * 0.15
            ).clip(0, 100).round(1)

        # -----------------------------
        # WEIGHTED ML-STYLE AI SCORE
        # -----------------------------
        ai_rec_df["AI_Weighted_Recommendation_Score"] = (
            ai_rec_df["Final_Opportunity_Score"] * 0.25
            + ai_rec_df["Predictive_Recommendation_Probability"] * 0.25
            + ai_rec_df["Forecasted_Demand_Index"] * 0.15
            + ai_rec_df["Financial_Viability_Score"] * 0.15
            + ai_rec_df["Change_Readiness_Score"] * 0.10
            + ai_rec_df["Data_Governance_Score"] * 0.05
            + ai_rec_df["Pattern_Normality_Score"] * 0.05
            - ai_rec_df["Saturation_Score"] * 0.05
            - ai_rec_df["Inventory_Risk_Score"] * 0.03
        ).clip(0, 100).round(1)

        ai_rec_df["Recommendation_Confidence_%"] = (
            ai_rec_df["Predictive_Recommendation_Probability"] * 0.45
            + ai_rec_df["Pattern_Normality_Score"] * 0.25
            + ai_rec_df["Data_Governance_Score"] * 0.20
            + ai_rec_df["Change_Readiness_Score"] * 0.10
        ).clip(0, 100).round(1)

        def ai_recommendation_label(row):
            if row["AI_Anomaly_Status"] == "Unusual Pattern" and row["AI_Weighted_Recommendation_Score"] < 70:
                return "Investigate Before Decision"
            elif row["AI_Weighted_Recommendation_Score"] >= 80 and row["Recommendation_Confidence_%"] >= 70:
                return "AI Priority Recommendation"
            elif row["AI_Weighted_Recommendation_Score"] >= 65:
                return "AI Recommended for Validation"
            elif row["AI_Weighted_Recommendation_Score"] >= 50:
                return "Monitor with Additional Data"
            else:
                return "Not Recommended Under Current Signals"

        ai_rec_df["AI_Recommendation"] = ai_rec_df.apply(
            ai_recommendation_label,
            axis=1
        )

        ai_rec_df = ai_rec_df.sort_values(
            "AI_Weighted_Recommendation_Score",
            ascending=False
        )

        top_ai_market = ai_rec_df.iloc[0]
        avg_ai_score = ai_rec_df["AI_Weighted_Recommendation_Score"].mean()
        avg_confidence = ai_rec_df["Recommendation_Confidence_%"].mean()
        anomaly_count = len(ai_rec_df[ai_rec_df["AI_Anomaly_Status"] == "Unusual Pattern"])
        priority_count = len(ai_rec_df[ai_rec_df["AI_Recommendation"] == "AI Priority Recommendation"])

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Top AI Market", top_ai_market["City"])
        m2.metric("Avg AI Score", f"{avg_ai_score:.1f}/100")
        m3.metric("Avg Confidence", f"{avg_confidence:.1f}%")
        m4.metric("Anomalies Detected", f"{anomaly_count:,}")

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### AI Recommendation Score by Market")

            fig_ai_rec = px.bar(
                ai_rec_df,
                x="City",
                y="AI_Weighted_Recommendation_Score",
                color="AI_Recommendation",
                text="AI_Weighted_Recommendation_Score",
                color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838", "#8A8A8A"]
            )

            fig_ai_rec.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )

            st.plotly_chart(
                chart_layout(fig_ai_rec, 540),
                use_container_width=True
            )

        with c2:
            st.markdown("### ML Cluster Map")

            fig_cluster = px.scatter(
                ai_rec_df,
                x="Financial_Viability_Score",
                y="Forecasted_Demand_Index",
                size="AI_Weighted_Recommendation_Score",
                color="Cluster_Strategy",
                hover_name="City",
                hover_data={
                    "AI_Cluster": True,
                    "Recommendation_Confidence_%": ":.1f",
                    "AI_Anomaly_Status": True,
                    "Scenario_ROI": ":.1%"
                },
                color_discrete_sequence=[GOLD, GOLD_LIGHT, "#7D6838"]
            )

            fig_cluster.update_layout(
                xaxis_title="Financial Viability Score",
                yaxis_title="Forecasted Demand Index"
            )

            st.plotly_chart(
                chart_layout(fig_cluster, 540),
                use_container_width=True
            )

        st.markdown("### Predictive Recommendation Confidence")

        fig_confidence = px.bar(
            ai_rec_df.sort_values("Recommendation_Confidence_%", ascending=False),
            x="City",
            y="Recommendation_Confidence_%",
            color="AI_Anomaly_Status",
            text="Recommendation_Confidence_%",
            color_discrete_map={
                "Normal Pattern": GOLD,
                "Unusual Pattern": "#B22222"
            }
        )

        fig_confidence.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_confidence, 500),
            use_container_width=True
        )

        st.markdown("### AI Recommendation Detail Table")

        ai_detail_cols = [
            "City",
            "AI_Recommendation",
            "AI_Weighted_Recommendation_Score",
            "Recommendation_Confidence_%",
            "Predictive_Recommendation_Probability",
            "AI_Anomaly_Status",
            "Cluster_Strategy",
            "Final_Opportunity_Score",
            "Scenario_ROI",
            "Forecasted_Demand_Index",
            "Financial_Viability_Score",
            "Change_Readiness_Score",
            "Data_Governance_Score",
            "Inventory_Risk_Score",
            "Saturation_Score"
        ]

        available_ai_detail_cols = [
            col for col in ai_detail_cols
            if col in ai_rec_df.columns
        ]

        st.dataframe(
            ai_rec_df[available_ai_detail_cols].style.format({
                "AI_Weighted_Recommendation_Score": "{:.1f}",
                "Recommendation_Confidence_%": "{:.1f}%",
                "Predictive_Recommendation_Probability": "{:.1f}%",
                "Final_Opportunity_Score": "{:.1f}",
                "Scenario_ROI": "{:.1%}",
                "Forecasted_Demand_Index": "{:.1f}",
                "Financial_Viability_Score": "{:.1f}",
                "Change_Readiness_Score": "{:.1f}",
                "Data_Governance_Score": "{:.1f}",
                "Inventory_Risk_Score": "{:.1f}",
                "Saturation_Score": "{:.1f}"
            }),
            use_container_width=True,
            height=480
        )

        st.markdown("### AI Cluster Profiles")

        st.dataframe(
            cluster_profile.style.format({
                "Avg_Opportunity_Score": "{:.1f}",
                "Avg_ROI": "{:.1%}",
                "Avg_Demand": "{:.1f}",
                "Avg_Data_Readiness": "{:.1f}"
            }),
            use_container_width=True,
            height=240
        )

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Executive AI Recommendation Summary</div>
            <div class="insight-body">
                The strongest AI-generated recommendation is <b>{top_ai_market["City"]}</b>, with an AI weighted score of
                <b>{top_ai_market["AI_Weighted_Recommendation_Score"]:.1f}/100</b> and recommendation confidence of
                <b>{top_ai_market["Recommendation_Confidence_%"]:.1f}%</b>.
                <br><br>
                The engine identified <b>{priority_count}</b> priority recommendation(s) and <b>{anomaly_count}</b> unusual market pattern(s).
                <br><br>
                This layer strengthens the platform by moving beyond fixed if/then rules into clustering,
                anomaly detection, predictive recommendation probability, weighted ML scoring, and confidence-based executive recommendations.
            </div>
        </div>
        """, unsafe_allow_html=True)



with tab36:

    st.markdown(
        '<div class="section-title">Workforce & Labor Optimization Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Operational labor intelligence for stylist utilization, labor forecasting, scheduling optimization, payroll efficiency, and service mix profitability.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # WORKFORCE DATA FOUNDATION
    # -----------------------------
    workforce_df = sales_df.copy()

    if "Salon_Location" not in workforce_df.columns:
        workforce_df["Salon_Location"] = "Main Salon"

    if "Date" in workforce_df.columns:
        workforce_df["Date"] = pd.to_datetime(workforce_df["Date"], errors="coerce")
    else:
        workforce_df["Date"] = pd.Timestamp.today()

    workforce_df = workforce_df.dropna(subset=["Date"]).copy()

    if "Revenue" not in workforce_df.columns:
        workforce_df["Revenue"] = workforce_df.get("Units_Sold", 0) * workforce_df.get("Retail_Price", 0)

    if "Gross_Profit_Calculated" not in workforce_df.columns:
        workforce_df["Gross_Profit_Calculated"] = workforce_df["Revenue"] - (
            workforce_df.get("Units_Sold", 0) * workforce_df.get("Unit_Cost", 0)
        )

    # If the source file does not have service/stylist-level fields yet, create realistic operational assumptions
    if "Stylist" not in workforce_df.columns:
        stylist_pool = [
            "Senior Stylist A", "Senior Stylist B", "Color Specialist A", "Color Specialist B",
            "Stylist C", "Stylist D", "Stylist E", "Assistant Stylist"
        ]
        workforce_df["Stylist"] = [stylist_pool[i % len(stylist_pool)] for i in range(len(workforce_df))]

    if "Service_Category" not in workforce_df.columns:
        def infer_service_category(row):
            product_text = str(row.get("Product_Name", "")).lower()
            brand_text = str(row.get("Brand", "")).lower()
            if any(word in product_text for word in ["color", "gloss", "toner", "bleach", "developer"]):
                return "Color Services"
            if any(word in product_text for word in ["treatment", "mask", "repair", "keratin"]):
                return "Treatment Services"
            if any(word in product_text for word in ["extension", "weft", "tape"]):
                return "Extensions"
            if any(word in brand_text for word in ["retail", "product"]):
                return "Retail Support"
            return "Styling / Blowout"

        workforce_df["Service_Category"] = workforce_df.apply(infer_service_category, axis=1)

    service_hours_map = {
        "Styling / Blowout": 1.0,
        "Color Services": 2.5,
        "Treatment Services": 1.5,
        "Extensions": 3.0,
        "Retail Support": 0.4
    }

    if "Service_Hours" not in workforce_df.columns:
        workforce_df["Service_Hours"] = workforce_df["Service_Category"].map(service_hours_map).fillna(1.0)

    if "Payroll_Cost" not in workforce_df.columns:
        stylist_rate_map = {
            "Senior Stylist A": 42,
            "Senior Stylist B": 40,
            "Color Specialist A": 45,
            "Color Specialist B": 43,
            "Stylist C": 32,
            "Stylist D": 31,
            "Stylist E": 30,
            "Assistant Stylist": 22
        }
        workforce_df["Hourly_Rate"] = workforce_df["Stylist"].map(stylist_rate_map).fillna(32)
        workforce_df["Payroll_Cost"] = workforce_df["Service_Hours"] * workforce_df["Hourly_Rate"]
    else:
        workforce_df["Payroll_Cost"] = pd.to_numeric(workforce_df["Payroll_Cost"], errors="coerce").fillna(0)
        if "Hourly_Rate" not in workforce_df.columns:
            workforce_df["Hourly_Rate"] = workforce_df.apply(
                lambda row: row["Payroll_Cost"] / row["Service_Hours"] if row["Service_Hours"] > 0 else 0,
                axis=1
            )

    if "Available_Hours" not in workforce_df.columns:
        workforce_df["Available_Hours"] = 8

    numeric_workforce_cols = [
        "Revenue", "Gross_Profit_Calculated", "Service_Hours", "Payroll_Cost", "Available_Hours", "Units_Sold"
    ]

    for col in numeric_workforce_cols:
        if col in workforce_df.columns:
            workforce_df[col] = pd.to_numeric(workforce_df[col], errors="coerce").fillna(0)

    workforce_df["Month"] = workforce_df["Date"].dt.to_period("M").dt.to_timestamp()
    workforce_df["Weekday"] = workforce_df["Date"].dt.day_name()

    # -----------------------------
    # STYLIST UTILIZATION
    # -----------------------------
    stylist_summary = workforce_df.groupby(
        ["Salon_Location", "Stylist"],
        as_index=False
    ).agg(
        Appointments_or_Transactions=("Date", "count"),
        Service_Hours=("Service_Hours", "sum"),
        Available_Hours=("Available_Hours", "sum"),
        Revenue=("Revenue", "sum"),
        Gross_Profit=("Gross_Profit_Calculated", "sum"),
        Payroll_Cost=("Payroll_Cost", "sum")
    )

    stylist_summary["Utilization_%"] = stylist_summary.apply(
        lambda row: (row["Service_Hours"] / row["Available_Hours"] * 100) if row["Available_Hours"] > 0 else 0,
        axis=1
    ).clip(0, 140).round(1)

    stylist_summary["Revenue_Per_Service_Hour"] = stylist_summary.apply(
        lambda row: row["Revenue"] / row["Service_Hours"] if row["Service_Hours"] > 0 else 0,
        axis=1
    ).round(2)

    stylist_summary["Profit_Per_Service_Hour"] = stylist_summary.apply(
        lambda row: row["Gross_Profit"] / row["Service_Hours"] if row["Service_Hours"] > 0 else 0,
        axis=1
    ).round(2)

    stylist_summary["Payroll_Efficiency_Ratio"] = stylist_summary.apply(
        lambda row: row["Revenue"] / row["Payroll_Cost"] if row["Payroll_Cost"] > 0 else 0,
        axis=1
    ).round(2)

    stylist_summary["Utilization_Status"] = stylist_summary["Utilization_%"].apply(
        lambda x: "Over Capacity" if x >= 95 else "Optimized" if x >= 70 else "Underutilized"
    )

    # -----------------------------
    # LABOR FORECASTING
    # -----------------------------
    monthly_labor = workforce_df.groupby(
        ["Month", "Salon_Location"],
        as_index=False
    ).agg(
        Revenue=("Revenue", "sum"),
        Service_Hours=("Service_Hours", "sum"),
        Payroll_Cost=("Payroll_Cost", "sum"),
        Transactions=("Date", "count")
    )

    labor_forecast_base = monthly_labor.sort_values("Month").groupby("Salon_Location").tail(3)

    labor_forecast_df = labor_forecast_base.groupby(
        "Salon_Location",
        as_index=False
    ).agg(
        Forecast_Next_Month_Service_Hours=("Service_Hours", "mean"),
        Forecast_Next_Month_Revenue=("Revenue", "mean"),
        Forecast_Next_Month_Payroll=("Payroll_Cost", "mean"),
        Forecast_Next_Month_Transactions=("Transactions", "mean")
    )

    labor_forecast_df["Recommended_FTE"] = (labor_forecast_df["Forecast_Next_Month_Service_Hours"] / 160).round(1)
    labor_forecast_df["Revenue_Per_Forecasted_Labor_Hour"] = labor_forecast_df.apply(
        lambda row: row["Forecast_Next_Month_Revenue"] / row["Forecast_Next_Month_Service_Hours"]
        if row["Forecast_Next_Month_Service_Hours"] > 0 else 0,
        axis=1
    ).round(2)

    # -----------------------------
    # SCHEDULING OPTIMIZATION
    # -----------------------------
    weekday_schedule = workforce_df.groupby(
        ["Salon_Location", "Weekday"],
        as_index=False
    ).agg(
        Demand_Hours=("Service_Hours", "sum"),
        Revenue=("Revenue", "sum"),
        Transactions=("Date", "count")
    )

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_schedule["Weekday"] = pd.Categorical(weekday_schedule["Weekday"], categories=weekday_order, ordered=True)
    weekday_schedule = weekday_schedule.sort_values(["Salon_Location", "Weekday"])

    avg_daily_hours = weekday_schedule.groupby("Salon_Location")["Demand_Hours"].transform("mean")
    weekday_schedule["Staffing_Recommendation"] = np.where(
        weekday_schedule["Demand_Hours"] >= avg_daily_hours * 1.20,
        "Add Coverage",
        np.where(
            weekday_schedule["Demand_Hours"] <= avg_daily_hours * 0.80,
            "Reduce / Reallocate Hours",
            "Maintain Coverage"
        )
    )

    # -----------------------------
    # SERVICE MIX PROFITABILITY
    # -----------------------------
    service_mix_df = workforce_df.groupby(
        ["Service_Category"],
        as_index=False
    ).agg(
        Revenue=("Revenue", "sum"),
        Gross_Profit=("Gross_Profit_Calculated", "sum"),
        Service_Hours=("Service_Hours", "sum"),
        Payroll_Cost=("Payroll_Cost", "sum"),
        Transactions=("Date", "count")
    )

    service_mix_df["Gross_Margin_%"] = service_mix_df.apply(
        lambda row: row["Gross_Profit"] / row["Revenue"] * 100 if row["Revenue"] > 0 else 0,
        axis=1
    ).round(1)

    service_mix_df["Profit_Per_Service_Hour"] = service_mix_df.apply(
        lambda row: row["Gross_Profit"] / row["Service_Hours"] if row["Service_Hours"] > 0 else 0,
        axis=1
    ).round(2)

    service_mix_df["Payroll_Load_%"] = service_mix_df.apply(
        lambda row: row["Payroll_Cost"] / row["Revenue"] * 100 if row["Revenue"] > 0 else 0,
        axis=1
    ).round(1)

    # -----------------------------
    # LOCATION LABOR BENCHMARKING
    # -----------------------------
    location_labor_df = workforce_df.groupby(
        "Salon_Location",
        as_index=False
    ).agg(
        Revenue=("Revenue", "sum"),
        Gross_Profit=("Gross_Profit_Calculated", "sum"),
        Service_Hours=("Service_Hours", "sum"),
        Payroll_Cost=("Payroll_Cost", "sum"),
        Transactions=("Date", "count"),
        Stylists=("Stylist", "nunique")
    )

    location_labor_df["Revenue_Per_Stylist"] = location_labor_df.apply(
        lambda row: row["Revenue"] / row["Stylists"] if row["Stylists"] > 0 else 0,
        axis=1
    ).round(2)

    location_labor_df["Revenue_Per_Labor_Hour"] = location_labor_df.apply(
        lambda row: row["Revenue"] / row["Service_Hours"] if row["Service_Hours"] > 0 else 0,
        axis=1
    ).round(2)

    location_labor_df["Payroll_%_of_Revenue"] = location_labor_df.apply(
        lambda row: row["Payroll_Cost"] / row["Revenue"] * 100 if row["Revenue"] > 0 else 0,
        axis=1
    ).round(1)

    location_labor_df["Labor_Productivity_Score"] = (
        location_labor_df["Revenue_Per_Labor_Hour"].rank(pct=True) * 45
        + (100 - location_labor_df["Payroll_%_of_Revenue"].rank(pct=True) * 100) * 0.30
        + location_labor_df["Revenue_Per_Stylist"].rank(pct=True) * 25
    ).clip(0, 100).round(1)

    location_labor_df["Labor_Action"] = location_labor_df["Labor_Productivity_Score"].apply(
        lambda score: "Scale Best Practices" if score >= 75 else "Optimize Scheduling" if score >= 50 else "Review Staffing Model"
    )

    # -----------------------------
    # KPI ROW
    # -----------------------------
    avg_utilization = stylist_summary["Utilization_%"].mean() if not stylist_summary.empty else 0
    total_labor_cost = workforce_df["Payroll_Cost"].sum()
    payroll_pct_revenue = (total_labor_cost / workforce_df["Revenue"].sum() * 100) if workforce_df["Revenue"].sum() > 0 else 0
    avg_revenue_per_labor_hour = (workforce_df["Revenue"].sum() / workforce_df["Service_Hours"].sum()) if workforce_df["Service_Hours"].sum() > 0 else 0
    underutilized_count = len(stylist_summary[stylist_summary["Utilization_Status"] == "Underutilized"])

    w1, w2, w3, w4, w5 = st.columns(5)

    w1.metric("Avg Stylist Utilization", f"{avg_utilization:.1f}%")
    w2.metric("Payroll % of Revenue", f"{payroll_pct_revenue:.1f}%")
    w3.metric("Revenue / Labor Hour", f"${avg_revenue_per_labor_hour:,.0f}")
    w4.metric("Underutilized Stylists", f"{underutilized_count:,}")
    w5.metric("Forecasted FTE Needed", f"{labor_forecast_df['Recommended_FTE'].sum():.1f}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Stylist Utilization")

        fig_utilization = px.bar(
            stylist_summary.sort_values("Utilization_%", ascending=False),
            x="Stylist",
            y="Utilization_%",
            color="Utilization_Status",
            text="Utilization_%",
            color_discrete_map={
                "Over Capacity": "#B22222",
                "Optimized": GOLD,
                "Underutilized": "#8A8A8A"
            }
        )

        fig_utilization.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_utilization, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### Service Mix Profitability")

        fig_service_profit = px.bar(
            service_mix_df.sort_values("Profit_Per_Service_Hour", ascending=False),
            x="Service_Category",
            y="Profit_Per_Service_Hour",
            color="Payroll_Load_%",
            text="Profit_Per_Service_Hour",
            color_continuous_scale=["#EFE2BD", GOLD, "#7D6838"]
        )

        fig_service_profit.update_traces(
            texttemplate="$%{text:.0f}",
            textposition="outside"
        )

        st.plotly_chart(
            chart_layout(fig_service_profit, 540),
            use_container_width=True
        )

    st.markdown("### Labor Forecasting by Location")

    fig_labor_forecast = px.bar(
        labor_forecast_df.sort_values("Forecast_Next_Month_Service_Hours", ascending=False),
        x="Salon_Location",
        y="Forecast_Next_Month_Service_Hours",
        color="Recommended_FTE",
        text="Recommended_FTE",
        color_continuous_scale=["#EFE2BD", GOLD, "#7D6838"]
    )

    fig_labor_forecast.update_traces(
        texttemplate="%{text:.1f} FTE",
        textposition="outside"
    )

    st.plotly_chart(
        chart_layout(fig_labor_forecast, 520),
        use_container_width=True
    )

    st.markdown("### Scheduling Optimization by Day")

    fig_schedule = px.bar(
        weekday_schedule,
        x="Weekday",
        y="Demand_Hours",
        color="Staffing_Recommendation",
        facet_col="Salon_Location" if weekday_schedule["Salon_Location"].nunique() <= 4 else None,
        text="Demand_Hours",
        color_discrete_map={
            "Add Coverage": "#B22222",
            "Maintain Coverage": GOLD,
            "Reduce / Reallocate Hours": "#8A8A8A"
        }
    )

    fig_schedule.update_traces(
        texttemplate="%{text:.0f}h",
        textposition="outside"
    )

    st.plotly_chart(
        chart_layout(fig_schedule, 560),
        use_container_width=True
    )

    st.markdown("### Location Labor Benchmarking")

    fig_location_labor = px.scatter(
        location_labor_df,
        x="Payroll_%_of_Revenue",
        y="Revenue_Per_Labor_Hour",
        size="Revenue",
        color="Labor_Action",
        hover_name="Salon_Location",
        hover_data={
            "Stylists": True,
            "Revenue_Per_Stylist": ":$,.0f",
            "Labor_Productivity_Score": ":.1f"
        },
        color_discrete_sequence=[GOLD, GOLD_LIGHT, "#7D6838"]
    )

    fig_location_labor.update_layout(
        xaxis_title="Payroll % of Revenue",
        yaxis_title="Revenue per Labor Hour"
    )

    st.plotly_chart(
        chart_layout(fig_location_labor, 540),
        use_container_width=True
    )

    st.markdown("### Stylist Performance Detail")

    st.dataframe(
        stylist_summary.sort_values("Revenue_Per_Service_Hour", ascending=False).style.format({
            "Service_Hours": "{:,.1f}",
            "Available_Hours": "{:,.1f}",
            "Revenue": "${:,.0f}",
            "Gross_Profit": "${:,.0f}",
            "Payroll_Cost": "${:,.0f}",
            "Utilization_%": "{:.1f}%",
            "Revenue_Per_Service_Hour": "${:,.0f}",
            "Profit_Per_Service_Hour": "${:,.0f}",
            "Payroll_Efficiency_Ratio": "{:.2f}x"
        }),
        use_container_width=True,
        height=420
    )

    st.markdown("### Labor Forecast Detail")

    st.dataframe(
        labor_forecast_df.style.format({
            "Forecast_Next_Month_Service_Hours": "{:,.1f}",
            "Forecast_Next_Month_Revenue": "${:,.0f}",
            "Forecast_Next_Month_Payroll": "${:,.0f}",
            "Forecast_Next_Month_Transactions": "{:,.0f}",
            "Recommended_FTE": "{:.1f}",
            "Revenue_Per_Forecasted_Labor_Hour": "${:,.0f}"
        }),
        use_container_width=True,
        height=280
    )

    st.markdown("### Service Mix Profitability Detail")

    st.dataframe(
        service_mix_df.sort_values("Profit_Per_Service_Hour", ascending=False).style.format({
            "Revenue": "${:,.0f}",
            "Gross_Profit": "${:,.0f}",
            "Service_Hours": "{:,.1f}",
            "Payroll_Cost": "${:,.0f}",
            "Gross_Margin_%": "{:.1f}%",
            "Profit_Per_Service_Hour": "${:,.0f}",
            "Payroll_Load_%": "{:.1f}%"
        }),
        use_container_width=True,
        height=320
    )

    top_stylist = stylist_summary.sort_values("Revenue_Per_Service_Hour", ascending=False).iloc[0]
    top_service = service_mix_df.sort_values("Profit_Per_Service_Hour", ascending=False).iloc[0]
    highest_demand_day = weekday_schedule.sort_values("Demand_Hours", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Workforce Optimization Summary</div>
        <div class="insight-body">
            The strongest labor productivity signal comes from <b>{top_stylist["Stylist"]}</b>, generating
            <b>${top_stylist["Revenue_Per_Service_Hour"]:,.0f}</b> per service hour.
            <br><br>
            The most profitable service category by labor hour is <b>{top_service["Service_Category"]}</b>, producing
            <b>${top_service["Profit_Per_Service_Hour"]:,.0f}</b> gross profit per service hour.
            <br><br>
            The highest scheduling demand appears on <b>{highest_demand_day["Weekday"]}</b> in
            <b>{highest_demand_day["Salon_Location"]}</b>, with <b>{highest_demand_day["Demand_Hours"]:,.0f}</b> service hours.
            <br><br>
            This layer strengthens the platform with salon-specific labor optimization, stylist utilization,
            labor forecasting, payroll efficiency, scheduling recommendations, and service mix profitability.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab37:

    st.markdown('<div class="section-title">Executive Architecture Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Enterprise-level documentation of the platform architecture, data flows, API layers, governance workflow, and operational decision process. This tab is designed to support executive communication, implementation planning, and NIW evidence.</div>', unsafe_allow_html=True)

    arch_kpi_1, arch_kpi_2, arch_kpi_3, arch_kpi_4 = st.columns(4)
    arch_kpi_1.metric("Architecture Layers", "6")
    arch_kpi_2.metric("Data Domains", "9")
    arch_kpi_3.metric("Decision Engines", "10+")
    arch_kpi_4.metric("Governance Controls", "8")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Enterprise System Architecture")

    st.graphviz_chart("""
    digraph G {
        graph [rankdir=LR, bgcolor="transparent"];
        node [shape=box, style="rounded,filled", color="#C6A052", fillcolor="#FFF8E6", fontname="Inter", fontsize=10];
        edge [color="#8A6A24", arrowsize=0.8];
        DataSources [label="Data Sources\nGoogle Sheets | Excel | APIs | Manual Inputs"];
        Ingestion [label="Data Ingestion Layer\nCSV Load | Excel Load | API Requests"];
        Validation [label="Data Validation & Governance\nMissing Values | Duplicates | Trust Scoring"];
        Analytics [label="Analytics Engines\nForecasting | Supply Chain | CRM | Workforce"];
        Decision [label="Decision Intelligence Layer\nScoring | Recommendations | Simulations"];
        ExecutiveUI [label="Executive Streamlit Interface\nDashboards | Reports | Downloadable Evidence"];
        DataSources -> Ingestion;
        Ingestion -> Validation;
        Validation -> Analytics;
        Analytics -> Decision;
        Decision -> ExecutiveUI;
    }
    """)

    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">Architecture Interpretation</div>
        <div class="insight-body">
            The platform follows a layered enterprise architecture: data sources feed an ingestion layer, data is validated through governance controls,
            analytics engines transform operational data into intelligence, and decision engines convert those insights into executive recommendations.
            <br><br>
            This supports expansion planning, product intelligence, supply chain optimization, franchise operations, CRM analytics, workforce planning,
            change management, data governance maturity, and risk simulation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Data Flow & Pipeline Documentation")

    pipeline_df = pd.DataFrame({
        "Pipeline Stage": [
            "1. Source Data Capture", "2. Data Ingestion", "3. Data Cleaning", "4. Feature Engineering",
            "5. Analytics Modeling", "6. Decision Scoring", "7. Executive Visualization", "8. Governance Review"
        ],
        "Purpose": [
            "Collect market, sales, inventory, academy, franchise, CRM, labor, and competitor data.",
            "Load structured data from Google Sheets, Excel workbooks, APIs, and manual assumptions.",
            "Standardize columns, convert dates, clean numeric fields, and handle missing values.",
            "Create ROI metrics, utilization ratios, maturity scores, churn signals, forecast features, and risk scores.",
            "Run forecasting, optimization, segmentation, benchmarking, governance, and simulation logic.",
            "Translate outputs into opportunity scores, recommendations, risk levels, and operational priorities.",
            "Present dashboards, charts, tables, executive summaries, and downloadable reports.",
            "Review completeness, source trust, auditability, ownership, and implementation readiness."
        ],
        "Business Value": [
            "Creates one analytical foundation across multiple business domains.",
            "Reduces manual reporting effort and improves refreshability.",
            "Improves decision reliability and reduces data quality risk.",
            "Turns raw data into management decision variables.",
            "Enables predictive and prescriptive decision support.",
            "Supports leadership prioritization and resource allocation.",
            "Makes complex analytics understandable for executives.",
            "Supports scalable, auditable, and repeatable transformation governance."
        ]
    })
    st.dataframe(pipeline_df, use_container_width=True, height=360)

    st.markdown("### API & Integration Architecture")
    api_architecture_df = pd.DataFrame({
        "Integration Layer": ["Google Sheets API", "Google Places API", "Census API", "Excel Operational Workbooks", "Streamlit Runtime", "Report Generation Layer"],
        "Current / Planned Role": [
            "Stores and synchronizes competitor intelligence cache.",
            "Retrieves live competitor location, rating, and review data.",
            "Retrieves demographic indicators such as population and median income.",
            "Stores product, inventory, academy, franchise, CRM, labor, and operational data.",
            "Runs analytics, scenario logic, dashboard rendering, and user interaction.",
            "Generates executive PDF outputs and evidence-oriented summaries."
        ],
        "Governance Consideration": [
            "Requires access control and refresh ownership.", "Requires API key security and query monitoring.",
            "Requires source trust and vintage tracking.", "Requires version control and data owner assignment.",
            "Requires deployment security and environment configuration.", "Requires consistent assumptions and audit trail."
        ]
    })
    st.dataframe(api_architecture_df, use_container_width=True, height=300)

    st.graphviz_chart("""
    digraph G {
        graph [rankdir=TB, bgcolor="transparent"];
        node [shape=box, style="rounded,filled", color="#C6A052", fillcolor="#FFF8E6", fontname="Inter", fontsize=10];
        edge [color="#8A6A24", arrowsize=0.8];
        User [label="Executive User"];
        Streamlit [label="Streamlit Application"];
        Sheets [label="Google Sheets API"];
        Places [label="Google Places API"];
        Census [label="Census API"];
        Excel [label="Excel Data Model"];
        Models [label="Analytics & Optimization Engines"];
        Reports [label="PDF / Executive Outputs"];
        User -> Streamlit;
        Streamlit -> Sheets;
        Streamlit -> Places;
        Streamlit -> Census;
        Streamlit -> Excel;
        Sheets -> Models;
        Places -> Models;
        Census -> Models;
        Excel -> Models;
        Models -> Streamlit;
        Streamlit -> Reports;
    }
    """)

    st.markdown("### Governance Flow")
    governance_flow_df = pd.DataFrame({
        "Governance Control": ["Data Ownership", "Data Stewardship", "Master Data Consistency", "Duplicate Detection", "Source Trust Scoring", "Lineage Documentation", "Auditability", "Executive Review"],
        "How It Works in the Platform": [
            "Assigns accountability to each data domain such as market, inventory, CRM, workforce, and franchise operations.",
            "Defines who maintains data quality and approves operational updates.",
            "Standardizes location, product, stylist, customer, and franchise identifiers.",
            "Flags duplicate customers, products, locations, or transaction records.",
            "Scores data sources based on reliability, recency, and completeness.",
            "Documents where each insight originates and how it is transformed.",
            "Creates repeatable calculations and transparent assumptions.",
            "Summarizes findings into leadership-ready recommendations and risk flags."
        ],
        "Executive Benefit": ["Clear accountability.", "Improved data quality.", "Consistent reporting.", "Reduced reporting distortion.", "Higher confidence in analytics.", "Traceable decisions.", "Defensible outputs.", "Faster decision-making."]
    })
    st.dataframe(governance_flow_df, use_container_width=True, height=360)

    st.markdown("### Operational Workflow")
    st.graphviz_chart("""
    digraph G {
        graph [rankdir=LR, bgcolor="transparent"];
        node [shape=box, style="rounded,filled", color="#C6A052", fillcolor="#FFF8E6", fontname="Inter", fontsize=10];
        edge [color="#8A6A24", arrowsize=0.8];
        Input [label="Update Inputs\nMarket | Sales | Labor | CRM | Franchise"];
        Validate [label="Validate Data\nCompleteness | Duplicates | Trust"];
        Analyze [label="Run Analytics\nForecast | Optimize | Benchmark"];
        Interpret [label="Interpret Outputs\nRisk | ROI | Readiness | Confidence"];
        Act [label="Executive Action\nExpand | Reorder | Staff | Retain | Train"];
        Monitor [label="Monitor Results\nKPIs | Accuracy | Adoption"];
        Input -> Validate -> Analyze -> Interpret -> Act -> Monitor -> Input;
    }
    """)

    workflow_df = pd.DataFrame({
        "Workflow Step": ["Update Inputs", "Validate Data", "Run Analytics", "Interpret Outputs", "Take Executive Action", "Monitor Results"],
        "Operational Example": [
            "Refresh sales, inventory, customer, workforce, franchise, and market data.",
            "Check missing values, duplicates, source trust, and governance maturity.",
            "Run forecasts, reorder logic, workforce utilization, churn risk, and franchise benchmarking.",
            "Review risk levels, confidence scores, profitability, maturity, and recommendations.",
            "Adjust staffing, reorder inventory, target customers, validate expansion markets, or update training plans.",
            "Track adoption, accuracy, profitability, retention, labor efficiency, and operational performance."
        ]
    })
    st.dataframe(workflow_df, use_container_width=True, height=280)

    st.markdown("### Enterprise Module Map")
    module_map_df = pd.DataFrame({
        "Platform Module": [
            "Market Expansion Intelligence", "Competitive Intelligence", "AI Demand Forecasting", "Supply Chain Optimization",
            "Franchise Operational Intelligence", "CRM / Customer Intelligence", "Change Management Governance", "Data Governance Maturity",
            "Executive Simulation Engine", "Real AI Recommendation Engine", "Workforce / Labor Optimization"
        ],
        "Primary Decision Supported": [
            "Where to expand next.", "How saturated and attractive each market is.", "What demand may look like over future periods.",
            "What to reorder, when, and with what risk level.", "Which locations perform best and why.",
            "Which customer segments to retain, grow, or reactivate.", "How ready the organization is for transformation.",
            "Whether data is reliable, owned, auditable, and consistent.", "What outcomes are likely under uncertainty.",
            "Which actions have the highest predicted value.", "How to optimize staffing, utilization, payroll, and service profitability."
        ],
        "Architecture Role": [
            "Strategic planning layer", "External intelligence layer", "Predictive analytics layer", "Prescriptive optimization layer",
            "Operating model layer", "Customer analytics layer", "Transformation governance layer", "Data control layer",
            "Risk simulation layer", "AI decision layer", "Workforce planning layer"
        ]
    })
    st.dataframe(module_map_df, use_container_width=True, height=420)

    architecture_markdown = """
# Executive Architecture Documentation

## Platform Name
AI-Driven Supply Chain & Retail Technology Strategy Platform

## Purpose
This platform provides an integrated executive intelligence system for market expansion, supply chain optimization, franchise operations, customer intelligence, workforce planning, governance maturity, and transformation decision-making.

## Enterprise Architecture Layers
1. Data Sources: Google Sheets, Excel workbooks, APIs, operational inputs, market data, customer data, labor data, and franchise data.
2. Data Ingestion: CSV loading, Excel workbook loading, API requests, and manual scenario assumptions.
3. Data Validation & Governance: missing value detection, duplicate detection, source trust scoring, ownership, stewardship, auditability, and lineage.
4. Analytics Engines: forecasting, supply chain optimization, CRM segmentation, workforce optimization, franchise benchmarking, AI recommendations, and Monte Carlo simulation.
5. Decision Intelligence: scoring models, confidence metrics, risk classifications, recommendations, and executive summaries.
6. Executive Interface: Streamlit dashboards, KPI cards, charts, tables, reports, and downloadable documentation.

## Data Flow
Source data is ingested, cleaned, validated, transformed into analytical features, processed through decision engines, and displayed as executive recommendations.

## API Architecture
The platform currently supports or is structured for Google Sheets API, Google Places API, Census API, Excel data models, Streamlit runtime logic, and report generation workflows.

## Governance Flow
The governance model includes data ownership, stewardship, source trust scoring, lineage, auditability, duplicate detection, and executive review.

## Operational Workflow
1. Refresh data inputs.
2. Validate and govern data.
3. Run analytics engines.
4. Interpret recommendations.
5. Execute business action.
6. Monitor results and improve the model.

## NIW Evidence Value
This architecture demonstrates applied expertise in AI-driven analytics, data governance, supply chain optimization, digital transformation, franchise operations, workforce optimization, and executive decision support.
"""

    st.download_button(
        label="Download Architecture Documentation",
        data=architecture_markdown,
        file_name="executive_architecture_documentation.md",
        mime="text/markdown"
    )

    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">Executive Architecture Summary</div>
        <div class="insight-body">
            This documentation layer makes the platform look less like a standalone dashboard and more like an enterprise decision architecture.
            <br><br>
            It explains how data moves through the system, how APIs and operational files connect, how governance is applied, and how analytics outputs become executive decisions.
            <br><br>
            For NIW evidence, this helps show not only that the tool exists, but that it was designed as a scalable digital transformation and decision intelligence framework.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab38:

    st.markdown(
        '<div class="section-title">Security & Enterprise Readiness</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Conceptual enterprise security layer covering role-based access, authentication, audit logs, encryption, governance controls, and executive readiness.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # SECURITY CONTROL MODEL
    # -----------------------------

    security_controls_df = pd.DataFrame({
        "Security Domain": [
            "Role-Based Access Control",
            "Authentication",
            "Audit Logging",
            "Encryption",
            "Governance Controls",
            "Data Access Review",
            "Operational Monitoring"
        ],
        "Control Description": [
            "Define access by user role such as executive, operations manager, franchise owner, analyst, and administrator.",
            "Require authenticated access before users can view sensitive business intelligence or operational data.",
            "Track data refreshes, report downloads, scenario simulations, and high-impact user actions.",
            "Protect sensitive data in transit and at rest through secure connections and encrypted storage.",
            "Apply approval workflows, policy ownership, data stewardship, and executive review controls.",
            "Review user permissions periodically and remove access when users change roles.",
            "Monitor system usage, failed access attempts, unusual activity, and governance exceptions."
        ],
        "Current State": [
            "Conceptual / Ready to implement",
            "Conceptual / Ready to implement",
            "Conceptual / Ready to implement",
            "Conceptual / Ready to implement",
            "Partially designed through governance logic",
            "Conceptual / Ready to implement",
            "Conceptual / Ready to implement"
        ],
        "Enterprise Readiness Score": [85, 80, 78, 82, 88, 75, 77]
    })

    security_readiness_score = security_controls_df["Enterprise Readiness Score"].mean()

    if security_readiness_score >= 85:
        security_readiness_status = "Enterprise Ready"
    elif security_readiness_score >= 75:
        security_readiness_status = "Strong Foundation — Implementation Recommended"
    elif security_readiness_score >= 60:
        security_readiness_status = "Developing Security Maturity"
    else:
        security_readiness_status = "Requires Security Design"

    # -----------------------------
    # ROLE-BASED ACCESS MATRIX
    # -----------------------------

    rbac_df = pd.DataFrame({
        "Role": [
            "Executive Leadership",
            "Operations Manager",
            "Franchise Owner",
            "Data Analyst",
            "Academy Manager",
            "System Administrator"
        ],
        "Overview Dashboards": ["View", "View", "View", "View", "View", "Full Access"],
        "Financial Metrics": ["View", "View", "Limited View", "View", "Limited View", "Full Access"],
        "Customer / CRM Data": ["Aggregated View", "View", "Own Location Only", "View", "No Access", "Full Access"],
        "Workforce Data": ["Aggregated View", "View", "Own Location Only", "View", "No Access", "Full Access"],
        "Data Governance": ["Review", "Review", "Limited View", "Edit / Analyze", "Limited View", "Full Access"],
        "Admin Settings": ["No Access", "No Access", "No Access", "No Access", "No Access", "Full Access"]
    })

    # -----------------------------
    # AUDIT LOG SAMPLE
    # -----------------------------

    audit_log_df = pd.DataFrame({
        "Timestamp": [
            "2026-06-11 08:15",
            "2026-06-11 08:42",
            "2026-06-11 09:05",
            "2026-06-11 09:27",
            "2026-06-11 10:10",
            "2026-06-11 10:45"
        ],
        "User Role": [
            "Operations Manager",
            "Executive Leadership",
            "Data Analyst",
            "Franchise Owner",
            "System Administrator",
            "Academy Manager"
        ],
        "Action": [
            "Viewed workforce optimization dashboard",
            "Downloaded executive report",
            "Updated data governance scorecard",
            "Viewed own-location franchise performance",
            "Refreshed Google Places market data",
            "Viewed academy training intelligence"
        ],
        "Risk Level": ["Low", "Medium", "Medium", "Low", "High", "Low"],
        "Control Applied": [
            "Role permission validated",
            "Download event logged",
            "Governance change captured",
            "Location-level access restricted",
            "Admin access required",
            "Role permission validated"
        ]
    })

    # -----------------------------
    # DATA PROTECTION MODEL
    # -----------------------------

    data_protection_df = pd.DataFrame({
        "Data Category": [
            "Market & Census Data",
            "Financial Scenario Data",
            "Customer / CRM Data",
            "Workforce Data",
            "Franchise Performance Data",
            "Supplier & Inventory Data",
            "Academy Data"
        ],
        "Sensitivity": [
            "Low",
            "Medium",
            "High",
            "High",
            "High",
            "Medium",
            "Medium"
        ],
        "Recommended Protection": [
            "Standard access controls",
            "Role-based visibility and report logging",
            "Restricted access, aggregation, and encryption",
            "Restricted access and need-to-know visibility",
            "Location-level permissions and executive review",
            "Supplier access controls and audit trail",
            "Limited role-based access and training data governance"
        ],
        "Encryption / Control Note": [
            "HTTPS transport and trusted source documentation",
            "Secure storage and controlled report export",
            "Encrypt at rest and in transit; avoid unnecessary PII exposure",
            "Encrypt at rest and restrict detailed employee-level views",
            "Separate franchise-level access from enterprise-wide access",
            "Protect supplier terms, costs, and operational metrics",
            "Protect student/payment fields and restrict detailed records"
        ]
    })

    s1, s2, s3, s4 = st.columns(4)

    s1.metric("Security Readiness Score", f"{security_readiness_score:.1f}/100")
    s2.metric("Readiness Status", security_readiness_status)
    s3.metric("Security Domains", f"{len(security_controls_df):,}")
    s4.metric("RBAC Roles", f"{len(rbac_df):,}")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Security Control Readiness")

        fig_security = px.bar(
            security_controls_df.sort_values("Enterprise Readiness Score", ascending=False),
            x="Security Domain",
            y="Enterprise Readiness Score",
            text="Enterprise Readiness Score",
            color="Security Domain",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838",
                "#D8C28A",
                "#8C6F2F",
                "#B8923D"
            ]
        )

        fig_security.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside"
        )

        fig_security.update_layout(showlegend=False)

        st.plotly_chart(
            chart_layout(fig_security, 540),
            use_container_width=True
        )

    with c2:
        st.markdown("### Audit Risk Distribution")

        audit_risk_summary = audit_log_df.groupby(
            "Risk Level",
            as_index=False
        ).agg(
            Events=("Action", "count")
        )

        fig_audit = px.pie(
            audit_risk_summary,
            names="Risk Level",
            values="Events",
            color_discrete_sequence=[
                GOLD,
                GOLD_LIGHT,
                "#B22222"
            ]
        )

        st.plotly_chart(
            chart_layout(fig_audit, 540),
            use_container_width=True
        )

    st.markdown("### Role-Based Access Control Matrix")
    st.dataframe(
        rbac_df,
        use_container_width=True,
        height=320
    )

    st.markdown("### Security Controls & Governance Readiness")
    st.dataframe(
        security_controls_df,
        use_container_width=True,
        height=360
    )

    st.markdown("### Audit Log Framework")
    st.dataframe(
        audit_log_df,
        use_container_width=True,
        height=320
    )

    st.markdown("### Data Protection & Encryption Framework")
    st.dataframe(
        data_protection_df,
        use_container_width=True,
        height=360
    )

    st.markdown("### Enterprise Security Architecture")

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Security Architecture Flow</div>
        <div class="insight-body">
            <b>User Login / Authentication</b>
            → <b>Role-Based Permission Check</b>
            → <b>Data Access Rules</b>
            → <b>Dashboard or Report Access</b>
            → <b>Audit Logging</b>
            → <b>Governance Review</b>
            <br><br>
            This framework allows the platform to be described as enterprise-ready even before full production-grade identity management is implemented.
            It shows that the system has a clear plan for secure access, sensitive data protection, governance accountability, and auditable usage.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Security Readiness Summary</div>
        <div class="insight-body">
            The platform currently demonstrates a <b>{security_readiness_status}</b> security posture with a conceptual readiness score of
            <b>{security_readiness_score:.1f}/100</b>.
            <br><br>
            The security layer includes role-based access control, authentication design, audit logging, encryption controls, governance oversight,
            data protection rules, and enterprise monitoring requirements.
            <br><br>
            For executive and NIW evidence purposes, this strengthens the platform by showing that the solution was designed not only for analytics,
            but also for responsible enterprise deployment, controlled access, and scalable digital transformation governance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    security_markdown = f"""
# Security & Enterprise Readiness Framework

## Security Readiness Score
{security_readiness_score:.1f}/100

## Readiness Status
{security_readiness_status}

## Core Security Domains
- Role-Based Access Control
- Authentication
- Audit Logging
- Encryption
- Governance Controls
- Data Access Review
- Operational Monitoring

## Role-Based Access Control
The platform should separate permissions by role: executive leadership, operations manager, franchise owner, data analyst, academy manager, and system administrator.

## Authentication
Users should authenticate before accessing dashboards, reports, customer intelligence, workforce analytics, franchise data, or governance outputs.

## Audit Logs
The system should log report downloads, data refreshes, dashboard views, scenario simulations, governance changes, and administrator actions.

## Encryption
Sensitive data should be protected in transit and at rest. CRM, workforce, franchise, and financial data require stronger protection than public market data.

## Governance Controls
Security governance should include data ownership, stewardship, access reviews, executive oversight, and policy compliance.

## Enterprise Value
This framework helps position the platform as an enterprise-ready digital transformation system rather than a basic analytics dashboard.
"""

    st.download_button(
        label="Download Security Readiness Documentation",
        data=security_markdown,
        file_name="security_enterprise_readiness_framework.md",
        mime="text/markdown"
    )



with tab39:

    st.markdown(
        '<div class="section-title">KPI Drill-Down Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Enterprise drill-down layer for executives to explore KPIs by location, month, product, franchise, employee/stylist, and ZIP or market.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # KPI DRILL-DOWN DATA FOUNDATION
    # -----------------------------
    drill_sales_df = sales_df.copy()

    if "Date" in drill_sales_df.columns:
        drill_sales_df["Date"] = pd.to_datetime(drill_sales_df["Date"], errors="coerce")
    else:
        drill_sales_df["Date"] = pd.Timestamp.today()

    drill_sales_df = drill_sales_df.dropna(subset=["Date"]).copy()

    if "Salon_Location" not in drill_sales_df.columns:
        drill_sales_df["Salon_Location"] = "Main Salon"

    if "Product_Name" not in drill_sales_df.columns:
        drill_sales_df["Product_Name"] = "General Service / Product"

    if "Brand" not in drill_sales_df.columns:
        drill_sales_df["Brand"] = "Unassigned Brand"

    if "Units_Sold" not in drill_sales_df.columns:
        drill_sales_df["Units_Sold"] = 0

    if "Revenue" not in drill_sales_df.columns:
        drill_sales_df["Revenue"] = drill_sales_df.get("Units_Sold", 0) * drill_sales_df.get("Retail_Price", 0)

    if "Gross_Profit_Calculated" not in drill_sales_df.columns:
        drill_sales_df["Gross_Profit_Calculated"] = drill_sales_df["Revenue"] - (
            drill_sales_df.get("Units_Sold", 0) * drill_sales_df.get("Unit_Cost", 0)
        )

    if "Stylist" not in drill_sales_df.columns:
        stylist_pool = [
            "Senior Stylist A", "Senior Stylist B", "Color Specialist",
            "Extension Specialist", "Junior Stylist", "Retail Advisor"
        ]
        drill_sales_df["Stylist"] = [stylist_pool[i % len(stylist_pool)] for i in range(len(drill_sales_df))]

    if "ZIP_Code" not in drill_sales_df.columns:
        if "Zip" in drill_sales_df.columns:
            drill_sales_df["ZIP_Code"] = drill_sales_df["Zip"]
        elif "ZIP" in drill_sales_df.columns:
            drill_sales_df["ZIP_Code"] = drill_sales_df["ZIP"]
        else:
            zip_map = {
                "Miami": "33131",
                "Coral Gables": "33134",
                "Doral": "33166",
                "Aventura": "33180",
                "Sunny Isles Beach": "33160",
                "Fort Lauderdale": "33301",
                "Orlando": "32801",
                "Tampa": "33602"
            }
            drill_sales_df["ZIP_Code"] = drill_sales_df["Salon_Location"].map(zip_map).fillna("Unassigned ZIP")

    numeric_drill_cols = ["Units_Sold", "Revenue", "Gross_Profit_Calculated"]
    for col in numeric_drill_cols:
        drill_sales_df[col] = pd.to_numeric(drill_sales_df[col], errors="coerce").fillna(0)

    drill_sales_df["Month"] = drill_sales_df["Date"].dt.to_period("M").dt.to_timestamp()
    drill_sales_df["Month_Label"] = drill_sales_df["Month"].dt.strftime("%Y-%m")
    drill_sales_df["Gross_Margin_%"] = drill_sales_df.apply(
        lambda row: (row["Gross_Profit_Calculated"] / row["Revenue"] * 100)
        if row["Revenue"] > 0 else 0,
        axis=1
    )

    # -----------------------------
    # EXECUTIVE FILTERS
    # -----------------------------
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    filter_col4, filter_col5, filter_col6 = st.columns(3)

    with filter_col1:
        selected_drill_locations = st.multiselect(
            "Drill Down by Location",
            sorted(drill_sales_df["Salon_Location"].dropna().astype(str).unique()),
            default=sorted(drill_sales_df["Salon_Location"].dropna().astype(str).unique())
        )

    with filter_col2:
        selected_drill_months = st.multiselect(
            "Drill Down by Month",
            sorted(drill_sales_df["Month_Label"].dropna().astype(str).unique()),
            default=sorted(drill_sales_df["Month_Label"].dropna().astype(str).unique())
        )

    with filter_col3:
        selected_drill_products = st.multiselect(
            "Drill Down by Product",
            sorted(drill_sales_df["Product_Name"].dropna().astype(str).unique()),
            default=sorted(drill_sales_df["Product_Name"].dropna().astype(str).unique())[:12]
        )

    with filter_col4:
        selected_drill_brands = st.multiselect(
            "Drill Down by Brand / Product Family",
            sorted(drill_sales_df["Brand"].dropna().astype(str).unique()),
            default=sorted(drill_sales_df["Brand"].dropna().astype(str).unique())
        )

    with filter_col5:
        selected_drill_employees = st.multiselect(
            "Drill Down by Employee / Stylist",
            sorted(drill_sales_df["Stylist"].dropna().astype(str).unique()),
            default=sorted(drill_sales_df["Stylist"].dropna().astype(str).unique())
        )

    with filter_col6:
        selected_drill_zips = st.multiselect(
            "Drill Down by ZIP Code",
            sorted(drill_sales_df["ZIP_Code"].dropna().astype(str).unique()),
            default=sorted(drill_sales_df["ZIP_Code"].dropna().astype(str).unique())
        )

    drill_filtered_df = drill_sales_df[
        drill_sales_df["Salon_Location"].astype(str).isin(selected_drill_locations)
        & drill_sales_df["Month_Label"].astype(str).isin(selected_drill_months)
        & drill_sales_df["Product_Name"].astype(str).isin(selected_drill_products)
        & drill_sales_df["Brand"].astype(str).isin(selected_drill_brands)
        & drill_sales_df["Stylist"].astype(str).isin(selected_drill_employees)
        & drill_sales_df["ZIP_Code"].astype(str).isin(selected_drill_zips)
    ].copy()

    if drill_filtered_df.empty:
        st.warning("No KPI records match the selected drill-down filters.")
    else:
        drill_revenue = drill_filtered_df["Revenue"].sum()
        drill_units = drill_filtered_df["Units_Sold"].sum()
        drill_profit = drill_filtered_df["Gross_Profit_Calculated"].sum()
        drill_margin = (drill_profit / drill_revenue * 100) if drill_revenue > 0 else 0
        drill_transactions = len(drill_filtered_df)
        drill_avg_ticket = (drill_revenue / drill_transactions) if drill_transactions > 0 else 0

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Filtered Revenue", f"${drill_revenue:,.0f}")
        kpi2.metric("Filtered Units", f"{drill_units:,.0f}")
        kpi3.metric("Filtered Gross Profit", f"${drill_profit:,.0f}")
        kpi4.metric("Gross Margin", f"{drill_margin:.1f}%")
        kpi5.metric("Avg Transaction", f"${drill_avg_ticket:,.0f}")

        st.markdown("<br>", unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("### KPI Trend by Month")

            monthly_drill = drill_filtered_df.groupby(
                "Month",
                as_index=False
            ).agg(
                Revenue=("Revenue", "sum"),
                Gross_Profit=("Gross_Profit_Calculated", "sum"),
                Units_Sold=("Units_Sold", "sum")
            )

            fig_month_drill = px.line(
                monthly_drill,
                x="Month",
                y="Revenue",
                markers=True,
                title="Revenue Drill-Down Trend"
            )

            st.plotly_chart(
                chart_layout(fig_month_drill, 500),
                use_container_width=True
            )

        with chart_col2:
            st.markdown("### KPI by Location")

            location_drill = drill_filtered_df.groupby(
                "Salon_Location",
                as_index=False
            ).agg(
                Revenue=("Revenue", "sum"),
                Gross_Profit=("Gross_Profit_Calculated", "sum"),
                Units_Sold=("Units_Sold", "sum")
            )

            fig_location_drill = px.bar(
                location_drill.sort_values("Revenue", ascending=False),
                x="Salon_Location",
                y="Revenue",
                color="Gross_Profit",
                text="Revenue",
                color_continuous_scale=["#EFE2BD", "#C6A052", "#7D6838"]
            )

            st.plotly_chart(
                chart_layout(fig_location_drill, 500),
                use_container_width=True
            )

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            st.markdown("### KPI by Product")

            product_drill = drill_filtered_df.groupby(
                ["Product_Name", "Brand"],
                as_index=False
            ).agg(
                Revenue=("Revenue", "sum"),
                Gross_Profit=("Gross_Profit_Calculated", "sum"),
                Units_Sold=("Units_Sold", "sum")
            )

            fig_product_drill = px.bar(
                product_drill.sort_values("Revenue", ascending=False).head(15),
                x="Revenue",
                y="Product_Name",
                orientation="h",
                color="Brand",
                text="Revenue",
                color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
            )
            fig_product_drill.update_layout(yaxis=dict(autorange="reversed"))

            st.plotly_chart(
                chart_layout(fig_product_drill, 540),
                use_container_width=True
            )

        with chart_col4:
            st.markdown("### KPI by Employee / Stylist")

            employee_drill = drill_filtered_df.groupby(
                "Stylist",
                as_index=False
            ).agg(
                Revenue=("Revenue", "sum"),
                Gross_Profit=("Gross_Profit_Calculated", "sum"),
                Units_Sold=("Units_Sold", "sum")
            )

            employee_drill["Revenue_Per_Unit"] = employee_drill.apply(
                lambda row: row["Revenue"] / row["Units_Sold"] if row["Units_Sold"] > 0 else 0,
                axis=1
            )

            fig_employee_drill = px.bar(
                employee_drill.sort_values("Revenue", ascending=False),
                x="Stylist",
                y="Revenue",
                color="Gross_Profit",
                text="Revenue",
                color_continuous_scale=["#EFE2BD", "#C6A052", "#7D6838"]
            )

            st.plotly_chart(
                chart_layout(fig_employee_drill, 540),
                use_container_width=True
            )

        chart_col5, chart_col6 = st.columns(2)

        with chart_col5:
            st.markdown("### KPI by ZIP Code")

            zip_drill = drill_filtered_df.groupby(
                "ZIP_Code",
                as_index=False
            ).agg(
                Revenue=("Revenue", "sum"),
                Gross_Profit=("Gross_Profit_Calculated", "sum"),
                Units_Sold=("Units_Sold", "sum")
            )

            fig_zip_drill = px.bar(
                zip_drill.sort_values("Revenue", ascending=False),
                x="ZIP_Code",
                y="Revenue",
                color="Gross_Profit",
                text="Revenue",
                color_continuous_scale=["#EFE2BD", "#C6A052", "#7D6838"]
            )

            st.plotly_chart(
                chart_layout(fig_zip_drill, 500),
                use_container_width=True
            )

        with chart_col6:
            st.markdown("### Franchise / Salon / Academy Benchmark")

            franchise_drill = franchise_ops_df.copy()
            franchise_drill["Monthly_Revenue"] = pd.to_numeric(franchise_drill["Monthly_Revenue"], errors="coerce").fillna(0)
            franchise_drill["Monthly_Profit"] = pd.to_numeric(franchise_drill["Monthly_Profit"], errors="coerce").fillna(0)

            fig_franchise_drill = px.scatter(
                franchise_drill,
                x="Revenue_Per_Stylist",
                y="Profit_Margin_%",
                size="Monthly_Revenue",
                color="Location_Type",
                hover_name="Location_Name",
                color_discrete_sequence=[GOLD_LIGHT, GOLD, "#A9843C", "#7D6838"]
            )

            st.plotly_chart(
                chart_layout(fig_franchise_drill, 500),
                use_container_width=True
            )

        st.markdown("### Executive Drill-Down Detail Table")

        drill_detail_cols = [
            "Date", "Month_Label", "Salon_Location", "ZIP_Code", "Stylist",
            "Brand", "Product_Name", "Units_Sold", "Revenue",
            "Gross_Profit_Calculated", "Gross_Margin_%"
        ]

        available_drill_detail_cols = [
            col for col in drill_detail_cols
            if col in drill_filtered_df.columns
        ]

        st.dataframe(
            drill_filtered_df[available_drill_detail_cols].sort_values("Revenue", ascending=False),
            use_container_width=True,
            height=460
        )

        st.markdown("### KPI Drill-Down Summary by Dimension")

        summary_dimension = st.selectbox(
            "Select Summary Dimension",
            [
                "Salon_Location",
                "Month_Label",
                "Product_Name",
                "Brand",
                "Stylist",
                "ZIP_Code"
            ]
        )

        drill_dimension_summary = drill_filtered_df.groupby(
            summary_dimension,
            as_index=False
        ).agg(
            Revenue=("Revenue", "sum"),
            Gross_Profit=("Gross_Profit_Calculated", "sum"),
            Units_Sold=("Units_Sold", "sum"),
            Records=("Date", "count")
        )

        drill_dimension_summary["Gross_Margin_%"] = drill_dimension_summary.apply(
            lambda row: (row["Gross_Profit"] / row["Revenue"] * 100)
            if row["Revenue"] > 0 else 0,
            axis=1
        ).round(1)

        st.dataframe(
            drill_dimension_summary.sort_values("Revenue", ascending=False),
            use_container_width=True,
            height=360
        )

        top_location = location_drill.sort_values("Revenue", ascending=False).iloc[0]["Salon_Location"]
        top_product = product_drill.sort_values("Revenue", ascending=False).iloc[0]["Product_Name"]
        top_employee = employee_drill.sort_values("Revenue", ascending=False).iloc[0]["Stylist"]

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Executive KPI Drill-Down Interpretation</div>
            <div class="insight-body">
                Under the selected filters, the strongest revenue location is <b>{top_location}</b>,
                the strongest product is <b>{top_product}</b>, and the strongest employee/stylist signal is <b>{top_employee}</b>.
                <br><br>
                Filtered revenue equals <b>${drill_revenue:,.0f}</b>, with gross profit of
                <b>${drill_profit:,.0f}</b> and margin of <b>{drill_margin:.1f}%</b>.
                <br><br>
                This transforms the dashboard from executive summary reporting into a true operational intelligence system,
                allowing leaders to move from high-level KPI visibility into location, month, product, franchise, employee,
                and ZIP-level diagnostic analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        drill_markdown = f"""
# KPI Drill-Down Center Documentation

## Purpose
This module allows enterprise executives to drill down from summary KPIs into operational detail.

## Drill-Down Dimensions
- Location
- Month
- Product
- Brand / Product Family
- Franchise / Salon / Academy Location Type
- Employee / Stylist
- ZIP Code

## Filtered KPI Output
- Revenue: ${drill_revenue:,.0f}
- Units Sold: {drill_units:,.0f}
- Gross Profit: ${drill_profit:,.0f}
- Gross Margin: {drill_margin:.1f}%
- Average Transaction: ${drill_avg_ticket:,.0f}

## Executive Value
This capability supports enterprise reporting, operational diagnostics, franchise benchmarking, workforce accountability, product analysis, and ZIP-level market validation.
"""

        st.download_button(
            label="Download KPI Drill-Down Documentation",
            data=drill_markdown,
            file_name="kpi_drill_down_center_documentation.md",
            mime="text/markdown"
        )


with tab40:

    st.markdown(
        '<div class="section-title">Real-Time Operational Alerts Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Automated threshold monitoring, anomaly detection, operational risk alerts, and email-ready executive notifications.</div>',
        unsafe_allow_html=True
    )

    alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)

    with alert_col1:
        low_stock_threshold = st.number_input(
            "Low Stock Threshold",
            min_value=0,
            max_value=500,
            value=10,
            step=1
        )

    with alert_col2:
        stockout_risk_threshold = st.slider(
            "Stockout Risk Alert Threshold %",
            0,
            100,
            70
        )

    with alert_col3:
        margin_threshold = st.slider(
            "Low Margin Alert Threshold %",
            0,
            100,
            35
        )

    with alert_col4:
        anomaly_sensitivity = st.slider(
            "Anomaly Sensitivity",
            1.0,
            3.0,
            2.0,
            0.1
        )

    alerts = []

    def add_alert(category, severity, location, entity, metric, current_value, threshold, recommendation):
        alerts.append({
            "Alert_Category": category,
            "Severity": severity,
            "Location": location,
            "Entity": entity,
            "Metric": metric,
            "Current_Value": current_value,
            "Threshold": threshold,
            "Recommendation": recommendation
        })

    # -----------------------------
    # INVENTORY THRESHOLD ALERTS
    # -----------------------------

    if "inventory_df" in globals() and not inventory_df.empty:
        inventory_alert_df = inventory_df.copy()
        inventory_alert_df["Current_Stock"] = pd.to_numeric(
            inventory_alert_df.get("Current_Stock", 0),
            errors="coerce"
        ).fillna(0)

        inventory_alert_df["Reorder_Point"] = pd.to_numeric(
            inventory_alert_df.get("Reorder_Point", 0),
            errors="coerce"
        ).fillna(0)

        for _, row in inventory_alert_df.iterrows():
            location_value = row.get("Salon_Location", "Unknown Location")
            product_value = row.get("Product_Name", "Unknown Product")
            current_stock = row.get("Current_Stock", 0)
            reorder_point = row.get("Reorder_Point", 0)

            if current_stock <= low_stock_threshold:
                add_alert(
                    "Inventory Threshold",
                    "High" if current_stock <= 5 else "Medium",
                    location_value,
                    product_value,
                    "Current Stock",
                    current_stock,
                    low_stock_threshold,
                    "Review inventory immediately and prepare replenishment order."
                )

            if current_stock <= reorder_point:
                add_alert(
                    "Reorder Point Breach",
                    "High",
                    location_value,
                    product_value,
                    "Current Stock vs Reorder Point",
                    current_stock,
                    reorder_point,
                    "Trigger reorder workflow and validate forecasted demand before purchase order approval."
                )

    # -----------------------------
    # SUPPLY CHAIN RISK ALERTS
    # -----------------------------

    if "supply_chain_df" in globals() and not supply_chain_df.empty:
        supply_alert_df = supply_chain_df.copy()
        supply_alert_df["Stockout_Risk_%"] = pd.to_numeric(
            supply_alert_df.get("Stockout_Risk_%", 0),
            errors="coerce"
        ).fillna(0)

        supply_alert_df["Supplier_Performance_Score"] = pd.to_numeric(
            supply_alert_df.get("Supplier_Performance_Score", 100),
            errors="coerce"
        ).fillna(100)

        for _, row in supply_alert_df.iterrows():
            location_value = row.get("Salon_Location", "Unknown Location")
            product_value = row.get("Product_Name", "Unknown Product")
            stockout_risk = row.get("Stockout_Risk_%", 0)
            supplier_score = row.get("Supplier_Performance_Score", 100)

            if stockout_risk >= stockout_risk_threshold:
                add_alert(
                    "Stockout Risk",
                    "Critical" if stockout_risk >= 85 else "High",
                    location_value,
                    product_value,
                    "Stockout Risk %",
                    f"{stockout_risk:.1f}%",
                    f"{stockout_risk_threshold}%",
                    "Increase safety stock, expedite replenishment, or review supplier lead time reliability."
                )

            if supplier_score < 75:
                add_alert(
                    "Supplier Performance",
                    "High",
                    location_value,
                    row.get("Supplier", "Unknown Supplier"),
                    "Supplier Performance Score",
                    f"{supplier_score:.1f}",
                    "75",
                    "Review supplier scorecard, OTIF, fill rate, and backup supplier options."
                )

    # -----------------------------
    # SALES / MARGIN ALERTS
    # -----------------------------

    if "sales_df" in globals() and not sales_df.empty:
        sales_alert_df = sales_df.copy()

        sales_alert_df["Revenue"] = pd.to_numeric(
            sales_alert_df.get("Revenue", 0),
            errors="coerce"
        ).fillna(0)

        sales_alert_df["Gross_Profit_Calculated"] = pd.to_numeric(
            sales_alert_df.get("Gross_Profit_Calculated", 0),
            errors="coerce"
        ).fillna(0)

        sales_alert_df["Gross_Margin_%"] = sales_alert_df.apply(
            lambda row: (row["Gross_Profit_Calculated"] / row["Revenue"] * 100)
            if row["Revenue"] > 0 else 0,
            axis=1
        )

        product_margin_alerts = sales_alert_df.groupby(
            ["Salon_Location", "Product_Name"],
            as_index=False
        ).agg(
            Revenue=("Revenue", "sum"),
            Gross_Profit=("Gross_Profit_Calculated", "sum")
        )

        product_margin_alerts["Gross_Margin_%"] = product_margin_alerts.apply(
            lambda row: (row["Gross_Profit"] / row["Revenue"] * 100)
            if row["Revenue"] > 0 else 0,
            axis=1
        )

        for _, row in product_margin_alerts.iterrows():
            margin_value = row["Gross_Margin_%"]

            if row["Revenue"] > 0 and margin_value < margin_threshold:
                add_alert(
                    "Profitability Threshold",
                    "Medium" if margin_value >= 20 else "High",
                    row.get("Salon_Location", "Unknown Location"),
                    row.get("Product_Name", "Unknown Product"),
                    "Gross Margin %",
                    f"{margin_value:.1f}%",
                    f"{margin_threshold}%",
                    "Review discounting, pricing, unit cost, service mix, or product profitability."
                )

        # -----------------------------
        # MONTHLY SALES ANOMALY DETECTION
        # -----------------------------

        sales_alert_df["Date"] = pd.to_datetime(sales_alert_df["Date"], errors="coerce")
        sales_alert_df = sales_alert_df.dropna(subset=["Date"])

        monthly_location_sales_alerts = (
            sales_alert_df
            .groupby([
                pd.Grouper(key="Date", freq="MS"),
                "Salon_Location"
            ], as_index=False)
            .agg(Revenue=("Revenue", "sum"))
        )

        anomaly_base = monthly_location_sales_alerts.sort_values("Date").copy()
        anomaly_base["Rolling_Avg"] = anomaly_base.groupby("Salon_Location")["Revenue"].transform(
            lambda x: x.rolling(3).mean()
        )
        anomaly_base["Rolling_Std"] = anomaly_base.groupby("Salon_Location")["Revenue"].transform(
            lambda x: x.rolling(3).std()
        )
        anomaly_base["High_Threshold"] = anomaly_base["Rolling_Avg"] + anomaly_sensitivity * anomaly_base["Rolling_Std"]
        anomaly_base["Low_Threshold"] = anomaly_base["Rolling_Avg"] - anomaly_sensitivity * anomaly_base["Rolling_Std"]

        detected_anomalies = anomaly_base[
            (
                anomaly_base["Revenue"] > anomaly_base["High_Threshold"]
            )
            |
            (
                anomaly_base["Revenue"] < anomaly_base["Low_Threshold"]
            )
        ].copy()

        for _, row in detected_anomalies.iterrows():
            anomaly_type = "Revenue Spike" if row["Revenue"] > row["High_Threshold"] else "Revenue Drop"
            severity = "High" if anomaly_type == "Revenue Drop" else "Medium"

            add_alert(
                "Anomaly Detection",
                severity,
                row.get("Salon_Location", "Unknown Location"),
                anomaly_type,
                "Monthly Revenue",
                f"${row['Revenue']:,.0f}",
                f"Expected around ${row['Rolling_Avg']:,.0f}",
                "Investigate operational causes such as campaign activity, staffing changes, stockouts, pricing, or booking volume shifts."
            )

    # -----------------------------
    # CUSTOMER / CRM ALERTS
    # -----------------------------

    if "customer_df" in globals() and not customer_df.empty:
        crm_alert_df = customer_df.copy()

        if "Churn_Risk_%" in crm_alert_df.columns:
            crm_alert_df["Churn_Risk_%"] = pd.to_numeric(
                crm_alert_df["Churn_Risk_%"],
                errors="coerce"
            ).fillna(0)

            high_churn_customers = crm_alert_df[crm_alert_df["Churn_Risk_%"] >= 70]

            if len(high_churn_customers) > 0:
                add_alert(
                    "Customer Churn Risk",
                    "High",
                    "CRM Portfolio",
                    "High-risk customer segment",
                    "Customers with churn risk >= 70%",
                    len(high_churn_customers),
                    "0",
                    "Launch retention outreach, service follow-up, loyalty offer, or rebooking campaign."
                )

    alerts_df = pd.DataFrame(alerts)

    if alerts_df.empty:
        total_alerts = 0
        critical_alerts = 0
        high_alerts = 0
        medium_alerts = 0
    else:
        total_alerts = len(alerts_df)
        critical_alerts = len(alerts_df[alerts_df["Severity"] == "Critical"])
        high_alerts = len(alerts_df[alerts_df["Severity"] == "High"])
        medium_alerts = len(alerts_df[alerts_df["Severity"] == "Medium"])

    a1, a2, a3, a4 = st.columns(4)

    a1.metric("Total Active Alerts", f"{total_alerts:,}")
    a2.metric("Critical Alerts", f"{critical_alerts:,}")
    a3.metric("High Alerts", f"{high_alerts:,}")
    a4.metric("Medium Alerts", f"{medium_alerts:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    if alerts_df.empty:
        st.success("No active operational alerts detected under the selected thresholds.")
    else:
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        alerts_df["Severity_Order"] = alerts_df["Severity"].map(severity_order).fillna(9)
        alerts_df = alerts_df.sort_values(["Severity_Order", "Alert_Category", "Location"])

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Alerts by Severity")

            severity_summary = alerts_df.groupby(
                "Severity",
                as_index=False
            ).agg(Alerts=("Alert_Category", "count"))

            fig_alert_severity = px.bar(
                severity_summary,
                x="Severity",
                y="Alerts",
                color="Severity",
                text="Alerts",
                color_discrete_map={
                    "Critical": "#7A0000",
                    "High": "#B22222",
                    "Medium": "#C6A052",
                    "Low": "#8A8A8A"
                }
            )

            st.plotly_chart(
                chart_layout(fig_alert_severity, 460),
                use_container_width=True
            )

        with c2:
            st.markdown("### Alerts by Category")

            category_summary = alerts_df.groupby(
                "Alert_Category",
                as_index=False
            ).agg(Alerts=("Severity", "count"))

            fig_alert_category = px.bar(
                category_summary.sort_values("Alerts", ascending=False),
                x="Alert_Category",
                y="Alerts",
                color="Alerts",
                text="Alerts",
                color_continuous_scale=[
                    "#EFE2BD",
                    "#C6A052",
                    "#7D6838"
                ]
            )

            st.plotly_chart(
                chart_layout(fig_alert_category, 460),
                use_container_width=True
            )

        st.markdown("### Active Operational Alert Queue")

        st.dataframe(
            alerts_df.drop(columns=["Severity_Order"], errors="ignore"),
            use_container_width=True,
            height=480
        )

    # -----------------------------
    # EMAIL-READY NOTIFICATION REPORT
    # -----------------------------

    if alerts_df.empty:
        email_summary = "No active operational alerts were detected under the current thresholds."
        top_alert_lines = "No action required at this time."
    else:
        top_alert_lines = "\n".join(
            [
                f"- [{row['Severity']}] {row['Alert_Category']} | {row['Location']} | {row['Entity']} | {row['Metric']}: {row['Current_Value']}"
                for _, row in alerts_df.head(10).iterrows()
            ]
        )

        email_summary = f"""
Active alert count: {total_alerts}
Critical alerts: {critical_alerts}
High alerts: {high_alerts}
Medium alerts: {medium_alerts}
""".strip()

    alert_email_body = f"""
Subject: Operational Alert Summary - Strategic Expansion Intelligence Platform

Hello,

The operational monitoring engine has completed its latest threshold and anomaly scan.

{email_summary}

Top alerts:
{top_alert_lines}

Recommended next actions:
1. Review critical and high alerts first.
2. Validate whether alerts are caused by stockouts, supplier delays, pricing issues, campaign spikes, or data quality problems.
3. Assign an owner for each high-priority issue.
4. Re-run the dashboard after corrective actions are completed.

This notification supports automated monitoring, executive governance, and operational risk management.
""".strip()

    st.markdown("### Email-Ready Alert Notification")
    st.text_area(
        "Copy this alert summary into an email or internal message",
        alert_email_body,
        height=300
    )

    st.download_button(
        label="Download Alert Report CSV",
        data=alerts_df.drop(columns=["Severity_Order"], errors="ignore").to_csv(index=False),
        file_name="real_time_operational_alerts.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download Email Alert Summary",
        data=alert_email_body,
        file_name="operational_alert_email_summary.txt",
        mime="text/plain"
    )

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Alerting Interpretation</div>
        <div class="insight-body">
            This module converts the platform from passive reporting into active operational monitoring.
            <br><br>
            It continuously evaluates inventory thresholds, reorder breaches, stockout risk, supplier performance,
            margin pressure, revenue anomalies, and customer risk signals when available.
            <br><br>
            Current active alerts: <b>{total_alerts:,}</b>. Critical alerts: <b>{critical_alerts:,}</b>.
            <br><br>
            This strengthens the platform’s alignment with enterprise analytics, automated monitoring,
            anomaly detection, governance controls, and executive operational readiness.
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab41:

    st.markdown(
        '<div class="section-title">Workflow Automation Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Automated operational workflows for replenishment, supplier notifications, escalations, and executive reporting.</div>',
        unsafe_allow_html=True
    )

    automation_mode = st.selectbox(
        "Automation Mode",
        [
            "Simulation Only",
            "Ready for Human Approval",
            "Auto-Execute Eligible Workflows"
        ]
    )

    escalation_sla_hours = st.slider(
        "Escalation SLA for High-Priority Issues (Hours)",
        4,
        72,
        24
    )

    auto_replenishment_limit = st.number_input(
        "Auto-Replenishment Approval Limit ($)",
        min_value=0,
        max_value=50000,
        value=2500,
        step=250
    )

    workflow_rows = []

    def add_workflow(workflow_type, priority, location, owner, trigger, action, status, estimated_value, next_step):
        workflow_rows.append({
            "Workflow_Type": workflow_type,
            "Priority": priority,
            "Location": location,
            "Owner": owner,
            "Trigger": trigger,
            "Automated_Action": action,
            "Status": status,
            "Estimated_Value": estimated_value,
            "Next_Step": next_step
        })

    # -----------------------------
    # AUTO-REPLENISHMENT WORKFLOWS
    # -----------------------------

    replenishment_source = None

    if "supply_chain_df" in globals() and not supply_chain_df.empty:
        replenishment_source = supply_chain_df.copy()
    elif "reorder_df" in globals() and not reorder_df.empty:
        replenishment_source = reorder_df.copy()

    if replenishment_source is not None and not replenishment_source.empty:
        replenishment_source["Current_Stock"] = pd.to_numeric(
            replenishment_source.get("Current_Stock", 0),
            errors="coerce"
        ).fillna(0)

        if "Optimized_Reorder_Qty" not in replenishment_source.columns:
            replenishment_source["Optimized_Reorder_Qty"] = pd.to_numeric(
                replenishment_source.get("Recommended_Reorder_Qty", 0),
                errors="coerce"
            ).fillna(0)
        else:
            replenishment_source["Optimized_Reorder_Qty"] = pd.to_numeric(
                replenishment_source["Optimized_Reorder_Qty"],
                errors="coerce"
            ).fillna(0)

        if "Unit_Cost" not in replenishment_source.columns:
            unit_cost_lookup_auto = sales_df.groupby(
                ["Brand", "Product_ID", "Product_Name"],
                as_index=False
            ).agg(Unit_Cost=("Unit_Cost", "mean"))

            replenishment_source = replenishment_source.merge(
                unit_cost_lookup_auto,
                on=["Brand", "Product_ID", "Product_Name"],
                how="left"
            )

        replenishment_source["Unit_Cost"] = pd.to_numeric(
            replenishment_source.get("Unit_Cost", 0),
            errors="coerce"
        ).fillna(0)

        replenishment_source["Estimated_Replenishment_Value"] = (
            replenishment_source["Optimized_Reorder_Qty"]
            * replenishment_source["Unit_Cost"]
        ).round(2)

        auto_replenishment_items = replenishment_source[
            replenishment_source["Optimized_Reorder_Qty"] > 0
        ].copy()

        for _, row in auto_replenishment_items.iterrows():
            estimated_value = row.get("Estimated_Replenishment_Value", 0)
            supplier_name = row.get("Supplier", "Assigned Supplier")

            if estimated_value <= auto_replenishment_limit:
                status = "Auto-Approval Eligible" if automation_mode == "Auto-Execute Eligible Workflows" else "Pending Approval"
                priority = "High" if row.get("Supply_Chain_Risk_Level", "") == "High Risk" else "Medium"
                next_step = "Generate supplier purchase request and confirm availability."
            else:
                status = "Executive Approval Required"
                priority = "High"
                next_step = "Route replenishment request to operations leader for approval."

            add_workflow(
                "Auto-Replenishment",
                priority,
                row.get("Salon_Location", "Unknown Location"),
                "Inventory / Operations",
                f"{row.get('Product_Name', 'Product')} requires {row.get('Optimized_Reorder_Qty', 0):,.0f} units",
                f"Create replenishment workflow for {supplier_name}",
                status,
                estimated_value,
                next_step
            )

    # -----------------------------
    # SUPPLIER NOTIFICATION WORKFLOWS
    # -----------------------------

    if "supplier_scorecard_df" in globals() and not supplier_scorecard_df.empty:
        supplier_alerts = supplier_scorecard_df.copy()

        supplier_alerts["Avg_Performance_Score"] = pd.to_numeric(
            supplier_alerts["Avg_Performance_Score"],
            errors="coerce"
        ).fillna(0)

        low_supplier_performance = supplier_alerts[
            supplier_alerts["Avg_Performance_Score"] < 85
        ].copy()

        for _, row in low_supplier_performance.iterrows():
            priority = "High" if row["Avg_Performance_Score"] < 75 else "Medium"

            add_workflow(
                "Supplier Notification",
                priority,
                "Supplier Network",
                "Supply Chain Lead",
                f"Supplier score below target: {row['Avg_Performance_Score']:.1f}/100",
                f"Send performance follow-up to {row.get('Supplier', 'supplier')}",
                "Ready to Send",
                row.get("Total_Projected_Logistics_Cost", 0),
                "Request delivery reliability, fill rate, and lead time improvement plan."
            )

    # -----------------------------
    # AUTOMATED ESCALATION WORKFLOWS
    # -----------------------------

    if "alerts_df" in globals() and not alerts_df.empty:
        escalation_alerts = alerts_df.copy()
        escalation_alerts = escalation_alerts[
            escalation_alerts["Severity"].isin(["Critical", "High"])
        ].copy()

        for _, row in escalation_alerts.head(25).iterrows():
            owner = "Executive / Operations Lead" if row["Severity"] == "Critical" else "Department Owner"

            add_workflow(
                "Automated Escalation",
                row["Severity"],
                row.get("Location", "Unknown Location"),
                owner,
                f"{row.get('Alert_Category', 'Alert')} - {row.get('Metric', 'Metric')}",
                "Create escalation ticket and assign owner",
                f"Escalate within {escalation_sla_hours} hours",
                0,
                row.get("Recommended_Action", "Review issue and confirm corrective action.")
            )

    # -----------------------------
    # AUTOMATED REPORTING WORKFLOWS
    # -----------------------------

    reporting_recipients = [
        "Executive Team",
        "Operations Lead",
        "Supply Chain Lead",
        "Franchise Management"
    ]

    for recipient in reporting_recipients:
        add_workflow(
            "Automated Reporting",
            "Medium",
            "Enterprise Portfolio",
            recipient,
            "Scheduled performance review cycle",
            f"Generate weekly dashboard summary for {recipient}",
            "Scheduled",
            0,
            "Review KPIs, open alerts, workflow queue, and pending approvals."
        )

    # -----------------------------
    # DATA GOVERNANCE / QUALITY WORKFLOWS
    # -----------------------------

    if "validation_df" in globals() and not validation_df.empty:
        validation_workflows = validation_df.copy()

        for _, row in validation_workflows.head(20).iterrows():
            add_workflow(
                "Data Governance Workflow",
                row.get("Severity", "Medium"),
                row.get("Dataset", "Data Platform"),
                "Data Steward",
                f"{row.get('Issue_Type', 'Data issue')} in {row.get('Field', 'field')}",
                "Create data correction task",
                "Pending Data Steward Review",
                0,
                row.get("Recommendation", "Validate source data and correct the issue.")
            )

    workflow_df = pd.DataFrame(workflow_rows)

    if workflow_df.empty:
        total_workflows = 0
        high_priority_workflows = 0
        auto_eligible_workflows = 0
        pending_approval_workflows = 0
    else:
        total_workflows = len(workflow_df)
        high_priority_workflows = len(workflow_df[workflow_df["Priority"].isin(["Critical", "High"] )])
        auto_eligible_workflows = len(workflow_df[workflow_df["Status"] == "Auto-Approval Eligible"])
        pending_approval_workflows = len(workflow_df[workflow_df["Status"].str.contains("Approval", case=False, na=False)])

    w1, w2, w3, w4 = st.columns(4)

    w1.metric("Active Workflows", f"{total_workflows:,}")
    w2.metric("High Priority", f"{high_priority_workflows:,}")
    w3.metric("Auto-Eligible", f"{auto_eligible_workflows:,}")
    w4.metric("Pending Approval", f"{pending_approval_workflows:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    if workflow_df.empty:
        st.success("No active automation workflows generated under the current rules.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Workflow Queue by Type")

            workflow_type_summary = workflow_df.groupby(
                "Workflow_Type",
                as_index=False
            ).agg(Workflows=("Priority", "count"))

            fig_workflow_type = px.bar(
                workflow_type_summary.sort_values("Workflows", ascending=False),
                x="Workflow_Type",
                y="Workflows",
                color="Workflow_Type",
                text="Workflows",
                color_discrete_sequence=[
                    GOLD_LIGHT,
                    GOLD,
                    "#A9843C",
                    "#7D6838",
                    "#3E3E3E"
                ]
            )

            fig_workflow_type.update_layout(showlegend=False)

            st.plotly_chart(
                chart_layout(fig_workflow_type, 480),
                use_container_width=True
            )

        with c2:
            st.markdown("### Workflow Queue by Status")

            workflow_status_summary = workflow_df.groupby(
                "Status",
                as_index=False
            ).agg(Workflows=("Priority", "count"))

            fig_workflow_status = px.bar(
                workflow_status_summary.sort_values("Workflows", ascending=False),
                x="Status",
                y="Workflows",
                color="Workflows",
                text="Workflows",
                color_continuous_scale=[
                    "#EFE2BD",
                    "#C6A052",
                    "#7D6838"
                ]
            )

            st.plotly_chart(
                chart_layout(fig_workflow_status, 480),
                use_container_width=True
            )

        st.markdown("### Automation Workflow Queue")

        priority_order = {
            "Critical": 0,
            "High": 1,
            "Medium": 2,
            "Low": 3
        }

        workflow_df["Priority_Order"] = workflow_df["Priority"].map(priority_order).fillna(9)

        st.dataframe(
            workflow_df.sort_values(
                ["Priority_Order", "Workflow_Type", "Location"]
            ).drop(columns=["Priority_Order"], errors="ignore"),
            use_container_width=True,
            height=520
        )

    # -----------------------------
    # SUPPLIER EMAIL TEMPLATE
    # -----------------------------

    supplier_workflows = workflow_df[
        workflow_df["Workflow_Type"].isin(["Supplier Notification", "Auto-Replenishment"])
    ].copy() if not workflow_df.empty else pd.DataFrame()

    if supplier_workflows.empty:
        supplier_email_body = "No supplier notification or replenishment workflows are currently pending."
    else:
        supplier_lines = "\n".join(
            [
                f"- {row['Priority']} | {row['Location']} | {row['Trigger']} | Status: {row['Status']}"
                for _, row in supplier_workflows.head(12).iterrows()
            ]
        )

        supplier_email_body = f"""
Subject: Supplier Workflow Notification - Action Required

Hello,

The Strategic Expansion Intelligence Platform generated the following supplier-related workflows:

{supplier_lines}

Requested action:
1. Confirm inventory availability and estimated delivery timeline.
2. Confirm any lead time, fill rate, or shipment constraints.
3. Provide corrective action plan for any supplier performance issue.
4. Reply with expected resolution date.

Thank you.
""".strip()

    st.markdown("### Supplier Notification Template")

    st.text_area(
        "Copy this message into a supplier email or internal procurement note",
        supplier_email_body,
        height=300
    )

    # -----------------------------
    # EXECUTIVE REPORTING TEMPLATE
    # -----------------------------

    if workflow_df.empty:
        executive_workflow_summary = "No active workflows are currently pending."
    else:
        executive_workflow_summary = f"""
Active workflows: {total_workflows}
High-priority workflows: {high_priority_workflows}
Auto-approval eligible workflows: {auto_eligible_workflows}
Pending approval workflows: {pending_approval_workflows}
Automation mode: {automation_mode}
Escalation SLA: {escalation_sla_hours} hours
""".strip()

    executive_report_body = f"""
Subject: Weekly Workflow Automation Summary

Hello,

The workflow automation engine generated the following operational summary:

{executive_workflow_summary}

Recommended executive actions:
1. Approve high-value replenishment workflows above the approval threshold.
2. Review critical and high-priority escalations.
3. Confirm supplier corrective action plans where performance is below target.
4. Review recurring data governance issues that may affect reporting reliability.

This workflow layer supports transformation governance, automated reporting, supplier accountability, replenishment automation, and scalable operating discipline.
""".strip()

    st.markdown("### Executive Reporting Template")

    st.text_area(
        "Copy this summary into a weekly executive update",
        executive_report_body,
        height=300
    )

    if not workflow_df.empty:
        st.download_button(
            label="Download Workflow Queue CSV",
            data=workflow_df.drop(columns=["Priority_Order"], errors="ignore").to_csv(index=False),
            file_name="workflow_automation_queue.csv",
            mime="text/csv"
        )

    st.download_button(
        label="Download Supplier Notification Template",
        data=supplier_email_body,
        file_name="supplier_workflow_notification.txt",
        mime="text/plain"
    )

    st.download_button(
        label="Download Executive Workflow Summary",
        data=executive_report_body,
        file_name="executive_workflow_summary.txt",
        mime="text/plain"
    )

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Workflow Automation Interpretation</div>
        <div class="insight-body">
            This module converts operational intelligence into action-oriented workflows.
            <br><br>
            It creates automated replenishment workflows, supplier follow-up messages, escalation tasks,
            governance workflows, and scheduled reporting summaries.
            <br><br>
            Current active workflows: <b>{total_workflows:,}</b>. High-priority workflows: <b>{high_priority_workflows:,}</b>.
            <br><br>
            This strengthens the platform’s alignment with digital transformation consulting,
            operating model design, workflow automation, supplier coordination, and executive governance.
        </div>
    </div>
    """, unsafe_allow_html=True)



with tab42:

    st.markdown(
        '<div class="section-title">Strategic Consulting Layer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-note">Consulting-oriented maturity assessment and transformation roadmap generator across AI, supply chain, digital, operational, and governance capabilities.</div>',
        unsafe_allow_html=True
    )

    # -----------------------------
    # STRATEGIC MATURITY ASSESSMENT ENGINE
    # -----------------------------

    def maturity_stage(score):
        if score < 40:
            return "Foundational"
        elif score < 60:
            return "Emerging"
        elif score < 75:
            return "Scaling"
        elif score < 90:
            return "Advanced"
        else:
            return "Leading Practice"

    def maturity_recommendation(capability, score):
        if capability == "AI Maturity":
            if score < 60:
                return "Expand predictive models, improve forecast history, and add model performance monitoring."
            elif score < 80:
                return "Operationalize AI outputs into workflows, alerts, and executive decision routines."
            else:
                return "Move toward governed AI portfolio management and continuous model improvement."
        elif capability == "Supply Chain Maturity":
            if score < 60:
                return "Standardize safety stock, lead time, supplier reliability, and reorder governance."
            elif score < 80:
                return "Improve service level optimization, supplier scorecards, and cost-to-serve analytics."
            else:
                return "Advance toward predictive supply chain control tower capabilities."
        elif capability == "Digital Maturity":
            if score < 60:
                return "Define core digital workflows, system ownership, adoption KPIs, and security controls."
            elif score < 80:
                return "Automate recurring workflows and integrate operational alerts with management routines."
            else:
                return "Scale digital operating model across locations with governance and automation."
        elif capability == "Operational Maturity":
            if score < 60:
                return "Standardize location KPIs, labor utilization, customer metrics, and franchise benchmarking."
            elif score < 80:
                return "Use drill-down analytics to manage performance by location, employee, product, and customer segment."
            else:
                return "Build cross-location operating discipline and continuous improvement cadence."
        else:
            if score < 60:
                return "Assign data owners, clean master data, document lineage, and reduce duplication."
            elif score < 80:
                return "Formalize governance policy scoring, auditability, and source trust monitoring."
            else:
                return "Scale data governance council routines and enterprise reporting controls."

    # AI maturity
    try:
        ai_forecast_available = 0 if ai_forecast_df.empty else 1
        ai_confidence_component = min(100, max(0, ai_forecast_df["Forecast_Confidence"].mean())) if ai_forecast_available else 35
        ai_maturity_score = (
            ai_confidence_component * 0.45
            + (80 if ai_forecast_available else 20) * 0.35
            + (75 if "ml_recommendations_df" in globals() else 45) * 0.20
        )
    except Exception:
        ai_maturity_score = 45

    # Supply chain maturity
    try:
        avg_supplier_score = supplier_scorecard_df["Avg_Performance_Score"].mean() if not supplier_scorecard_df.empty else 50
        avg_stockout = supply_chain_df["Stockout_Risk_%"].mean() if not supply_chain_df.empty else 50
        supply_chain_maturity_score = (
            avg_supplier_score * 0.40
            + (100 - avg_stockout) * 0.35
            + (85 if "supply_chain_df" in globals() else 40) * 0.25
        )
    except Exception:
        supply_chain_maturity_score = 50

    # Digital maturity
    try:
        security_score = enterprise_security_score if "enterprise_security_score" in globals() else 60
        workflow_score = 85 if "workflow_df" in globals() and not workflow_df.empty else 55
        alert_score = 85 if "alert_df" in globals() and not alert_df.empty else 55
        digital_maturity_score = security_score * 0.35 + workflow_score * 0.35 + alert_score * 0.30
    except Exception:
        digital_maturity_score = 60

    # Operational maturity
    try:
        franchise_score = franchise_operational_score if "franchise_operational_score" in globals() else 65
        labor_score = labor_optimization_score if "labor_optimization_score" in globals() else 60
        drilldown_score = 85 if "kpi_drilldown_df" in globals() else 60
        operational_maturity_score = franchise_score * 0.35 + labor_score * 0.35 + drilldown_score * 0.30
    except Exception:
        operational_maturity_score = 62

    # Governance maturity
    try:
        governance_policy_score = governance_maturity_score if "governance_maturity_score" in globals() else data_validation_score
        source_trust_score = source_trust_summary["Source_Trust_Score"].mean() if "source_trust_summary" in globals() and not source_trust_summary.empty else 65
        data_governance_maturity_score = governance_policy_score * 0.60 + source_trust_score * 0.40
    except Exception:
        data_governance_maturity_score = data_validation_score if "data_validation_score" in globals() else 60

    consulting_maturity_df = pd.DataFrame({
        "Capability": [
            "AI Maturity",
            "Supply Chain Maturity",
            "Digital Maturity",
            "Operational Maturity",
            "Data Governance Maturity"
        ],
        "Maturity_Score": [
            round(ai_maturity_score, 1),
            round(supply_chain_maturity_score, 1),
            round(digital_maturity_score, 1),
            round(operational_maturity_score, 1),
            round(data_governance_maturity_score, 1)
        ]
    })

    consulting_maturity_df["Maturity_Stage"] = consulting_maturity_df["Maturity_Score"].apply(maturity_stage)
    consulting_maturity_df["Consulting_Recommendation"] = consulting_maturity_df.apply(
        lambda row: maturity_recommendation(row["Capability"], row["Maturity_Score"]),
        axis=1
    )

    strategic_maturity_score = consulting_maturity_df["Maturity_Score"].mean()
    weakest_capability = consulting_maturity_df.sort_values("Maturity_Score").iloc[0]
    strongest_capability = consulting_maturity_df.sort_values("Maturity_Score", ascending=False).iloc[0]

    if strategic_maturity_score >= 80:
        strategic_position = "Advanced Transformation Platform"
    elif strategic_maturity_score >= 65:
        strategic_position = "Scaling Transformation Capability"
    elif strategic_maturity_score >= 50:
        strategic_position = "Emerging Consulting Operating Model"
    else:
        strategic_position = "Foundational Transformation Readiness"

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Strategic Maturity Score", f"{strategic_maturity_score:.1f}/100")
    c2.metric("Maturity Stage", maturity_stage(strategic_maturity_score))
    c3.metric("Strongest Capability", strongest_capability["Capability"])
    c4.metric("Highest Gap", weakest_capability["Capability"])

    st.markdown("<br>", unsafe_allow_html=True)

    colA, colB = st.columns([1.2, 1])

    with colA:
        st.markdown("### Maturity Assessment by Capability")

        fig_maturity = px.bar(
            consulting_maturity_df.sort_values("Maturity_Score", ascending=False),
            x="Capability",
            y="Maturity_Score",
            color="Maturity_Stage",
            text="Maturity_Score",
            color_discrete_sequence=[
                GOLD_LIGHT,
                GOLD,
                "#A9843C",
                "#7D6838",
                "#4F9D69"
            ]
        )

        fig_maturity.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_maturity.update_layout(
            yaxis=dict(range=[0, 110]),
            xaxis_title="Capability Area",
            yaxis_title="Maturity Score"
        )

        st.plotly_chart(
            chart_layout(fig_maturity, 540),
            use_container_width=True
        )

    with colB:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">Strategic Consulting Interpretation</div>
            <div class="insight-body">
                The platform is currently assessed as <b>{strategic_position}</b>, with an overall strategic maturity score of
                <b>{strategic_maturity_score:.1f}/100</b>.
                <br><br>
                Strongest capability: <b>{strongest_capability["Capability"]}</b>.
                <br><br>
                Highest improvement gap: <b>{weakest_capability["Capability"]}</b>.
                <br><br>
                This transforms the product from a dashboard into a consulting diagnostic tool for digital transformation,
                AI adoption, operating model redesign, and executive roadmap planning.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Consulting Maturity Detail")

    st.dataframe(
        consulting_maturity_df,
        use_container_width=True,
        height=320
    )

    # -----------------------------
    # STRATEGIC ROADMAP GENERATOR
    # -----------------------------

    st.markdown("### Strategic Roadmap Generator")

    focus_area = st.selectbox(
        "Select Primary Transformation Focus",
        [
            "Balanced Transformation",
            "AI-Driven Analytics",
            "Supply Chain Optimization",
            "Digital Operating Model",
            "Franchise & Multi-Location Operations",
            "Data Governance"
        ]
    )

    roadmap_items = []

    def add_roadmap_item(horizon, initiative, owner, impact, priority):
        roadmap_items.append({
            "Horizon": horizon,
            "Initiative": initiative,
            "Recommended_Owner": owner,
            "Expected_Impact": impact,
            "Priority": priority
        })

    # Quick wins
    add_roadmap_item(
        "Quick Wins / 0-30 Days",
        "Standardize executive KPI definitions across expansion, franchise, product, labor, CRM, and supply chain dashboards.",
        "Management Analyst / Operations Lead",
        "Improves decision consistency and leadership reporting credibility.",
        "High"
    )
    add_roadmap_item(
        "Quick Wins / 0-30 Days",
        "Create a weekly executive operating review using alerts, workflow queue, maturity scores, and drill-down findings.",
        "Executive Sponsor / Management Analyst",
        "Turns analytics into recurring management action.",
        "High"
    )

    if weakest_capability["Capability"] == "AI Maturity" or focus_area == "AI-Driven Analytics":
        add_roadmap_item(
            "Quick Wins / 0-30 Days",
            "Validate AI forecasting outputs against actual demand and track MAPE, RMSE, and confidence by product/location.",
            "Analytics Owner",
            "Improves trust in AI-powered recommendations.",
            "High"
        )

    if weakest_capability["Capability"] == "Supply Chain Maturity" or focus_area == "Supply Chain Optimization":
        add_roadmap_item(
            "Quick Wins / 0-30 Days",
            "Review high-risk inventory items and align reorder thresholds with lead time, safety stock, and service level targets.",
            "Supply Chain / Purchasing Lead",
            "Reduces stockout exposure and replenishment inconsistency.",
            "High"
        )

    if weakest_capability["Capability"] == "Data Governance Maturity" or focus_area == "Data Governance":
        add_roadmap_item(
            "Quick Wins / 0-30 Days",
            "Assign data owners for customers, products, inventory, locations, employees, franchise metrics, and suppliers.",
            "Data Governance Lead",
            "Creates accountability for reporting quality and master data reliability.",
            "High"
        )

    # Medium term
    add_roadmap_item(
        "Medium-Term / 31-90 Days",
        "Deploy a formal maturity assessment cadence across AI, digital, supply chain, operations, and governance capabilities.",
        "Transformation Lead",
        "Creates measurable transformation governance and progress tracking.",
        "High"
    )
    add_roadmap_item(
        "Medium-Term / 31-90 Days",
        "Build location-level benchmarking routines for salons, academy programs, franchise locations, labor utilization, CRM retention, and product performance.",
        "Operations + Analytics Team",
        "Improves multi-location operating discipline and performance transparency.",
        "High"
    )
    add_roadmap_item(
        "Medium-Term / 31-90 Days",
        "Convert alerts and workflow simulations into approval-based operational playbooks for replenishment, supplier follow-up, and executive escalation.",
        "Operations Lead / Procurement Lead",
        "Moves from analytics to controlled execution workflows.",
        "Medium"
    )

    # Long term
    add_roadmap_item(
        "Long-Term / 90-180 Days",
        "Integrate live operational systems, CRM, inventory, POS, academy, and franchise data into a governed transformation data pipeline.",
        "Technology / Data Owner",
        "Creates scalable enterprise intelligence and reduces manual reporting dependence.",
        "High"
    )
    add_roadmap_item(
        "Long-Term / 90-180 Days",
        "Establish an executive transformation office with governance routines, adoption KPIs, operating model ownership, and continuous improvement cadence.",
        "Executive Sponsor",
        "Institutionalizes the transformation beyond a dashboard into a management system.",
        "High"
    )
    add_roadmap_item(
        "Long-Term / 90-180 Days",
        "Develop predictive consulting playbooks that recommend initiatives based on maturity gaps, risk signals, forecast performance, and operational constraints.",
        "Strategy / Analytics Lead",
        "Positions the platform as a strategic consulting and transformation engine.",
        "Medium"
    )

    roadmap_df = pd.DataFrame(roadmap_items)

    if focus_area != "Balanced Transformation":
        roadmap_df["Focus_Relevance"] = roadmap_df["Initiative"].apply(
            lambda x: "Primary" if any(word.lower() in x.lower() for word in focus_area.replace("&", " ").split()) else "Supporting"
        )
    else:
        roadmap_df["Focus_Relevance"] = "Balanced"

    roadmap_priority_order = {"High": 1, "Medium": 2, "Low": 3}
    roadmap_df["Priority_Order"] = roadmap_df["Priority"].map(roadmap_priority_order).fillna(9)
    roadmap_df = roadmap_df.sort_values(["Horizon", "Priority_Order"]).drop(columns=["Priority_Order"])

    fig_roadmap = px.timeline(
        roadmap_df,
        x_start=roadmap_df["Horizon"].map({
            "Quick Wins / 0-30 Days": "2026-06-17",
            "Medium-Term / 31-90 Days": "2026-07-17",
            "Long-Term / 90-180 Days": "2026-09-17"
        }),
        x_end=roadmap_df["Horizon"].map({
            "Quick Wins / 0-30 Days": "2026-07-17",
            "Medium-Term / 31-90 Days": "2026-09-17",
            "Long-Term / 90-180 Days": "2026-12-17"
        }),
        y="Initiative",
        color="Priority",
        hover_data=["Recommended_Owner", "Expected_Impact", "Focus_Relevance"],
        color_discrete_map={
            "High": "#B22222",
            "Medium": GOLD,
            "Low": "#8A8A8A"
        }
    )

    fig_roadmap.update_yaxes(autorange="reversed")

    st.plotly_chart(
        chart_layout(fig_roadmap, 620),
        use_container_width=True
    )

    st.dataframe(
        roadmap_df,
        use_container_width=True,
        height=460
    )

    # -----------------------------
    # EXECUTIVE CONSULTING NARRATIVE
    # -----------------------------

    quick_wins_text = "\n".join(
        [f"- {row['Initiative']}" for _, row in roadmap_df[roadmap_df["Horizon"] == "Quick Wins / 0-30 Days"].head(5).iterrows()]
    )

    medium_term_text = "\n".join(
        [f"- {row['Initiative']}" for _, row in roadmap_df[roadmap_df["Horizon"] == "Medium-Term / 31-90 Days"].head(5).iterrows()]
    )

    long_term_text = "\n".join(
        [f"- {row['Initiative']}" for _, row in roadmap_df[roadmap_df["Horizon"] == "Long-Term / 90-180 Days"].head(5).iterrows()]
    )

    consulting_summary = f"""
Strategic Consulting Summary

Overall maturity score: {strategic_maturity_score:.1f}/100
Strategic position: {strategic_position}
Strongest capability: {strongest_capability['Capability']} ({strongest_capability['Maturity_Score']:.1f}/100)
Highest improvement gap: {weakest_capability['Capability']} ({weakest_capability['Maturity_Score']:.1f}/100)
Primary focus area: {focus_area}

Quick wins / 0-30 days:
{quick_wins_text}

Medium-term / 31-90 days:
{medium_term_text}

Long-term / 90-180 days:
{long_term_text}
""".strip()

    st.markdown("### Auto-Generated Consulting Summary")

    st.text_area(
        "Copy this narrative into an executive update, client memo, or NIW evidence note",
        consulting_summary,
        height=360
    )

    st.download_button(
        label="Download Strategic Maturity Assessment CSV",
        data=consulting_maturity_df.to_csv(index=False),
        file_name="strategic_consulting_maturity_assessment.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download Strategic Transformation Roadmap CSV",
        data=roadmap_df.to_csv(index=False),
        file_name="strategic_transformation_roadmap.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download Consulting Summary TXT",
        data=consulting_summary,
        file_name="strategic_consulting_summary.txt",
        mime="text/plain"
    )

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Executive Strategic Consulting Interpretation</div>
        <div class="insight-body">
            This module reframes the platform as a consulting and transformation engine, not only a dashboard.
            <br><br>
            It evaluates maturity across AI, supply chain, digital operations, operational excellence, and data governance;
            identifies the strongest capability and highest improvement gap; and generates a phased transformation roadmap.
            <br><br>
            This strengthens alignment with strategic consulting, digital transformation, change management,
            operating model design, and executive transformation advisory work.
        </div>
    </div>
    """, unsafe_allow_html=True)


with tab43:
    st.markdown('<div class="section-title">Adoption KPI Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Strengthens change management evidence by tracking measurable adoption, onboarding, training, usage, and stakeholder resistance by department.</div>', unsafe_allow_html=True)

    adoption_df = pd.DataFrame({
        "Department": ["Salon Operations", "Academy", "Franchise Operations", "Marketing", "Finance", "Leadership"],
        "Target_Users": [42, 24, 30, 14, 10, 7],
        "Active_Users": [34, 18, 22, 12, 9, 6],
        "Weekly_Login_Rate_%": [81, 75, 67, 86, 78, 92],
        "Training_Completion_%": [79, 84, 65, 92, 71, 100],
        "Avg_Onboarding_Days": [9, 7, 14, 6, 10, 4],
        "Feature_Usage_%": [72, 69, 61, 83, 70, 88],
        "Resistance_Risk_%": [28, 22, 41, 18, 30, 10],
        "Executive_Sponsor_Score": [80, 78, 66, 89, 75, 95]
    })

    adoption_df["Active_User_%"] = (adoption_df["Active_Users"] / adoption_df["Target_Users"] * 100).round(1)
    adoption_df["Adoption_Health_Score"] = (
        adoption_df["Active_User_%"] * 0.20
        + adoption_df["Weekly_Login_Rate_%"] * 0.20
        + adoption_df["Training_Completion_%"] * 0.20
        + adoption_df["Feature_Usage_%"] * 0.20
        + adoption_df["Executive_Sponsor_Score"] * 0.10
        + (100 - adoption_df["Resistance_Risk_%"]) * 0.10
    ).round(1)
    adoption_df["Adoption_Status"] = adoption_df["Adoption_Health_Score"].apply(lambda x: "Strong Adoption" if x >= 80 else "Needs Reinforcement" if x >= 65 else "At Risk")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Active User Adoption", f"{adoption_df['Active_User_%'].mean():.1f}%")
    a2.metric("Training Completion", f"{adoption_df['Training_Completion_%'].mean():.1f}%")
    a3.metric("Avg Onboarding Time", f"{adoption_df['Avg_Onboarding_Days'].mean():.1f} days")
    a4.metric("Adoption Health", f"{adoption_df['Adoption_Health_Score'].mean():.1f}/100")

    left, right = st.columns(2)
    with left:
        fig_adopt = px.bar(adoption_df.sort_values("Adoption_Health_Score", ascending=False), x="Department", y="Adoption_Health_Score", color="Adoption_Status", text="Adoption_Health_Score", color_discrete_sequence=[GOLD, GOLD_LIGHT, "#7D6838"])
        fig_adopt.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(chart_layout(fig_adopt, 520), use_container_width=True)
    with right:
        fig_onboarding = px.bar(adoption_df.sort_values("Avg_Onboarding_Days", ascending=False), x="Department", y="Avg_Onboarding_Days", color="Adoption_Status", text="Avg_Onboarding_Days", color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838"])
        fig_onboarding.update_traces(texttemplate="%{text:.0f} days", textposition="outside")
        st.plotly_chart(chart_layout(fig_onboarding, 520), use_container_width=True)

    st.markdown("### Adoption KPI Detail")
    st.dataframe(adoption_df, use_container_width=True, height=360)

    interventions_df = pd.DataFrame({
        "Trigger": ["Active user rate below 70%", "Training completion below 75%", "Onboarding above 10 days", "Resistance risk above 35%", "Feature usage below 65%"],
        "Change_Management_Action": ["Schedule department-level adoption review and identify blockers.", "Assign refresher training and publish quick-start guides.", "Simplify workflow, clarify role expectations, and create onboarding checklist.", "Conduct stakeholder listening session and executive sponsor follow-up.", "Prioritize highest-value features and demonstrate use cases in weekly review."],
        "Evidence_Created": ["Adoption log", "Training completion record", "Onboarding tracker", "Stakeholder feedback log", "Feature usage report"]
    })
    st.markdown("### Change Management Intervention Rules")
    st.dataframe(interventions_df, use_container_width=True, height=260)

with tab44:
    st.markdown('<div class="section-title">Staff Data Literacy Program</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Dedicated module for internal staff data literacy, separate from the external Academy training business.</div>', unsafe_allow_html=True)

    literacy_df = pd.DataFrame({
        "Staff_Group": ["Salon Managers", "Front Desk", "Academy Coordinators", "Franchise Support", "Marketing", "Leadership"],
        "Baseline_Data_Literacy_%": [62, 54, 68, 57, 72, 78],
        "KPI_Understanding_%": [66, 58, 70, 60, 74, 82],
        "Dashboard_Confidence_%": [60, 52, 65, 55, 76, 84],
        "Completed_Modules": [3, 2, 4, 2, 4, 5],
        "Target_Modules": [5, 5, 5, 5, 5, 5]
    })
    literacy_df["Program_Completion_%"] = (literacy_df["Completed_Modules"] / literacy_df["Target_Modules"] * 100).round(1)
    literacy_df["Data_Literacy_Maturity"] = (
        literacy_df["Baseline_Data_Literacy_%"] * 0.25
        + literacy_df["KPI_Understanding_%"] * 0.25
        + literacy_df["Dashboard_Confidence_%"] * 0.25
        + literacy_df["Program_Completion_%"] * 0.25
    ).round(1)
    literacy_df["Readiness_Level"] = literacy_df["Data_Literacy_Maturity"].apply(lambda x: "Advanced" if x >= 80 else "Developing" if x >= 65 else "Foundation Needed")

    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Data Literacy Maturity", f"{literacy_df['Data_Literacy_Maturity'].mean():.1f}/100")
    l2.metric("KPI Understanding", f"{literacy_df['KPI_Understanding_%'].mean():.1f}%")
    l3.metric("Dashboard Confidence", f"{literacy_df['Dashboard_Confidence_%'].mean():.1f}%")
    l4.metric("Program Completion", f"{literacy_df['Program_Completion_%'].mean():.1f}%")

    fig_lit = px.bar(literacy_df.sort_values("Data_Literacy_Maturity", ascending=False), x="Staff_Group", y="Data_Literacy_Maturity", color="Readiness_Level", text="Data_Literacy_Maturity", color_discrete_sequence=[GOLD, GOLD_LIGHT, "#7D6838"])
    fig_lit.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    st.plotly_chart(chart_layout(fig_lit, 540), use_container_width=True)

    st.markdown("### Internal Data Literacy Curriculum")
    curriculum_df = pd.DataFrame({
        "Module": ["KPI Basics", "Dashboard Navigation", "Data Quality & Source Trust", "Inventory & Demand Signals", "Executive Storytelling with Data"],
        "Learning_Objective": ["Understand revenue, margin, ROI, retention, and utilization KPIs.", "Use filters, drill-downs, alerts, and downloadable reports.", "Recognize incomplete, stale, duplicate, or unreliable data.", "Interpret stockout risk, reorder signals, forecast confidence, and supplier performance.", "Translate data findings into decisions, actions, and executive updates."],
        "Assessment_Method": ["Short quiz", "Guided use case", "Data issue identification", "Scenario exercise", "One-page insight memo"]
    })
    st.dataframe(curriculum_df, use_container_width=True, height=280)
    st.markdown("### Staff Readiness Detail")
    st.dataframe(literacy_df, use_container_width=True, height=320)

with tab45:
    st.markdown('<div class="section-title">Supply Chain Traceability & Blockchain Readiness</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Conceptual blockchain-readiness layer for supply chain transparency, focused on traceability, vendor verification, lot-level visibility, and auditability before any blockchain deployment.</div>', unsafe_allow_html=True)

    traceability_df = pd.DataFrame({
        "Supply_Chain_Node": ["Supplier Master", "Product SKU Master", "Purchase Orders", "Inbound Shipments", "Inventory Receipts", "Store Transfers", "Customer Returns"],
        "Traceability_Coverage_%": [76, 82, 71, 64, 68, 58, 52],
        "Digital_Record_Completeness_%": [80, 78, 73, 66, 70, 61, 55],
        "Vendor_Verification_%": [74, 70, 68, 62, 65, 56, 50],
        "Audit_Trail_Strength_%": [72, 76, 69, 60, 64, 59, 54],
        "Blockchain_Readiness_%": [62, 66, 58, 51, 55, 48, 44]
    })
    traceability_df["Transparency_Score"] = (
        traceability_df["Traceability_Coverage_%"] * 0.25
        + traceability_df["Digital_Record_Completeness_%"] * 0.25
        + traceability_df["Vendor_Verification_%"] * 0.20
        + traceability_df["Audit_Trail_Strength_%"] * 0.20
        + traceability_df["Blockchain_Readiness_%"] * 0.10
    ).round(1)
    traceability_df["Traceability_Status"] = traceability_df["Transparency_Score"].apply(lambda x: "Ready to Pilot" if x >= 75 else "Prepare Data Layer" if x >= 60 else "Foundational Gap")

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Transparency Score", f"{traceability_df['Transparency_Score'].mean():.1f}/100")
    t2.metric("Traceability Coverage", f"{traceability_df['Traceability_Coverage_%'].mean():.1f}%")
    t3.metric("Audit Trail Strength", f"{traceability_df['Audit_Trail_Strength_%'].mean():.1f}%")
    t4.metric("Blockchain Readiness", f"{traceability_df['Blockchain_Readiness_%'].mean():.1f}%")

    left, right = st.columns(2)
    with left:
        fig_trace = px.bar(traceability_df.sort_values("Transparency_Score", ascending=False), x="Supply_Chain_Node", y="Transparency_Score", color="Traceability_Status", text="Transparency_Score", color_discrete_sequence=[GOLD, GOLD_LIGHT, "#7D6838"])
        fig_trace.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(chart_layout(fig_trace, 540), use_container_width=True)
    with right:
        fig_ready = px.bar(traceability_df.sort_values("Blockchain_Readiness_%", ascending=False), x="Supply_Chain_Node", y="Blockchain_Readiness_%", color="Traceability_Status", text="Blockchain_Readiness_%", color_discrete_sequence=[GOLD_LIGHT, GOLD, "#7D6838"])
        fig_ready.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(chart_layout(fig_ready, 540), use_container_width=True)

    st.markdown("### Traceability Readiness Detail")
    st.dataframe(traceability_df, use_container_width=True, height=360)

    pilot_df = pd.DataFrame({
        "Pilot_Phase": ["Phase 1: Data Foundation", "Phase 2: Traceability Pilot", "Phase 3: Blockchain Evaluation"],
        "Objective": ["Standardize supplier, SKU, PO, receipt, and transfer records.", "Track selected product categories from supplier to location using immutable audit logs.", "Evaluate whether blockchain adds business value beyond standard database audit controls."],
        "Success_Metric": ["90% complete digital records", "End-to-end traceability for pilot SKUs", "Clear ROI, compliance, or transparency benefit before deployment"]
    })
    st.markdown("### Practical Blockchain Implementation Roadmap")
    st.dataframe(pilot_df, use_container_width=True, height=220)

    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">Executive Interpretation</div>
        <div class="insight-body">
            This module intentionally treats blockchain as an advanced readiness layer, not an immediate technology purchase.
            The first management priority is to strengthen supplier master data, SKU-level records, purchase order consistency,
            shipment documentation, inventory receipt controls, and audit trails. Once those foundations are reliable,
            leadership can evaluate a limited blockchain or immutable-ledger pilot for high-value or high-risk product categories.
        </div>
    </div>
    """, unsafe_allow_html=True)
