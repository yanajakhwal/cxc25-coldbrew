import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import docx

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API")
genai.configure(api_key=gemini_api_key)

st.set_page_config(
    page_title="BrewBot",
    page_icon="dashboard/images/bb.png",
    layout="wide"
)
st.title("BrewBot: Your AI Investment Assistant")

# Custom Dark Theme CSS
st.markdown("""
    <style>
    header { visibility: hidden; }
    div[data-testid="stToolbar"] { display: none !important; }
    html, body, .stApp { font-family: "Courier New", monospace !important; color: white !important; }
    .stSidebar, .stMetric, .stRadio, .stTextInput, .stButton, .stMarkdown { font-family: "Courier New", monospace !important; font-size: 16px; color: white; }
    .custom-title { text-align: center; font-size: 22px !important; font-weight: bold; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("dashboard/images/bb.png", use_container_width=True)  # 🔥 Replace with your logo path

@st.cache_data
def load_data():
    deals_df = pd.read_csv("data/deals_updated.csv")
    deal_investors_df = pd.read_csv("data/dealInvestor_updated.csv")
    investors_df = pd.read_csv("data/investors_updated.csv")

    # Strip spaces from column names
    deals_df.columns = deals_df.columns.str.strip()
    deal_investors_df.columns = deal_investors_df.columns.str.strip()
    investors_df.columns = investors_df.columns.str.strip()

    # Convert amounts to numeric and filter out invalid data
    deals_df["amount"] = pd.to_numeric(deals_df["amount"], errors="coerce")
    deals_df = deals_df[deals_df["amount"] > 0]

    return deals_df, deal_investors_df, investors_df

deals_df, deal_investors_df, investors_df = load_data()

def get_top_sectors():
    sector_data = deals_df.groupby("primaryTag")["amount"].sum().reset_index()
    sector_data = sector_data.sort_values(by="amount", ascending=False).head(5)
    return sector_data.to_string(index=False)

def get_top_regions():
    region_data = deals_df.groupby("headquarters")["amount"].sum().reset_index()
    region_data = region_data.sort_values(by="amount", ascending=False).head(5)
    return region_data.to_string(index=False)

def get_active_investors():
    investor_data = deal_investors_df.groupby("investorName")["dealId"].count().reset_index()
    investor_data = investor_data.sort_values(by="dealId", ascending=False).head(5)
    return investor_data.to_string(index=False)


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask BrewBot about Canadian tech startups...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        full_query = f"""
        Use the following investment data to answer the user's question:

        📊 **Top Sectors (Total Investment):**  
        {get_top_sectors()}

        📍 **Top Investment Regions:**  
        {get_top_regions()}

        💰 **Most Active Investors:**  
        {get_active_investors()}

        **User Question:** {user_input}
        """
        response = genai.GenerativeModel("gemini-pro").generate_content(full_query)
        ai_response = response.text
    except Exception as e:
        ai_response = f"⚠️ Error: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})