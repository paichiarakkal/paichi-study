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

st.set_page_config(page_title="PAICHI GRID OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 GRID OS CSS ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    .stApp { background: #000000; color: #ffffff; }
    
    /* Smart Grid Tile Style */
    .stButton > button {
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a) !important;
        color: #ffd700 !important;
        border: 1px solid #333 !important;
        border-radius: 20px !important;
        height: 100px !important; /* വലിപ്പം കുറച്ചു */
        width: 100% !important;
        font-size: 14px !important;
        font-weight: bold !important;
        margin-bottom: 5px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    .stButton > button:active {
        transform: scale(0.95);
        border-color: #ffd700 !important;
    }

    /* Status Panel */
    .status-panel {
        background: #0a0a0a;
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #ffd700;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAV LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN (3x3 GRID) ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h2 style='text-align: center; color: #ffd700; margin-bottom: 20px;'>PAICHI OS</h2>", unsafe_allow_html=True)
    
    # Live Expense Display
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="status-panel">
            <p style="color: #666; margin:0; font-size: 12px;">SPENT THIS MONTH</p>
            <h2 style="color: #fff; margin:0;">₹ {total:,.2f}</h2>
        </div>
    ''', unsafe_allow_html=True)

    # --- THE 3x3 GRID ---
    # Row 1 (1 2 3)
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1: 
        if st.button("💰\nADD"): navigate("ADD")
    with r1_c2: 
        if st.button("📊\nDATA"): navigate("DATA")
    with r1_c3: 
        if st.button("🌙\nPEACE"): navigate("PEACE")

    # Row 2 (4 5 6)
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    with r2_c1: 
        if st.button("🔴\nDEBTS"): navigate("DEBTS")
    with r2_c2: 
        if st.button("📝\nTASKS"): navigate("TASKS")
    with r2_c3: 
        if st.button("🛒\nLIST"): navigate("LIST")

    # Row 3 (7 8 9)
    r3_c1, r3_c2, r3_c3 = st.columns(3)
    with r3_c1: 
        if st.button("⚙️\nSET"): navigate("SETTINGS")
    with r3_c2: 
        if st.button("🔄\nSYNC"): st.rerun()
    with r3_c3: 
        if st.button("📞\nSOS"): navigate("PEACE")

# --- 💰 ADD PAGE ---
elif st.session_state.page == "ADD":
    st.markdown("<h3 style='color: #ffd700;'>📥 Add Entry</h3>", unsafe_allow_html=True)
    if st.button("🔙 HOME"): navigate("🏠 HOME")
    
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("സേവ് ചെയ്തു!")

# --- 📊 DATA PAGE ---
elif st.session_state.page == "DATA":
    st.markdown("<h3 style='color: #ffd700;'>📊 Reports</h3>", unsafe_allow_html=True)
    if st.button("🔙 HOME"): navigate("🏠 HOME")
    try:
        df = pd.read_csv(CSV_URL)
        st.plotly_chart(px.pie(df, values=df.columns[-1], names=df.columns[1], hole=0.4, template="plotly_dark"))
    except: st.error("No data found")

else:
    st.title(st.session_state.page)
    if st.button("🔙 HOME"): navigate("🏠 HOME")

st.markdown("<p style='text-align: center; color: #222; margin-top: 50px;'>PAICHI GRID v40.0</p>", unsafe_allow_html=True)
