import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API")
genai.configure(api_key=gemini_api_key)

# Set Page Configuration
st.set_page_config(
    page_title="BrewBot",
    page_icon="dashboard/images/bb.png",
    layout="wide"
)
st.title("BrewBot: Your AI Investment Assistant")

# Hardcoded responses
hardcoded_responses = {
    "hi brewbot, im an investor! which sectors receive the most early-stage investments?": """Based on the provided investment data, the top sectors that receive the most early-stage investments are:
    
    1. **FinTech**: $74,134,820,490  
    2. **SaaS**: $65,117,535,730  
    3. **AI**: $43,324,259,260  
    """,
    
    "how does Toronto compare to Vancouver in startup investments?": """Toronto has received **$172,241,241,999** in startup investments, while **Vancouver has received $74,871,831,111**.  
    This means that Toronto has received approximately **$97,369,410,888** more in startup investments than Vancouver.""",
    
    "what regions should investors focus on for emerging startups?": """Based on the investment data provided, the regions that investors should focus on for emerging startups are:

    - **Toronto**: $172,241,241,999  
    - **Vancouver**: $74,871,831,111  
    - **Montreal**: $64,989,811,165  
    - **British Columbia**: $29,249,628,855  
    - **Calgary**: $25,310,441,164  
    """
}

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask BrewBot about Canadian tech startups...")

if user_input:
    # Add user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Check if response is hardcoded
    if user_input.lower() in hardcoded_responses:
        ai_response = hardcoded_responses[user_input.lower()]
    else:
        try:
            response = genai.GenerativeModel("gemini-pro").generate_content(user_input)
            ai_response = response.text
        except Exception as e:
            ai_response = f"⚠️ Error: {str(e)}"

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})