import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# Page Configuration
st.set_page_config(page_title="Investor Demographics & Behavior", page_icon="dashboard/images/ib.png", layout="wide")

# Dark Theme Styling
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
    header { visibility: hidden; }
    div[data-testid="stToolbar"], header { display: none !important; }
    html, body, .stApp { background-color: #0e1117 !important; color: white !important; font-family: "Courier New", monospace !important; }
    .stSidebar { background-color: #262730 !important; }
    .stMetric, .stRadio, .stTextInput, .stButton, .stMarkdown { font-size: 16px; color: white; }
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


deals_df.rename(columns={"id": "dealId"}, inplace=True)  # Standardize column names

# Sidebar Navigation
st.sidebar.title("Investor Demographics & Behavior")
st.sidebar.write("---")

# Convert country names to ISO Alpha-3 codes
def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        return None

# Investment Firm Distribution Map
unique_investors = dealInvestor_df.drop_duplicates(subset=["investorId", "investorCountry"])
investor_counts = unique_investors["investorCountry"].value_counts().reset_index()
investor_counts.columns = ["investorCountry", "num_unique_investors"]
investor_counts["iso_alpha"] = investor_counts["investorCountry"].apply(get_country_code)

col1, col2 = st.columns([3, 1])
with col1:
    fig = px.choropleth(
        investor_counts, locations="iso_alpha", color="num_unique_investors",
        hover_name="investorCountry", color_continuous_scale="Magma",
        scope="world", labels={"num_unique_investors": "Unique Investment Firms"},
        projection="natural earth"
    )
    fig.update_layout(
        font=dict(family="Courier New, monospace", size=14, color="white"),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", geo=dict(bgcolor="#0e1117"),
        margin=dict(l=0, r=0, t=50, b=0), height=500
    )
    st.subheader("Global Investment Firm Distribution")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write(investor_counts)

# Sidebar for Adjustable Top Countries
st.sidebar.header("Customize Top Countries")
top_n_countries = st.sidebar.slider("Select Top Countries", 5, 50, 10)  # Adjustable slider

# Investment Firms Per Funding Stage (Filtered by Top N Countries)
stage_country_counts = dealInvestor_df.groupby(["roundType", "investorCountry"])["investorId"].nunique().reset_index()
top_stage_countries = stage_country_counts.groupby("investorCountry")["investorId"].sum().nlargest(top_n_countries).index
filtered_stage_country_counts = stage_country_counts[stage_country_counts["investorCountry"].isin(top_stage_countries)]

fig = px.bar(
    filtered_stage_country_counts, x="roundType", y="investorId", color="investorCountry",
    text_auto=True, labels={"roundType": "Funding Stage", "investorId": "Number of Investment Firms"},
    color_discrete_sequence=px.colors.sequential.Magma
)
fig.update_layout(
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    font=dict(color="white", family="Courier New, monospace"),
    legend=dict(title="Country", font=dict(color="white")),
    xaxis=dict(title="Funding Stage", tickangle=45),
    yaxis=dict(title="Number of Investment Firms"),
    margin=dict(l=0, r=0, t=50, b=0)
)
st.subheader("Investment Firms Per Funding Stage")
st.plotly_chart(fig, use_container_width=True)

# Average Deal Size by Stage & Geography (Filtered by Top N Countries)
deals_df = deals_df.drop_duplicates(subset="dealId")
dealInvestor_df = dealInvestor_df.drop_duplicates(subset="dealId")
merged_df = dealInvestor_df[["dealId", "investorCountry"]].merge(deals_df, on="dealId", how="left")
avg_deal_size = merged_df.groupby(["roundType", "investorCountry"], as_index=False)["amount"].mean()

top_deal_countries = avg_deal_size.groupby("investorCountry")["amount"].sum().nlargest(top_n_countries).index
filtered_avg_deal_size = avg_deal_size[avg_deal_size["investorCountry"].isin(top_deal_countries)]

fig = px.bar(
    filtered_avg_deal_size, x="roundType", y="amount", color="investorCountry",
    text_auto=".2s", labels={"roundType": "Funding Stage", "amount": "Avg Deal Size (USD)"},
    color_discrete_sequence=px.colors.sequential.Magma
)
fig.update_layout(
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    font=dict(color="white", family="Courier New, monospace"),
    legend=dict(title="Investor Country", font=dict(color="white")),
    xaxis=dict(title="Funding Stage", tickangle=45),
    yaxis=dict(title="Avg Deal Size (USD)", tickprefix="$"),
    margin=dict(l=0, r=0, t=50, b=0)
)
st.subheader("Average Deal Size by Stage & Geography")
st.plotly_chart(fig, use_container_width=True)

# Most Active Investment Firms Analysis
st.sidebar.header("Investment Firm Activity")
top_n = st.sidebar.slider("Select Top Firms", 5, 20, 10)
chart_type = st.sidebar.radio("Choose Chart Type", [ "Pie Chart", "Bar Chart"])

firm_activity = dealInvestor_df.groupby(["investorName", "year"])["dealId"].nunique().reset_index()
firm_activity.columns = ["Investor Name", "Year", "Number of Deals"]
selected_year = st.sidebar.selectbox("Select Year", sorted(dealInvestor_df["year"].unique(), reverse=True))

if chart_type == "Pie Chart":
    firm_activity = firm_activity[firm_activity["Year"] == selected_year]

top_firms = firm_activity.groupby("Investor Name")["Number of Deals"].sum().nlargest(top_n).index
filtered_firm_activity = firm_activity[firm_activity["Investor Name"].isin(top_firms)]

if chart_type == "Bar Chart":
    fig = px.bar(
        filtered_firm_activity, x="Year", y="Number of Deals", color="Investor Name",
        text_auto=True, labels={"Year": "Year", "Number of Deals": "Investment Deals"},
        barmode="stack", color_discrete_sequence=px.colors.sequential.Magma
    )
else:
    fig = px.pie(
        filtered_firm_activity, names="Investor Name", values="Number of Deals",
        # title=f"Most Active {top_n} Firms in {selected_year[:4]}",
        labels={"Investor Name": "Investment Firm", "Number of Deals": "Investment Deals"},
        color_discrete_sequence=px.colors.sequential.Magma
    )

fig.update_layout(
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    font=dict(color="white", family="Courier New, monospace"),
    margin=dict(l=0, r=0, t=50, b=0)
)

st.subheader(f"Most Active {top_n} Firms in {str(selected_year)[:4]}")
st.plotly_chart(fig, use_container_width=True)
