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

st.set_page_config(page_title="PAICHI GRID OS", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 HARD-CODED 3-COLUMN GRID CSS ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    .stApp { background: #000000; color: #ffffff; }
    
    /* നിർബന്ധമായും 3 കോളങ്ങൾ വരാൻ വേണ്ടിയുള്ള വിദ്യ */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > div {
        width: 33% !important;
        min-width: 33% !important;
    }

    /* ബട്ടൺ ഡിസൈൻ - കൂടുതൽ ചെറുതാക്കി */
    .stButton > button {
        background: #111 !important;
        color: #ffd700 !important;
        border: 1px solid #333 !important;
        border-radius: 20px !important;
        height: 90px !important;
        width: 100% !important;
        font-size: 12px !important;
        font-weight: bold !important;
        padding: 0 !important;
        display: block !important;
    }
    
    .stButton > button:active {
        transform: scale(0.85);
        background: #222 !important;
    }

    .total-card {
        background: linear-gradient(180deg, #0a0a0a, #000);
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #ffd700;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def nav(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN (FIXED 3x3 GRID) ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h3 style='text-align: center; color: #ffd700; margin-top: -25px;'>PAICHI OS</h3>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="total-card">
            <p style="color: #666; font-size: 11px; margin:0;">SPENT THIS MONTH</p>
            <h2 style="color: #fff; margin:0;">₹ {total:,.2f}</h2>
        </div>
    ''', unsafe_allow_html=True)

    # നിർബന്ധമായും 3 കോളങ്ങൾ വരിവരിയായി വരും
    # ROW 1
    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.button("💰\nADD", on_click=nav, args=("ADD",))
    r1c2.button("📊\nDATA", on_click=nav, args=("DATA",))
    r1c3.button("🌙\nPEACE", on_click=nav, args=("PEACE",))

    # ROW 2
    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.button("🔴\nDEBTS", on_click=nav, args=("DEBTS",))
    r2c2.button("📝\nTASKS", on_click=nav, args=("TASKS",))
    r2c3.button("🛒\nLIST", on_click=nav, args=("LIST",))

    # ROW 3
    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.button("⚙️\nSET", on_click=nav, args=("SET",))
    r3c2.button("🔄\nSYNC", on_click=st.rerun)
    r3c3.button("📞\nSOS", on_click=nav, args=("PEACE",))

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
            st.success("Saved! ✅")

else:
    st.title(st.session_state.page)
    if st.button("🔙 BACK"): nav("🏠 HOME")

st.markdown("<p style='text-align: center; color: #111; font-size: 10px;'>ATOMIC GRID v42.0</p>", unsafe_allow_html=True)
