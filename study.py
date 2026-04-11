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

st.set_page_config(page_title="PAICHI OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 OS STYLE UI (GOLD & DARK) ---
st.markdown("""
    <style>
    /* സൈഡ്‌ബാർ പൂർണ്ണമായും ഹൈഡ് ചെയ്യുന്നു */
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    
    .stApp { background: #000000; color: #ffffff; }
    
    /* App Icon Style (Tiles) */
    .stButton>button {
        background: linear-gradient(145deg, #1e1e1e, #111111) !important;
        color: #ffd700 !important;
        border: 1px solid #333333 !important;
        border-radius: 25px !important; /* ആപ്പ് ഐക്കൺ പോലെ റൗണ്ട് */
        height: 120px !important;
        width: 100% !important;
        font-size: 16px !important;
        font-weight: bold !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.8);
        margin-bottom: 15px;
    }
    
    .stButton>button:hover {
        border: 1px solid #ffd700 !important;
        transform: scale(1.05);
        background: #1a1a1a !important;
    }

    /* Total Spent Display */
    .status-bar {
        background: #111111;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #ffd700;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAV LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN (APP GRID) ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center; color: #ffd700; margin-top: -30px;'>PAICHI OS</h1>", unsafe_allow_html=True)
    
    # Live Expense Card
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="status-bar">
            <p style="color: #888; margin:0;">TOTAL SPENT</p>
            <h1 style="color: #fff; margin:0;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)

    # App Grid (3 Columns like phone home screen)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰\nADD"): navigate("ADD")
        if st.button("📊\nDATA"): navigate("DATA")
    
    with col2:
        if st.button("🌙\nPEACE"): navigate("PEACE")
        if st.button("🔴\nDEBTS"): navigate("DEBTS")
        
    with col3:
        if st.button("📝\nTASKS"): navigate("TASKS")
        if st.button("🔄\nSYNC"): st.rerun()

# --- 💰 ADD ENTRY PAGE ---
elif st.session_state.page == "ADD":
    st.markdown("<h2 style='color: #ffd700;'>📥 Add Entry</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK"): navigate("🏠 HOME")
    
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("entry_form"):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("Cloud-ലേക്ക് മാറ്റി! ✅")

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "PEACE":
    st.markdown("<h2 style='color: #ffd700;'>🌙 Peace Mode</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK"): navigate("🏠 HOME")
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote('🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n🔵🔴🟢🟡')}"
    st.markdown(f'''
        <div style="background: #111; padding: 40px; border-radius: 20px; text-align: center; border: 1px solid #ffd700;">
            <h2 style="color: white;">Assalamu Alaikum</h2>
            <br><a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; border: none; padding: 15px 30px; border-radius: 10px; font-weight: bold;">SEND TO WA 🚀</button>
            </a>
        </div>
    ''', unsafe_allow_html=True)

# --- മറ്റ് പേജുകൾ ---
else:
    st.title(st.session_state.page)
    if st.button("🔙 BACK"): navigate("🏠 HOME")
    st.info("ഈ സെക്ഷൻ വർക്കിംഗ്‌ ആണ്!")

st.markdown("<br><p style='text-align: center; color: #333;'>PAICHI OS v39.0</p>", unsafe_allow_html=True)
