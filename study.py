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

# --- 🌗 UI DESIGN ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none; }
    .stApp { background: #000000; color: #ffffff; }
    
    /* 📱 FORCE COLUMNS SIDE-BY-SIDE ON MOBILE */
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
        min-width: 33% !important;
    }

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
        font-size: 22px !important;
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

if 'page' not in st.session_state: st.session_state.page = "🏠 HOME"
def nav(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>PAICHI OS</h2>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        total = pd.to_numeric(df.iloc[:, -1], errors='coerce').sum()
    except: total = 0

    st.markdown(f'<div class="status-card"><h2 style="color: #fff; margin:0;">₹ {total:,.2f}</h2></div>', unsafe_allow_html=True)

    # കൃത്യമായി 3 കോളങ്ങൾ വരാൻ
    row1 = st.columns(3)
    with row1[0]: st.button("💰", on_click=nav, args=("ADD",), key="btn1")
    with row1[1]: st.button("📊", on_click=nav, args=("DATA",), key="btn2")
    with row1[2]: st.button("🌙", on_click=nav, args=("PEACE",), key="btn3")

    st.write("")

    row2 = st.columns(3)
    with row2[0]: st.button("🔴", on_click=nav, args=("DEBTS",), key="btn4")
    with row2[1]: st.button("📝", on_click=nav, args=("TASKS",), key="btn5")
    with row2[2]: st.button("🛒", on_click=nav, args=("LIST",), key="btn6")

elif st.session_state.page == "ADD":
    if st.button("🔙 BACK"): nav("🏠 HOME")
    # ... ബാക്കി കോഡ് ...

st.markdown("<p style='text-align: center; color: #333; font-size: 10px;'>PAICHI MINI v43.0</p>", unsafe_allow_html=True)
