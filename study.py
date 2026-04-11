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

# സൈഡ്‌ബാർ പൂർണ്ണമായും ഹൈഡ് ചെയ്യുന്നു
st.set_page_config(page_title="PAICHI V36", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 PREMIUM GOLDEN UI (NO SIDEBAR) ---
st.markdown("""
    <style>
    /* സൈഡ്‌ബാർ ബട്ടൺ കാണാതിരിക്കാൻ */
    [data-testid="collapsedControl"] { display: none; }
    
    .stApp { background: #020617; color: #f8fafc; }
    
    /* മുകളിലെ മെനു ബാർ */
    .nav-container {
        display: flex;
        overflow-x: auto;
        gap: 10px;
        padding: 10px;
        background: #0f172a;
        border-bottom: 2px solid #ffd700;
        margin-bottom: 20px;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    
    .glass-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #ffd700;
    }

    /* ബട്ടൺ സ്റ്റൈൽ */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: bold !important;
        border: 1px solid #ffd700 !important;
        background: transparent !important;
        color: #ffd700 !important;
        min-width: 120px;
    }
    
    .stButton>button:active, .stButton>button:focus {
        background: #ffd700 !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# മുകളിലെ മെനു സെക്ഷൻ
st.markdown("<h2 style='text-align: center; color: #ffd700; margin-bottom: 5px;'>✨ PAICHI AI ✨</h2>", unsafe_allow_html=True)

# ഒരു വരിയിൽ മെനു ബട്ടണുകൾ നൽകുന്നു
col_nav = st.columns(6)
with col_nav[0]: 
    if st.button("HOME"): st.session_state.page = "🏠 Dashboard"; st.rerun()
with col_nav[1]: 
    if st.button("PEACE"): st.session_state.page = "🌙 Peace Mode"; st.rerun()
with col_nav[2]: 
    if st.button("ADD"): st.session_state.page = "💰 Transactions"; st.rerun()
with col_nav[3]: 
    if st.button("REPORTS"): st.session_state.page = "📊 Reports"; st.rerun()
with col_nav[4]: 
    if st.button("DEBTS"): st.session_state.page = "🔴 Debt Tracker"; st.rerun()
with col_nav[5]: 
    if st.button("TASKS"): st.session_state.page = "✅ To-Do List"; st.rerun()

st.markdown("---")

# --- 🏠 DASHBOARD ---
if st.session_state.page == "🏠 Dashboard":
    st.title("Main Board 💹")
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="glass-card">
            <p style="color: #ffd700; margin: 0; font-size: 18px;">Total Spent</p>
            <h1 style="color: #ffffff; margin: 0; font-size: 45px;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "🌙 Peace Mode":
    st.title("Neural Greeting 🌙")
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'''
        <div style="background: #1e293b; padding: 50px; border-radius: 25px; text-align: center; border: 2px solid #ffd700;">
            <h1 style="color: #ffd700 !important;">Assalamu Alaikum</h1><br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none; font-size: 18px;">SEND 🚀</button>
            </a>
        </div>
    ''', unsafe_allow_html=True)

# --- 💰 TRANSACTIONS ---
elif st.session_state.page == "💰 Transactions":
    st.title("Add Entry 📥")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_in')
    with st.form("entry"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("സേവ് ചെയ്തു!")

else:
    st.title(st.session_state.page)
    st.info("ഈ സെക്ഷൻ റെഡിയാണ് 🟢")

st.markdown("<br><p style='text-align: center; color: gray;'>PAICHI AI v36.0 | Golden No-Sidebar Edition</p>", unsafe_allow_html=True)
