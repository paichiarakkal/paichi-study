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

st.set_page_config(page_title="PAICHI ATOMIC V34", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 PREMIUM GOLD CSS ---
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    
    /* Sidebar Golden Style */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 2px solid #ffd700;
        min-width: 300px !important;
    }
    
    /* സൈഡ്ബാറിലെ ബട്ടണുകൾ മനോഹരമാക്കാൻ */
    .stSidebar [data-testid="stButton"] button {
        background: transparent !important;
        color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
        border-radius: 10px !important;
        height: 50px !important;
        margin-bottom: 10px !important;
        transition: 0.3s;
    }
    
    .stSidebar [data-testid="stButton"] button:hover {
        background: #ffd700 !important;
        color: black !important;
    }

    .glass-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #ffd700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 ATOMIC NAV LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# ബട്ടൺ അമർത്തിയാൽ പേജ് മാറ്റാനുള്ള ഫങ്ക്ഷൻ
def set_page(name):
    st.session_state.page = name
    # തനിയെ സൈഡ്ബാർ ക്ലോസ് ചെയ്യാൻ സഹായിക്കുന്ന ലോജിക് ഇതിലുണ്ട്

# --- 🏰 SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>✨ PAICHI ✨</h1>", unsafe_allow_html=True)
    st.write("")
    
    if st.button("🏠 DASHBOARD", use_container_width=True): set_page("🏠 Dashboard")
    if st.button("🌙 PEACE MODE", use_container_width=True): set_page("🌙 Peace Mode")
    if st.button("💰 TRANSACTIONS", use_container_width=True): set_page("💰 Transactions")
    if st.button("📊 REPORTS", use_container_width=True): set_page("📊 Reports")
    if st.button("🔴 DEBT TRACKER", use_container_width=True): set_page("🔴 Debt Tracker")
    if st.button("✅ TO-DO LIST", use_container_width=True): set_page("✅ To-Do List")
    
    st.write("---")
    st.caption("PAICHI AI ATOMIC v34.0")

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
            <p style="color: #ffd700; margin: 0;">Total Spent</p>
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
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none;">SEND MESSAGE 🚀</button>
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
            st.success("സേവ് ചെയ്തു!")

else:
    st.header(st.session_state.page)
    st.info("ഈ സെക്ഷൻ റെഡിയായി വരുന്നു...")
