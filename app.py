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

if not product_file.exists():
    st.error(f"Product file not found: {product_file.resolve()}")
    st.stop()

sales_df = pd.read_excel(product_file, sheet_name="Sales_Transactions")
products_df = pd.read_excel(product_file, sheet_name="Products")
inventory_df = pd.read_excel(product_file, sheet_name="Inventory")
stores_df = pd.read_excel(product_file, sheet_name="Stores")

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18, tab19, tab20, tab21, tab22, tab23, tab24, tab25, tab26, tab27, tab28 = st.tabs([
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
    "Multi-Location Benchmarking"
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
        '<div class="section-note">AI-driven product analytics, inventory visibility, and retail performance intelligence.</div>',
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
            "### Revenue by Brand"
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
            <b>{top_brand}</b> currently represents the strongest revenue-driving brand across the analyzed portfolio.
            <br><br>
            The top-performing product is <b>{top_product}</b>, based on total sales revenue.
            <br><br>
            Inventory analysis identified <b>{low_stock_count}</b> products requiring replenishment attention.
            <br><br>
            This intelligence layer supports retail optimization, demand forecasting, inventory planning,
            and AI-assisted operational decision-making.
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
