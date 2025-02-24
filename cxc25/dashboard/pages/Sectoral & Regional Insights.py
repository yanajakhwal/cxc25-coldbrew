import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(
    page_title="Sectoral & Regional Insights Dashboard",
    page_icon="dashboard/images/si.png",
    layout="wide"
)

# Custom Dark Theme CSS
st.markdown("""
    <style>
    header { visibility: hidden; }
    div[data-testid="stToolbar"] { display: none !important; }
    html, body, .stApp { 
        font-family: "Courier New", monospace !important; 
        color: white !important; 
    }
    
    .stSidebar, .stMetric, .stRadio, .stTextInput, .stButton, .stMarkdown { 
        font-family: "Courier New", monospace !important; 
        font-size: 16px; 
        color: white; 
    }

    div[data-testid="stMetric"] {
        font-size: 22px !important;
        font-weight: bold;
        text-align: center;
        background-color: #1E1E2F !important; 
        border-radius: 10px;
        padding: 20px;
        color: white !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-family: "Courier New", monospace !important;
        color: white !important;
    }    

    h1, h2, h3, h4, h5, h6 { 
        font-family: "Courier New", monospace !important; 
    }

    .custom-title { 
        text-align: center; 
        font-family: "Courier New", monospace !important; 
        font-size: 22px !important; 
        font-weight: bold; 
        color: white !important; 
    }
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

# Sidebar Filters
st.sidebar.title("Sectoral & Regional Insights Dashboard")
st.sidebar.write("---")

min_date, max_date = deals_df["date"].min().date(), deals_df["date"].max().date()
date_range = st.sidebar.slider("Select Date Range:", min_date, max_date, (min_date, max_date), format="YYYY-MM-DD", key="date_range")

filtered_deals = deals_df[
    (deals_df["date"] >= pd.to_datetime(date_range[0])) & 
    (deals_df["date"] <= pd.to_datetime(date_range[1]))
]

# ✅ Remove $0 investments from filtered data
filtered_deals = filtered_deals[filtered_deals["amount"] > 0]

num_categories = st.sidebar.slider("Select Number of Top Sectors:", min_value=1, max_value=50, value=10, step=1, key="num_sectors")
num_regions = st.sidebar.slider("Select Number of Top Regions:", min_value=1, max_value=20, value=5, step=1, key="num_regions")

investment_type = st.sidebar.radio("Select Investment Type:", ["Total Investment", "Average Investment"], key="investment_type")
heatmap_metric = st.sidebar.radio("Choose Heatmap Metric:", ["Number of Deals", "Total Investment"], key="heatmap_metric")



# **Dynamically determine top regions**
top_regions = (
    filtered_deals.groupby("headquarters")["amount"]
    .sum()
    .reset_index()
    .sort_values(by="amount", ascending=False)
    .head(num_regions)["headquarters"]
    .tolist()
)

top_sectors = (
    filtered_deals.groupby("primaryTag")["amount"]
    .sum()
    .reset_index()
    .sort_values(by="amount", ascending=False)
    .head(num_categories)["primaryTag"]
    .tolist()
)

# **Filter Data for Selected Sectors & Regions**
filtered_sector_region = filtered_deals[
    (filtered_deals["primaryTag"].isin(top_sectors)) & 
    (filtered_deals["headquarters"].isin(top_regions))
]

# **Determine Heatmap Data Based on Selection**
if heatmap_metric == "Number of Deals":
    heatmap_data = (
        filtered_sector_region.groupby(["primaryTag", "headquarters"])
        .size()
        .reset_index(name="count")
    )
    z_label = "Number of Deals"
    colorbar_title = "Total Deals"
    heatmap_z = "count"
else:
    heatmap_data = (
        filtered_sector_region.groupby(["primaryTag", "headquarters"])["amount"]
        .sum()
        .reset_index()
    )
    z_label = "Total Investment ($)"
    colorbar_title = "Total Investment ($)"
    heatmap_z = "amount"

# **Sector vs. Region Investment Heatmap**
st.subheader(f"{heatmap_metric} Distribution: Sectors vs. Regions")

fig1 = px.density_heatmap(
    heatmap_data,
    x="headquarters",
    y="primaryTag",
    z=heatmap_z,
    color_continuous_scale="magma",
    labels={"headquarters": "Region", "primaryTag": "Sector", heatmap_z: z_label},
)

fig1.update_layout(
    coloraxis_colorbar=dict(
        title=colorbar_title,
        tickformat="$.0s" if heatmap_metric == "Total Investment" else ""
    )
)

st.plotly_chart(fig1, use_container_width=True)

# **Sector Distribution Across Companies (Pie Chart)**
col1, col2 = st.columns(2)  # Adjust column widths

with col1: 
    st.subheader("Sector Distribution Across Companies")
    company_distribution = (
        filtered_deals.groupby("primaryTag").size().reset_index(name="count").sort_values(by="count", ascending=False)
    )
    fig2 = px.pie(
        company_distribution,
        names="primaryTag",
        values="count",
        labels={"primaryTag": "Sector", "count": "Number of Companies"},
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Magma
    )
    fig2.update_traces(textinfo="none", hovertemplate="<b>%{label}</b><br>Number of Companies: %{value}<br>Percentage: %{percent}")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    # **Sector Distribution by Deals (Treemap/Bar Chart)**
    st.subheader("Distribution of Sectors by Number of Deals")
    sector_dist = (
        filtered_deals.groupby("primaryTag").size().reset_index(name="count").sort_values(by="count", ascending=False)
    )
    view_type = st.radio("Choose a sector visualization:", ["Treemap", "Bar Chart"], key="view_type")

    if view_type == "Treemap":
        fig3 = px.treemap(sector_dist, path=["primaryTag"], values="count", labels={"primaryTag": "Sector", "count": "Number of Deals"}, color="count", color_continuous_scale="magma")
    else:
        fig3 = px.bar(sector_dist, x="count", y="primaryTag", orientation="h", labels={"primaryTag": "Sector", "count": "Number of Deals"}, color="count", color_continuous_scale="magma")

    st.plotly_chart(fig3, use_container_width=True)

# **Investment by Sector**
st.subheader(f"{investment_type} of Top {num_categories} Sectors")
fig4 = px.bar(
    filtered_deals.groupby("primaryTag")[["amount"]].sum().reset_index().nlargest(num_categories, "amount"),
    x="primaryTag",
    y="amount",
    text_auto=True,
    labels={"primaryTag": "Investment Category", "amount": "Total Investment ($)"},
    color="amount",
    color_continuous_scale="magma"
)
fig4.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig4, use_container_width=True)

# **Stacked Bar Chart for Sector Investment Breakdown by Region**
st.subheader(f"{investment_type} of Top {num_regions} Regions")
fig5 = px.bar(
    heatmap_data,
    x="headquarters",
    y=heatmap_z,
    color="primaryTag",
    labels={"headquarters": "Region", heatmap_z: z_label, "primaryTag": "Sector"},
    barmode="stack",
    color_discrete_sequence=px.colors.sequential.Magma
)
st.plotly_chart(fig5, use_container_width=True)