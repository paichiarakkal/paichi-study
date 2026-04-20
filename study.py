import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PREMIUM v9.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN (Purple & Gold) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { 
        background: rgba(0, 0, 0, 0.7) !important; 
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1); 
    }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 25px;
        border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. CORE LOGIC ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    
    # SHABANA ACCESS: Only Balance and Add Entry
    if curr_user == "shabana":
        page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry"])
    else:
        st.sidebar.title(f"👤 {curr_user.capitalize()}")
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History", "🤝 Debt Tracker"])

    # --- PAGES ---
    if page == "🏠 Dashboard":
        st.title("Financial Status")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
            balance = total_in - total_out
            st.markdown(f"""<div class="purple-box"><p>Current Balance</p><h1 style="color:#FFD700;">₹{balance:,.0f}</h1></div>""", unsafe_allow_html=True)
        except: st.error("Error loading data")

    elif page == "💰 Add Entry":
        st.title("Add Transaction")
        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_f", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            # Amount
