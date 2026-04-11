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

st.set_page_config(page_title="PAICHI MINI", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 MINI-ICON UI DESIGN ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none; }
    .stApp { background: #000000; color: #ffffff; }
    
    /* ബട്ടണുകൾക്ക് പകരം റൗണ്ട് ഐക്കണുകൾ */
    .stButton > button {
        background: #1a1a1a !important;
        color: #ffd700 !important;
        border: 2px solid #333 !important;
        border-radius: 50% !important; /* ആപ്പ് ഐക്കൺ പോലെ റൗണ്ട് */
        height: 75px !important;
        width: 75px !important;
        margin: 0 auto !important;
        display: flex !important;
        font-size: 22px !important;
        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.1);
    }
    
    .stButton > button:active {
        transform: scale(0.9);
        border-color: #ffd700 !important;
    }

    /* പേര് ബട്ടണിന് താഴെ വരാൻ */
    .icon-label {
        text-align: center;
        font-size: 11px;
        color: #888;
        margin-top: 5px;
        font-weight: bold;
    }

    .status-card {
        background: #0d0d0d;
        padding: 20px;
        border-radius: 25px;
        border: 1px solid #ffd700;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAV LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def nav(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>PAICHI OS</h2>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="status-card">
            <p style="color: #555; font-size: 11px; margin:0;">TOTAL SPENT</p>
            <h2 style="color: #fff; margin:0;">₹ {total:,.2f}</h2>
        </div>
    ''', unsafe_allow_html=True)

    # --- MINI 3x3 GRID ---
    # ROW 1
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.button("💰", on_click=nav, args=("ADD",))
        st.markdown("<p class='icon-label'>ADD</p>", unsafe_allow_html=True)
    with c2: 
        st.button("📊", on_click=nav, args=("DATA",))
        st.markdown("<p class='icon-label'>DATA</p>", unsafe_allow_html=True)
    with c3: 
        st.button("🌙", on_click=nav, args=("PEACE",))
        st.markdown("<p class='icon-label'>PEACE</p>", unsafe_allow_html=True)

    st.write("") # ചെറിയ വിടവ്

    # ROW 2
    c4, c5, c6 = st.columns(3)
    with c4: 
        st.button("🔴", on_click=nav, args=("DEBTS",))
        st.markdown("<p class='icon-label'>DEBTS</p>", unsafe_allow_html=True)
    with c5: 
        st.button("📝", on_click=nav, args=("TASKS",))
        st.markdown("<p class='icon-label'>TASKS</p>", unsafe_allow_html=True)
    with c6: 
        st.button("🛒", on_click=nav, args=("LIST",))
        st.markdown("<p class='icon-label'>LIST</p>", unsafe_allow_html=True)

    st.write("")

    # ROW 3
    c7, c8, c9 = st.columns(3)
    with c7: 
        st.button("⚙️", on_click=nav, args=("SET",))
        st.markdown("<p class='icon-label'>SETTINGS</p>", unsafe_allow_html=True)
    with c8: 
        st.button("🔄", on_click=st.rerun)
        st.markdown("<p class='icon-label'>SYNC</p>", unsafe_allow_html=True)
    with c9: 
        st.button("📞", on_click=nav, args=("PEACE",))
        st.markdown("<p class='icon-label'>SOS</p>", unsafe_allow_html=True)

# --- 💰 ADD PAGE ---
elif st.session_state.page == "ADD":
    st.markdown("<h3 style='color: #ffd700;'>📥 Entry</h3>", unsafe_allow_html=True)
    if st.button("🔙 BACK"): nav("🏠 HOME")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("Synced! ✅")

else:
    st.title(st.session_state.page)
    if st.button("🔙 BACK"): nav("🏠 HOME")

st.markdown("<p style='text-align: center; color: #111; font-size: 10px; margin-top: 50px;'>PAICHI MINI v43.0</p>", unsafe_allow_html=True)
