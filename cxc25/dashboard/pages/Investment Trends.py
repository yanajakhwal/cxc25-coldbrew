import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(
    page_title="Investment Trends Dashboard",
    page_icon="dashboard/images/itot.png",
    layout="wide"
)

# Custom Dark Theme CSS
st.markdown("""
    <style>
    header { visibility: hidden; }
    div[data-testid="stToolbar"] { display: none !important; }
    html, body, .stApp { font-family: "Courier New", monospace !important; color: white !important; }
    .stSidebar, .stMetric, .stRadio, .stTextInput, .stButton, .stMarkdown { font-family: "Courier New", monospace !important; font-size: 16px; color: white; }
    div[data-testid="stMetric"] {
        font-family: "Courier New", monospace !important; /* Change to desired font */
        font-size: 22px !important;
        font-weight: bold;
        text-align: center;
        background-color: #1E1E2F !important; /* Change background color */
        border-radius: 10px;
        padding: 20px;
        color: white !important;
    }

    /* Adjust font for the metric labels (small text at the top) */
    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-family: "Courier New", monospace !important;
        color: white !important;
    }    h1, h2, h3, h4, h5, h6 { font-family: "Courier New", monospace !important; }
    .custom-title { text-align: center; font-family: "Courier New", monospace !important; font-size: 22px !important; font-weight: bold; color: white !important; }
    .stRadio div[role="radiogroup"] { display: flex; justify-content: flex-end; padding-right: 20px; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("data/deals_updated.csv")
    df = df.drop(columns=["ecosystemSecondary"], errors="ignore")  
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["year"] = df["date"].dt.year
    df = df[df["year"].between(2019, 2024)]
    return df
deals_df = load_data()

@st.cache_data
def load_data():
    df = pd.read_csv("data/dealInvestor_updated.csv")
    df = df.dropna(subset=["date"])
    df = df[df["year"].between(2019, 2024)]
    return df
dealInvestor_df = load_data()

@st.cache_data
def load_data():
    df = pd.read_csv("data/companies_updated.csv")
    return df
companies_df = load_data()

@st.cache_data
def load_data():
    df = pd.read_csv("data/investors_updated.csv")
    return df
investors_df = load_data()


# Sidebar Navigation
st.sidebar.title("Investment Trends Dashboard")
st.sidebar.write("---")

# Sidebar Filters
min_date, max_date = deals_df["date"].min().date(), deals_df["date"].max().date()
date_range = st.sidebar.slider("Select Date Range:", min_date, max_date, (min_date, max_date), format="YYYY-MM-DD")
filtered_deals = deals_df[(deals_df["date"] >= pd.to_datetime(date_range[0])) & (deals_df["date"] <= pd.to_datetime(date_range[1]))]



# KPI CARDS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Investment ($M)", f"{filtered_deals['amount'].sum() / 1e6:.2f}M")
col2.metric("Total Deals", f"{filtered_deals.shape[0]}")
col3.metric("Largest Deal ($M)", f"{filtered_deals['amount'].max() / 1e6:.2f}M")
col4.metric("Smallest Deal ($K)", f"{filtered_deals['amount'].min() / 1e3:.2f}K")

####### Investment Over Time #######
option = st.radio("Choose Investment View:", ["Total Investment Per Quarter", "Average Investment Amounts Over Time"])
filtered_deals["yearQuarter"] = filtered_deals["date"].dt.to_period("Q").astype(str).apply(lambda x: "'" + f"{x[2:4]} Q{x[-1]}")
if option == "Total Investment Per Quarter":
    investment_by_quarter = filtered_deals.groupby("yearQuarter")["amount"].sum().reset_index()
    st.subheader("Total Investment Per Quarter")
else:
    investment_by_quarter = filtered_deals.groupby("yearQuarter")["amount"].mean().reset_index()
    st.subheader("Average Investment Amounts Over Time")
fig = px.bar(
    investment_by_quarter, x="yearQuarter", y="amount",
    labels={"yearQuarter": "Quarter", "amount": "Investment ($)" if option == "Total Investment Per Quarter" else "Avg Investment ($)"},
    text_auto=True, color="amount", color_continuous_scale="magma"
)
st.plotly_chart(fig, use_container_width=True)
deals_per_year = filtered_deals.groupby("year").size().reset_index(name="deal_count")
avg_deal_size_per_year = filtered_deals.groupby("year")["amount"].mean().reset_index()
avg_deal_size_per_year.columns = ["year", "avg_deal_size"]  # Ensure correct column name
avg_deal_size_per_year["avg_deal_size"] /= 1e6  # Convert to millions

col5, col6 = st.columns(2)
with col5:
    ####### Investment Distribution by Funding Stage Over Time #######
    avg_amounts = filtered_deals.groupby(["year", "roundType"])["amount"].sum().reset_index()
    area_chart = px.area(
        avg_amounts,
        x="year",
        y="amount",
        color="roundType",
        labels={"amount": "Total Investment ($)", "year": "Year", "roundType": "Funding Stage"},
        color_discrete_sequence=px.colors.sequential.Magma
    )
    area_chart.update_layout(font=dict(family="Courier New, monospace", size=14, color="white"))
    st.subheader("Investment Distribution by Funding Stage Over Time")
    st.plotly_chart(area_chart, use_container_width=True)

with col6:
    ####### Number of Deals Per Year #######
    fig1 = px.line(deals_per_year, x="year", y="deal_count", markers=True, color_discrete_sequence=["#D53B70"])
    fig1.update_layout(xaxis_title="Year", yaxis_title="Number of Deals", template="plotly_dark", width=450, height=250)
    st.subheader("Number of Deals Per Year")
    st.plotly_chart(fig1, use_container_width=True)
    ####### Avg Deal Size Per Year ($M) #######
    fig2 = px.line(avg_deal_size_per_year, x="year", y="avg_deal_size", markers=True, color_discrete_sequence=["#FAF09D"])
    fig2.update_layout(xaxis_title="Year", yaxis_title="Avg Deal Size ($M)", template="plotly_dark", width=450, height=250)
    st.subheader("Avg Deal Size Per Year ($M)")
    st.plotly_chart(fig2, use_container_width=True)
