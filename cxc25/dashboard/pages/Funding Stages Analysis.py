import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(
    page_title="Funding Stages Analysis Dashboard",
    page_icon="dashboard/images/fs.png",
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
            
    </style>
""", unsafe_allow_html=True)

funding_data = {
    "Funding Stage": [
        "Equity Crowdfunding", "Grant", "Pre-Seed", "Seed", "Series A", "Series B",
        "Series C", "Series D", "Series D+", "Series E - G"
    ],
    "Typical Funding Range": [
        "$50K - $5M", "$10K - $1M", "$100K - $1M", "$500K - $5M", "$2M - $15M",
        "$10M - $50M", "$30M - $100M", "$50M - $200M", "$100M - $500M", "$200M+"
    ],
    "Description": [
        "A startup raises small investments from a large number of people, usually online.",
        "Non-dilutive funding from governments or institutions to support early-stage startups.",
        "Initial funding to develop an idea, often from personal savings, friends & family.",
        "First formal funding to build a product, conduct market research, and start operations.",
        "Scaling up with a proven business model, focusing on customer acquisition and revenue.",
        "Expanding market reach, increasing team size, and improving product offerings.",
        "Accelerating growth through acquisitions, global expansion, and new product lines.",
        "Preparing for an IPO or major acquisition; often used for further market dominance.",
        "Late-stage funding for highly successful companies scaling aggressively.",
        "Rare funding rounds for mature companies needing capital before going public."
    ]
}

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

st.sidebar.title("Funding Stages Analysis Dashboard")
st.sidebar.write("---")

min_date, max_date = deals_df["date"].min().date(), deals_df["date"].max().date()
date_range = st.sidebar.slider("Select Date Range:", min_date, max_date, (min_date, max_date), format="YYYY-MM-DD")
filtered_deals = deals_df[(deals_df["date"] >= pd.to_datetime(date_range[0])) & (deals_df["date"] <= pd.to_datetime(date_range[1]))]


col1, col2 = st.columns([2, 1])
with col1:
    ####### Evolution of Average Deal Size by Funding Stage #######
    daily_avg_deal_size = filtered_deals.groupby(["date", "roundType"])["amount"].mean().reset_index()
    daily_avg_deal_size["amount"] = daily_avg_deal_size["amount"] / 1e6
    chart_type = st.radio("Select Chart Type:", ["Line", "Points", "Both"], horizontal=True)
    if chart_type == "Line":
        fig1 = px.line(daily_avg_deal_size, x="date", y="amount", color="roundType", line_shape="linear",
                    color_discrete_sequence=px.colors.sequential.Magma)
    elif chart_type == "Points":
        fig1 = px.scatter(daily_avg_deal_size, x="date", y="amount", color="roundType",
                        color_discrete_sequence=px.colors.sequential.Magma)
    else:
        fig1 = px.line(daily_avg_deal_size, x="date", y="amount", color="roundType", markers=True, line_shape="linear",
                    color_discrete_sequence=px.colors.sequential.Magma)
    fig1.update_layout(font=dict(family="Courier New, monospace", size=14, color="white"), xaxis=dict(title="Date", tickformat="%Y-%m-%d"), legend_title_text="Funding Stage")
    st.subheader("Evolution of Average Deal Size by Funding Stage")
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    ####### Top 5 Sectors for Equity Crowdfunding #######
    sector_stage_investment = deals_df.groupby(["roundType", "primaryTag"])["amount"].sum().reset_index()
    funding_stages = sector_stage_investment["roundType"].unique()
    selected_stage = st.selectbox("Select a Funding Stage", funding_stages)
    filtered_data = sector_stage_investment[sector_stage_investment["roundType"] == selected_stage]
    top_5_sectors = filtered_data.nlargest(5, "amount")
    fig = px.bar(
        top_5_sectors,
        x="primaryTag",
        y="amount",
        labels={"primaryTag": "Sector", "amount": "Total Investment ($)"},
        color="primaryTag",
        color_discrete_sequence=px.colors.sequential.Magma
    )
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.subheader(f"Top 5 Sectors for {selected_stage}")
    st.plotly_chart(fig, use_container_width=True)



###### What Do Funding Stages Mean? ########

col1, col2= st.columns([2, 1])  # Adjust column widths
with col1:  #
    st.subheader("Primary Sectors Across Funding Stages")
    sector_counts = filtered_deals.groupby("roundType")["ecosystemName"].nunique().reset_index()
    sector_counts = sector_counts.sort_values(by="ecosystemName", ascending=True)
    fig = px.bar(sector_counts, x="ecosystemName", y="roundType", orientation="h", 
                # title="Primary Sectors Across Funding Stages",
                labels={"ecosystemName": "Number of Unique Sectors", "roundType": "Funding Stage"},
                color="roundType", color_discrete_sequence=px.colors.sequential.Magma)
    st.plotly_chart(fig, use_container_width=True)
with col2: 
    funding_df = pd.DataFrame(funding_data)
    with st.expander("What Do Funding Stages Mean?"):
        st.write("Each funding stage represents a company's growth and investment needs.")
        st.dataframe(funding_df, hide_index=True)


####### Ecosystem of Startup's Distribution Across Funding Stage #######
view_type = st.radio("Choose a sector visualization:", ["Treemap", "Bar Graph"])

if view_type == "Treemap":
    sector_distribution = filtered_deals.groupby(["roundType", "ecosystemName"]).size().reset_index(name="count")
    fig = px.treemap(sector_distribution, path=["roundType", "ecosystemName"], values="count",
                    # title="Primary Ecosystem Distribution Across Funding Stages",
                    labels={"roundType": "Funding Stage", "count": "Number of Deals", "ecosystemName": "Primary Ecosystem"},
                    color="count", color_continuous_scale="magma")
else:
    sector_distribution = filtered_deals.groupby(["roundType", "ecosystemName"]).size().reset_index(name="count")
    fig = px.bar(sector_distribution, x="roundType", y="count", color="ecosystemName", 
                # title="Primary Ecosystem Distribution Across Funding Stages", labels={"roundType": "Funding Stage", "count": "Number of Deals", "ecosystemName": "Primary Ecosystem"},
                barmode="stack", color_discrete_sequence=px.colors.sequential.Magma)
st.subheader("Ecosystem of Startups' Distribution Across Funding Stage")
st.plotly_chart(fig, use_container_width=True)
    







