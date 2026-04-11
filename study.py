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

st.set_page_config(page_title="PAICHI LUXURY", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 LUXURY AI CSS (GOLD & DARK THEME) ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    .stApp { background: #020617; color: #f8fafc; }
    
    /* Luxury Card Style */
    .nav-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);
        cursor: pointer;
    }
    
    .glass-panel {
        background: rgba(30, 41, 59, 0.7);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 214, 0, 0.3);
        margin-bottom: 20px;
        text-align: center;
    }

    /* AI Model Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: black !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        height: 50px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOME"

def go_to(page):
    st.session_state.page = page
    st.rerun()

# --- 🏠 MAIN PAGE (LUXURY INTERFACE) ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>✨ PAICHI AI ✨</h1>", unsafe_allow_html=True)
    
    # 💰 Balance Card
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
    except: total = 0

    st.markdown(f'''
        <div class="glass-panel">
            <p style="color: #ffd700; font-size: 18px; margin-bottom: 5px;">Total Spent</p>
            <h1 style="font-size: 50px; margin: 0;">₹ {total:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)

    # Smart AI Grid (ഇതാണ് നിന്റെ പുതിയ മെനു)
    st.write("### AI Control Panel")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("🚀 ADD ENTRY"): go_to("💰 Transactions")
        if st.button("📊 ANALYSIS"): go_to("📊 Reports")
        if st.button("🌙 PEACE MODE"): go_to("🌙 Peace Mode")
        
    with c2:
        if st.button("🔴 DEBTS"): go_to("🔴 Debt Tracker")
        if st.button("✅ TASKS"): go_to("✅ To-Do List")
        if st.button("🔄 REFRESH"): st.rerun()

# --- 💰 TRANSACTIONS ---
elif st.session_state.page == "💰 Transactions":
    st.markdown("<h2 style='color: #ffd700;'>📥 New Transaction</h2>", unsafe_allow_html=True)
    if st.button("🔙 BACK TO HOME"): go_to("🏠 HOME")
    
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_in')
    with st.form("entry_form"):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0)
        if st.form_submit_button("SAVE TRANSACTION"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("സേവ് ചെയ്തു!")

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "🌙 Peace Mode":
    st.title("Neural Greeting 🌙")
    if st.button("🔙 BACK"): go_to("🏠 HOME")
    
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'''
        <div style="background: linear-gradient(45deg, #1e293b, #0f172a); padding: 50px; border-radius: 25px; text-align: center; border: 2px solid #ffd700;">
            <h1 style="color: #ffd700 !important;">Assalamu Alaikum</h1><br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none; font-size: 18px;">SEND TO WHATSAPP 🚀</button>
            </a>
        </div>
    ''', unsafe_allow_html=True)

# --- മറ്റ് പേജുകൾ ---
else:
    st.title(st.session_state.page)
    if st.button("🔙 BACK TO HOME"): go_to("🏠 HOME")
    st.info("ഈ സെക്ഷൻ റെഡിയാണ്!")

st.markdown("<br><p style='text-align: center; color: #475569;'>PAICHI LUXURY AI v37.0</p>", unsafe_allow_html=True)
