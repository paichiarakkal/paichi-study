import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. Settings
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"
MY_NUMBER = "918714752210"

st.set_page_config(page_title="PAICHI OS GRID", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 ULTRA COMPACT GRID CSS ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    .stApp { background: #000000; color: #ffffff; }
    
    /* ബട്ടണുകൾ ചെറുതാക്കാനും ഐക്കൺ സ്റ്റൈലിനും */
    .stButton > button {
        background: #111111 !important;
        color: #ffd700 !important;
        border: 1px solid #222 !important;
        border-radius: 18px !important;
        height: 85px !important; /* വലിപ്പം കുറച്ചു */
        width: 100% !important;
        font-size: 13px !important;
        font-weight: bold !important;
        margin-bottom: 5px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: 0.2s;
    }
    
    .stButton > button:active {
        transform: scale(0.9);
        background: #222 !important;
    }

    /* Status Bar */
    .status-card {
        background: linear-gradient(180deg, #0a0a0a, #000);
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

def nav(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 MAIN GRID (3x3 Layout) ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h3 style='text-align: center; color: #ffd700; margin-top: -20px;'>PAICHI OS</h3>", unsafe_allow_html=True)
    
    # Live Total Display
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="status-card">
            <p style="color: #555; margin:0; font-size: 11px; text-transform: uppercase;">Total Spent</p>
            <h2 style="color: #fff; margin:0;">₹ {total:,.2f}</h2>
        </div>
    ''', unsafe_allow_html=True)

    # --- THE COMPACT GRID (3x3) ---
    # വരി 1
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("💰\nADD"): nav("ADD")
    with c2: 
        if st.button("📊\nDATA"): nav("DATA")
    with c3: 
        if st.button("🌙\nPEACE"): nav("PEACE")

    # വരി 2
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("🔴\nDEBTS"): nav("DEBTS")
    with c5: 
        if st.button("📝\nTASKS"): nav("TASKS")
    with c6: 
        if st.button("🛒\nLIST"): nav("LIST")

    # വരി 3
    c7, c8, c9 = st.columns(3)
    with c7: 
        if st.button("⚙️\nSET"): nav("SETTINGS")
    with c8: 
        if st.button("🔄\nSYNC"): st.rerun()
    with c9: 
        if st.button("📞\nSOS"): nav("PEACE")

# --- 💰 ADD PAGE ---
elif st.session_state.page == "ADD":
    st.markdown("<h3 style='color: #ffd700;'>📥 Add Entry</h3>", unsafe_allow_html=True)
    if st.button("🔙 BACK"): nav("🏠 HOME")
    
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("സേവ് ചെയ്തു!")

else:
    st.title(st.session_state.page)
    if st.button("🔙 BACK"): nav("🏠 HOME")

st.markdown("<p style='text-align: center; color: #111; margin-top: 30px;'>GRID OS v41.0</p>", unsafe_allow_html=True)
