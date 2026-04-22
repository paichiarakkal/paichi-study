import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD PRIVACY", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px;
        border: 1px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 15px;
    }
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    # --- PRIVACY FILTER ---
    # ശബാനയ്ക്ക് "Add Entry" മാത്രമേ കാണാൻ പറ്റൂ
    if curr_user == "shabana":
        menu_options = ["💰 Add Entry"]
    else:
        menu_options = ["📊 Advisor", "🏠 Balance", "💰 Add Entry", "🔍 History"]
        
    page = st.sidebar.radio("Menu", menu_options)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("🚀 Signals")
        # Trading Logic (Shortened for speed)
        try:
            df = yf.download("CL=F", period="1d", interval="5m", progress=False)
            last_p = float(df['Close'].iloc[-1]) * 83.5 * 1.15
            st.markdown(f'<div class="purple-box"><h2>Crude Oil</h2><h1>₹{last_p:,.0f}</h1></div>', unsafe_allow_html=True)
        except: pass

    elif page == "💰 Add Entry":
        st.title("Voice Entry")
        
        # ബാലൻസ് ശബാനയ്ക്ക് കാണിക്കില്ല (Privacy)
        if curr_user != "shabana":
            try:
                df_bal = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
                bal = pd.to_numeric(df_bal['Credit'], errors='coerce').sum() - pd.to_numeric(df_bal['Debit'], errors='coerce').sum()
                st.markdown(f'<div class="purple-box"><h4>Balance: ₹{bal:,.2f}</h4></div>', unsafe_allow_html=True)
            except: pass

        st.write("🎙️ 'Chaya 10' എന്ന് പറയുക...")
        voice_input = speech_to_text(language='ml-IN', start_prompt="Talk Now", key='recorder')
        
        # --- AUTOMATION LOGIC ---
        detected_amount = None
        description = ""
        if voice_input:
            nums = re.findall(r'\d+', voice_input)
            if nums:
                detected_amount = float(nums[0])
                description = voice_input.replace(nums[0], "").strip()
            else:
                description = voice_input

        with st.form("entry_form", clear_on_submit=True):
            item = st.text_input("Item", value=description)
            amount = st.number_input("Amount", min_value=0.0, value=detected_amount)
            ttype = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if item and amount:
                    d, c = (amount, 0) if ttype == "Debit" else (0, amount)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {item}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("Saved! ✅")
                    st.rerun()

    elif page == "🔍 History":
        st.title("History")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        st.dataframe(df.iloc[::-1])
