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

# --- 🧠 ATOMIC NAV LOGIC (സൈഡ്‌ബാർ തനിയെ പോകാൻ) ---
# initial_sidebar_state="collapsed" പൈഡ്രോയിഡിൽ സൈഡ്‌ബാർ വേഗത്തിൽ മാറ്റാൻ സഹായിക്കും
st.set_page_config(page_title="PAICHI ATOMIC V35", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

def nav_to(page_name):
    st.session_state.page = page_name
    # Pydroid-ൽ ബട്ടൺ അമർത്തുമ്പോൾ റീലോഡ് ആയി സൈഡ്‌ബാർ അടയാൻ സഹായിക്കുന്നു
    st.rerun()

# --- 🌗 PREMIUM GOLD CSS ---
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    
    /* Sidebar Golden Style */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 2px solid #ffd700;
    }
    
    /* സൈഡ്ബാറിലെ ഗോൾഡൻ ബട്ടണുകൾ */
    .stSidebar [data-testid="stButton"] button {
        background: transparent !important;
        color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
        border-radius: 10px !important;
        height: 55px !important;
        margin-bottom: 12px !important;
        font-weight: bold !important;
    }
    
    .stSidebar [data-testid="stButton"] button:hover {
        background: #ffd700 !important;
        color: black !important;
    }

    .glass-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🏰 SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>✨ PAICHI ✨</h1>", unsafe_allow_html=True)
    st.write("")
    
    if st.button("🏠 DASHBOARD", key="btn1", use_container_width=True): nav_to("🏠 Dashboard")
    if st.button("🌙 PEACE MODE", key="btn2", use_container_width=True): nav_to("🌙 Peace Mode")
    if st.button("💰 TRANSACTIONS", key="btn3", use_container_width=True): nav_to("💰 Transactions")
    if st.button("📊 REPORTS", key="btn4", use_container_width=True): nav_to("📊 Reports")
    if st.button("🔴 DEBT TRACKER", key="btn5", use_container_width=True): nav_to("🔴 Debt Tracker")
    if st.button("✅ TO-DO LIST", key="btn6", use_container_width=True): nav_to("✅ To-Do List")
    
    st.write("---")
    st.caption("PAICHI AI V35.0")

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
            <p style="color: #ffd700; margin: 0;">System Active 🟢</p>
            <h1 style="color: #ffffff; margin: 0; font-size: 40px;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)
    st.write("")
    st.info("മെനു കാണാൻ ഇടതുവശത്തെ '>' ചിഹ്നത്തിൽ ക്ലിക്ക് ചെയ്യുക.")

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "🌙 Peace Mode":
    st.title("Neural Greeting 🌙")
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'''
        <div style="background: #1e293b; padding: 40px; border-radius: 25px; text-align: center; border: 2px solid #ffd700;">
            <h1 style="color: #ffd700 !important;">Assalamu Alaikum</h1><br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none;">SEND MESSAGE 🚀</button>
            </a>
        </div>
