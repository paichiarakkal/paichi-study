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

st.set_page_config(page_title="PAICHI ELITE", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 ELITE AI UI DESIGN ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    .stApp { background: #010409; color: #e6edf3; }
    
    /* Premium Header */
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #ffd700, #b8860b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 20px;
    }

    /* Spent Card */
    .balance-card {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        border: 2px solid #ffd700;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.15);
        margin-bottom: 30px;
    }

    /* AI Tile Buttons */
    .stButton>button {
        background: #161b22 !important;
        color: #ffd700 !important;
        border: 1px solid #30363d !important;
        border-radius: 20px !important;
        height: 100px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        transition: 0.3s !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    
    .stButton>button:hover {
        border: 1px solid #ffd700 !important;
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }

    /* Back Button */
    .back-btn button {
        height: 40px !important;
        background: transparent !important;
        color: #8b949e !important;
        border: 1px solid #30363d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAV LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<div class='main-header'>PAICHI NEURAL</div>", unsafe_allow_html=True)
    
    # Live Total Expense
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="balance-card">
            <p style="color: #8b949e; font-size: 16px; letter-spacing: 2px;">TOTAL EXPENDITURE</p>
            <h1 style="font-size: 55px; color: #fff; margin: 10px 0;">₹ {total:,.2f}</h1>
            <div style="width: 50px; height: 3px; background: #ffd700; margin: 0 auto;"></div>
        </div>
    ''', unsafe_allow_html=True)

    # AI Grid Layout
    st.write("### 📟 System Control")
    
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        if st.button("➕\nADD ENTRY"): navigate("ADD")
    with row1_c2:
        if st.button("📊\nREPORTS"): navigate("REPORTS")

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        if st.button("🌙\nPEACE"): navigate("PEACE")
    with row2_c2:
        if st.button("🔴\nDEBTS"): navigate("DEBTS")

    row3_c1, row3_c2 = st.columns(2)
    with row3_c1:
        if st.button("📝\nTASKS"): navigate("TASKS")
    with row3_c2:
        if st.button("🔄\nREFRESH"): st.rerun()

# --- ➕ ADD ENTRY PAGE ---
elif st.session_state.page == "ADD":
    st.markdown("<h2 style='color: #ffd700;'>📥 Add Entry</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK", key="back_add"): navigate("🏠 HOME")
    
    st.write("🎙️ **Voice Recognition**")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    
    with st.form("entry_form"):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0)
        if st.form_submit_button("CONFIRM SAVE"):
            if item and amt:
                requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success("Data Synced to Cloud! ✅")

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "PEACE":
    st.markdown("<h2 style='color: #ffd700;'>🌙 Peace Mode</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK", key="back_peace"): navigate("🏠 HOME")
    
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote('🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n🔵🔴🟢🟡')}"
    st.markdown(f'''
        <div style="background: #161b22; padding: 60px; border-radius: 30px; text-align: center; border: 1px solid #ffd700; margin-top: 20px;">
            <h1 style="color: white;">Assalamu Alaikum</h1>
            <p style="color: #8b949e;">Send morning greeting to Faisal</p><br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; border: none; padding: 15px 50px; border-radius: 15px; font-weight: bold; font-size: 20px;">SEND 🚀</button>
            </a>
        </div>
    ''', unsafe_allow_html=True)

# --- 📊 REPORTS ---
elif st.session_state.page == "REPORTS":
    st.markdown("<h2 style='color: #ffd700;'>📊 Financial Analysis</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK", key="back_rep"): navigate("🏠 HOME")
    try:
        df = pd.read_csv(CSV_URL)
        st.plotly_chart(px.pie(df, values=df.columns[-1], names=df.columns[1], hole=0.5, template="plotly_dark"))
        st.dataframe(df, use_container_width=True)
    except: st.error("No Data Found!")

# --- 🔴 DEBTS ---
elif st.session_state.page == "DEBTS":
    st.markdown("<h2 style='color: #ffd700;'>🔴 Debt Tracker</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK"): navigate("🏠 HOME")
    st.info("ഈ സെക്ഷൻ ഉടൻ അപ്ഡേറ്റ് ചെയ്യും.")

# --- 📝 TASKS ---
elif st.session_state.page == "TASKS":
    st.markdown("<h2 style='color: #ffd700;'>📝 Task Manager</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK"): navigate("🏠 HOME")
    st.info("ലിസ്റ്റുകൾ ഇവിടെ ചേർക്കാം.")

st.markdown("<br><p style='text-align: center; color: #30363d;'>PAICHI ELITE v38.0 | Powered by Neural Engine</p>", unsafe_allow_html=True)
