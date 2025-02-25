import pycountry
import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(
    page_title="Startups Analytics & Insights Dashboard",
    page_icon="dashboard/images/home.png",
    layout="wide"
)

REPORT_PATH = "CxC_Datathon_RunQL_Report.pdf"  # Change to your actual path   

with st.expander("About This Dashboard"):
    st.write(
        """
        Welcome to the CxC Datathon Investment Insights Dashboard! This platform provides a 
        comprehensive analysis of investment trends in the Canadian tech ecosystem (2019-2024).

        Key Features
        Sectoral & Regional Insights
        - Analyze the top investment sectors and compare trends across major Canadian cities.  
        - View total vs. average investments for various sectors and regions.  

        Investor Demographics & Behavior
        - Study investment trends by geography (Canada, US, international investors).  
        - Compare average deal sizes per funding stage based on investor geography.  
        - Identify leading investors and their influence on funding success.  

        Funding Stages Analysis
        - Examine funding activity across different investment stages (Seed, Series A, B, etc.).  
        - Track deal flow trends over time and understand the most active sectors.  

        Empowering Investors, Startups & Analysts 
        This dashboard helps investors, startups, and researchers make data-driven decisions 
        with interactive visualizations and insights into the Canadian investment landscape.

        Need insights beyond the dashboard? Chat with BrewBot for real-time answers!

        Download my report for detailed insights and forecasting!
        
        """
    )
    with open(REPORT_PATH, "rb") as file:
        pdf_bytes = file.read()

    # Download Button for the Report
    st.download_button(
        label="Download Full Report",
        data=pdf_bytes,
        file_name="CxC_Datathon_Report.pdf",
        mime="application/pdf"
    )
####### CSS #######
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



####### DATA #######

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



####### SIDEBAR #######

st.sidebar.title("Startups Analytics & Insights Dashboard")
st.sidebar.write("---")

min_date, max_date = deals_df["date"].min().date(), deals_df["date"].max().date()
date_range = st.sidebar.slider("Select Date Range:", min_date, max_date, (min_date, max_date), format="YYYY-MM-DD")
filtered_deals = deals_df[(deals_df["date"] >= pd.to_datetime(date_range[0])) & (deals_df["date"] <= pd.to_datetime(date_range[1]))]

st.sidebar.write("---")

st.sidebar.image("dashboard/images/bb.png", use_container_width=True)  # 🔥 Replace with your logo path


####### METRICS #######
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



col3, col4 = st.columns([2, 1])

####### Investment by Funding Stage #######
with col3:
    avg_amounts = filtered_deals.groupby(["year", "roundType"])["amount"].sum().reset_index()
    area_chart = px.area(
        avg_amounts,
        x="year",
        y="amount",
        title="Investment Distribution by Funding Stage Over Time",
        color="roundType",
        labels={"amount": "Total Investment ($)", "year": "Year", "roundType": "Funding Stage"},
        color_discrete_sequence=px.colors.sequential.Magma
    )
    area_chart.update_layout(font=dict(family="Courier New, monospace", size=14, color="white"))
    st.subheader("Investment Distribution by Funding Stage Over Time")
    st.plotly_chart(area_chart, use_container_width=True)

####### Avg Deal Size Per Year ($M) #######
with col4:
    fig1 = px.line(deals_per_year, x="year", y="deal_count", markers=True, color_discrete_sequence=["#D53B70"])
    fig1.update_layout(xaxis_title="Year", yaxis_title="Number of Deals", template="plotly_dark", width=450, height=250)
    st.subheader("Number of Deals Per Year")
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = px.line(avg_deal_size_per_year, x="year", y="avg_deal_size", markers=True, color_discrete_sequence=["#FAF09D"])
    fig2.update_layout(xaxis_title="Year", yaxis_title="Avg Deal Size ($M)", template="plotly_dark", width=450, height=250)
    st.subheader("Avg Deal Size Per Year ($M)")
    st.plotly_chart(fig2, use_container_width=True)




####### Investment Firm Distribution Map #######
def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        return None
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




####### "Investment Firms Per Funding Stage #######
st.header("Customize Top Countries")
top_n_countries = st.slider("Select Top Countries", 5, 50, 10)  # Adjustable slider

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


####### Average Deal Size by Stage & Geography #######
if "dealId" not in deals_df.columns:
    if "id" in deals_df.columns:
        deals_df.rename(columns={"id": "dealId"}, inplace=True)
    else:
        st.error("Error: 'dealId' column not found in deals_df!")
if "dealId" not in dealInvestor_df.columns:
    if "id" in dealInvestor_df.columns:
        dealInvestor_df.rename(columns={"id": "dealId"}, inplace=True)
    else:
        st.error("Error: 'dealId' column not found in dealInvestor_df!")
deals_df = deals_df.drop_duplicates(subset="dealId")
dealInvestor_df = dealInvestor_df.drop_duplicates(subset="dealId")
merged_df = dealInvestor_df[["dealId", "investorCountry"]].merge(deals_df, on="dealId", how="left")
avg_deal_size = merged_df.groupby(["roundType", "investorCountry"], as_index=False)["amount"].mean()
top_deal_countries = avg_deal_size.groupby("investorCountry")["amount"].sum().nlargest(top_n_countries).index
filtered_avg_deal_size = avg_deal_size[avg_deal_size["investorCountry"].isin(top_deal_countries)]
fig = px.bar(
    filtered_avg_deal_size,
    x="roundType",
    y="amount",
    color="investorCountry",
    text_auto=".2s",
    labels={"roundType": "Funding Stage", "amount": "Avg Deal Size (USD)"},
    color_discrete_sequence=px.colors.sequential.Magma
)
fig.update_layout(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font=dict(color="white", family="Courier New, monospace"),
    legend=dict(title="Investor Country", font=dict(color="white")),
    xaxis=dict(title="Funding Stage", tickangle=45),
    yaxis=dict(title="Avg Deal Size (USD)", tickprefix="$"),
    margin=dict(l=0, r=0, t=50, b=0)
)
st.subheader("Average Deal Size by Stage & Geography")
st.plotly_chart(fig, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    ####### Most Active ___ Investment Firms Analysis in Year ___ #######
    st.header("Investment Firm Activity")
    top_n = st.slider("Select Top Firms", 5, 20, 10)
    chart_type = st.radio("Choose Chart Type", [ "Pie Chart", "Bar Chart"])
    firm_activity = dealInvestor_df.groupby(["investorName", "year"])["dealId"].nunique().reset_index()
    firm_activity.columns = ["Investor Name", "Year", "Number of Deals"]
    selected_year = st.selectbox("Select Year", sorted(dealInvestor_df["year"].unique(), reverse=True))
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
with col2:
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
        # title=f"Top 5 Sectors for {selected_stage}",
        color="primaryTag",
        color_discrete_sequence=px.colors.sequential.Magma
    )
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.subheader(f"Top 5 Sectors for {selected_stage}")
    st.plotly_chart(fig, use_container_width=True)


####### Evolution of Average Deal Size by Funding Stage #######
st.subheader("Evolution of Average Deal Size by Funding Stage")
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
st.plotly_chart(fig1, use_container_width=True)

####### Primary Sectors Across Funding Stages #######
col1, col2= st.columns([2, 1])  # Adjust column widths
with col1:  # Pie chart takes up more space
    st.subheader("Primary Sectors Across Funding Stages")
    sector_counts = filtered_deals.groupby("roundType")["ecosystemName"].nunique().reset_index()
    sector_counts = sector_counts.sort_values(by="ecosystemName", ascending=True)
    fig = px.bar(sector_counts, x="ecosystemName", y="roundType", orientation="h", 
                # title="Primary Sectors Across Funding Stages",
                labels={"ecosystemName": "Number of Unique Sectors", "roundType": "Funding Stage"},
                color="roundType", color_discrete_sequence=px.colors.sequential.Magma)
    st.plotly_chart(fig, use_container_width=True)
with col2:  # Keep the funding stages explanation separate
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












num_categories = st.slider("Select Number of Top Sectors:", min_value=1, max_value=50, value=10, step=1, key="num_sectors")
num_regions = st.slider("Select Number of Top Regions:", min_value=1, max_value=20, value=5, step=1, key="num_regions")

heatmap_metric = st.radio("Choose Heatmap Metric:", ["Number of Deals", "Total Investment"], key="heatmap_metric")

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

####### Sector vs. Region Investment Heatmap #######
filtered_sector_region = filtered_deals[
    (filtered_deals["primaryTag"].isin(top_sectors)) & 
    (filtered_deals["headquarters"].isin(top_regions))
]
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
st.subheader(f"{heatmap_metric} Distribution: Sectors vs. Regions")
st.plotly_chart(fig1, use_container_width=True)



col1, col2 = st.columns(2) 

with col1: 
    ####### Sector Distribution Across Companies #######
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
    ####### Distribution of Sectors by Number of Deals #######
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

investment_type = st.radio("Select Investment Type:", ["Total Investment", "Average Investment"], key="investment_type")

####### Investment by Sector #######
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

####### Total Investment of Top ____ Regions #######
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

