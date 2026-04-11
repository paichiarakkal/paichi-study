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

st.set_page_config(page_title="PAICHI ATOMIC GOLD", layout="wide")

# --- 🌗 ATOMIC GOLD CSS ---
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 2px solid #ffd700;
    }
    
    /* Golden Sidebar Text */
    [data-testid="stSidebar"] button p {
        color: #ffd700 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }

    /* Sidebar buttons styling */
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        text-align: left !important;
    }

    [data-testid="stSidebar"] button:hover {
        border: 1px solid #ffd700 !important;
        background: rgba(255, 215, 0, 0.1) !important;
    }

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
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 ATOMIC NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

def change_page(page_name):
    st.session_state.page = page_name
    # Pydroid/Mobile-il sidebar taniyē close āvān ithu sahāyikkum

# Sidebar Header
st.sidebar.markdown("<h1 style='text-align: center; color: #ffd700;'>✨ PAICHI ✨</h1>", unsafe_allow_html=True)

# Sidebar Buttons (Radio-inu pakaram Buttons - Speed kūṭan)
if st.sidebar.button("🏠 DASHBOARD"): change_page("🏠 Dashboard")
if st.sidebar.button("🌙 PEACE MODE"): change_page("🌙 Peace Mode")
if st.sidebar.button("💰 TRANSACTIONS"): change_page("💰 Transactions")
if st.sidebar.button("📊 REPORTS"): change_page("📊 Reports")
if st.sidebar.button("🔴 DEBT TRACKER"): change_page("🔴 Debt Tracker")
if st.sidebar.button("✅ TO-DO LIST"): change_page("✅ To-Do List")

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
            <h1 style="color: #ffffff; margin: 0; font-size: 45px;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "🌙 Peace Mode":
    st.title("Morning Peace 🌙")
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'''
        <div style="background: #1e293b; padding: 40px; border-radius: 25px; text-align: center; border: 2px solid #ffd700;">
            <h1 style="color: #ffd700 !important;">Assalamu Alaikum</h1><br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none;">SEND 🚀</button>
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
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("Cloud-lēkku ayachu!")

else:
    st.header(st.session_state.page)
    st.info("System Online 🟡")

st.sidebar.write("---")
st.sidebar.caption("PAICHI AI ATOMIC v33.0")
