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

st.set_page_config(page_title="PAICHI GOLDEN PRO", layout="wide")

# --- 🌗 PURE GOLD CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background: #020617; color: #f8fafc; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 2px solid #ffd700;
    }
    
    /* Sidebar-ലെ എല്ലാ അക്ഷരങ്ങളും ഗോൾഡൻ */
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p {
        color: #ffd700 !important;
        font-weight: bold !important;
    }

    /* Radio Button (ആ സിൽവർ കളർ സർക്കിൾ) ഗോൾഡൻ ആക്കാൻ */
    div[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #ffd700 !important;
    }
    
    /* സെലക്ട് ചെയ്യാത്ത ബട്ടണുകളുടെ ബോർഡർ */
    div[role="radiogroup"] label div[data-test-id="stMarkdownContainer"] {
        color: #ffd700 !important;
    }

    /* Radio button സർക്കിളിന്റെ ഉള്ളിലെ നിറം മാറ്റാൻ */
    div[role="radiogroup"] [data-testid="stWidgetLabel"] p {
        color: #ffd700 !important;
    }

    /* Input focus and Radio circle */
    div[role="radiogroup"] > label > div:first-child {
        border-color: #ffd700 !important;
    }
    
    div[role="radiogroup"] > label[data-baseweb="radio"] div {
        background-color: transparent !important;
        border-color: #ffd700 !important;
    }

    /* സെലക്ട് ചെയ്യുമ്പോൾ ഉള്ള റേഡിയോ ബട്ടൺ */
    input[type="radio"]:checked + div {
        background-color: #ffd700 !important;
        border-color: #ffd700 !important;
    }

    /* Cards and General Buttons */
    .glass-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #ffd700;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ffd700, #b8860b) !important;
        color: black !important;
        border-radius: 12px !important;
        font-weight: bold;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# Sidebar Header
st.sidebar.markdown("<h1 style='text-align: center; color: #ffd700;'>✨ PAICHI ✨</h1>", unsafe_allow_html=True)

menu_options = ["🏠 Dashboard", "🌙 Peace Mode", "💰 Transactions", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List"]
st.session_state.page = st.sidebar.radio("COMMAND CENTRE:", menu_options, index=menu_options.index(st.session_state.page))

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
            <p style="color: #ffd700; margin: 0;">Total Expenses</p>
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
            <h1 style="color: #ffd700 !important;">Assalamu Alaikum</h1>
            <br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #ffd700; color: black; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; border: none;">SEND TO WHATSAPP 🚀</button>
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
        if st.form_submit_button("SAVE GOLDEN DATA"):
            requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
            st.success("സേവ് ചെയ്തു!")

else:
    st.header(st.session_state.page)
    st.info("Section Active 🟡")

st.sidebar.write("---")
st.sidebar.caption("PAICHI AI GOLD v32.0")
