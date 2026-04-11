import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. Links & Settings
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"
MY_NUMBER = "918714752210"

st.set_page_config(page_title="PAICHI GOLDEN AI", layout="wide")

# --- 🌗 GOLDEN PREMIUM UI DESIGN ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background: #020617; color: #f8fafc; }
    
    /* Sidebar Golden Style */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 2px solid #ffd700;
    }
    
    /* Sidebar-ile Ella Aksharangaḷum Golden Color Ākkunnu */
    [data-testid="stSidebar"] .stText, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] span {
        color: #ffd700 !important; /* Golden Color */
        font-weight: bold !important;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Radio button select cheyyumpōḷ uḷḷa color */
    div[data-testid="stMarkdownContainer"] > p {
        font-size: 18px;
    }
    
    /* Cards and Buttons */
    .glass-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #ffd700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: black !important;
        border-radius: 12px !important;
        font-weight: bold;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# Sidebar Menu
st.sidebar.markdown("<h1 style='text-align: center;'>✨ PAICHI ✨</h1>", unsafe_allow_html=True)
menu_options = ["🏠 Dashboard", "🌙 Peace Mode", "💰 Transactions", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List"]
st.session_state.page = st.sidebar.radio("COMMAND CENTRE:", menu_options, index=menu_options.index(st.session_state.page))

# --- 🏠 DASHBOARD ---
if st.session_state.page == "🏠 Dashboard":
    st.title("Golden Dashboard 💹")
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="glass-card">
            <p style="color: #ffd700; margin: 0;">Total Expenses</p>
            <h1 style="color: #ffffff; margin: 0; font-size: 45px;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "🌙 Peace Mode":
    st.title("Peace Mode 🌙")
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'''
        <div style="background: #1e293b; padding: 50px; border-radius: 25px; text-align: center; border: 2px solid #ffd700;">
            <h1 style="color: #ffd700 !important;">Assalamu Alaikum</h1>
            <br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none; font-size: 18px;">SEND 🚀</button>
            </a>
        </div>
    ''', unsafe_allow_html=True)

# --- 💰 TRANSACTIONS ---
elif st.session_state.page == "💰 Transactions":
    st.title("Add Transaction 📥")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_in')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE GOLDEN DATA"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("Cloud-lēkku mātthi!")

# --- Bākki Ella Sections-um sidebar vazhi rēkhappeṭuṭṭām ---
else:
    st.header(st.session_state.page)
    st.info("System Online 🟢")

st.sidebar.write("---")
st.sidebar.caption("PAICHI AI GOLD v31.0")
