import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. Settings
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI MINI", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 മൊബൈൽ സ്ക്രീനിന് വേണ്ടിയുള്ള ഡിസൈൻ ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none; }
    .stApp { background: #000000; color: #ffffff; }
    
    /* 📱 ഫോൺ നേരെ പിടിച്ചാലും 3 കോളങ്ങൾ വരിവരിയായി വരാൻ നിർബന്ധിക്കുന്ന കോഡ് */
    [data-testid="column"] {
        width: 33.33% !important;
        flex: 1 1 33.33% !important;
        min-width: 30% !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* ഐക്കൺ ബട്ടണുകൾ ഡിസൈൻ */
    .stButton > button {
        background: #1a1a1a !important;
        color: #ffd700 !important;
        border: 2px solid #333 !important;
        border-radius: 50% !important; 
        height: 70px !important;
        width: 70px !important;
        margin: 5px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.1);
    }
    
    .status-card {
        background: #0d0d0d;
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #ffd700;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def nav(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h2 style='text-align: center; color: #ffd700; margin-top: -30px;'>PAICHI OS</h2>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        total = pd.to_numeric(df.iloc[:, -1], errors='coerce').sum()
    except: total = 0

    st.markdown(f'<div class="status-card"><h2 style="color: #fff; margin:0;">₹ {total:,.2f}</h2></div>', unsafe_allow_html=True)

    # ഒന്നാമത്തെ വരി (3 ഐക്കണുകൾ)
    c1, c2, c3 = st.columns(3)
    with c1: st.button("💰", on_click=nav, args=("ADD",), key="btn1")
    with c2: st.button("📊", on_click=nav, args=("DATA",), key="btn2")
    with c3: st.button("🌙", on_click=nav, args=("PEACE",), key="btn3")

    st.write("") # ചെറിയ ഗ്യാപ്പ്

    # രണ്ടാമത്തെ വരി (3 ഐക്കണുകൾ)
    c4, c5, c6 = st.columns(3)
    with c4: st.button("🔴", on_click=nav, args=("DEBTS",), key="btn4")
    with c5: st.button("📝", on_click=nav, args=("TASKS",), key="btn5")
    with c6: st.button("🛒", on_click=nav, args=("LIST",), key="btn6")

    st.write("")

    # മൂന്നാമത്തെ വരി (3 ഐക്കണുകൾ)
    c7, c8, c9 = st.columns(3)
    with c7: st.button("⚙️", on_click=nav, args=("SET",), key="btn7")
    with c8: st.button("🔄", on_click=st.rerun, key="btn8")
    with c9: st.button("📞", on_click=nav, args=("PEACE",), key="btn9")

# --- 📥 ADD PAGE ---
elif st.session_state.page == "ADD":
    if st.button("🔙 BACK"): nav("🏠 HOME")
    st.markdown("<h3 style='color: #ffd700;'>📥 Entry</h3>", unsafe_allow_html=True)
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("Synced! ✅")

# --- 📊 DATA PAGE ---
elif st.session_state.page == "DATA":
    if st.button("🔙 BACK"): nav("🏠 HOME")
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        st.dataframe(df, use_container_width=True)
    except: st.error("Error loading data!")

st.markdown("<p style='text-align: center; color: #333; font-size: 10px; margin-top: 50px;'>PAICHI MINI v43.0</p>", unsafe_allow_html=True)
