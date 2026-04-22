import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# Password and Users
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v4.7", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.9) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 12px; font-weight: bold; width: 100%; border: none; height: 3em; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px;
        border: 1px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    h1, h2, h3, p, label { color: white !important; font-family: 'sans-serif'; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 TRADING ENGINE ---
def get_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.download(sym, period="2d", interval="5m", progress=False)
            if df.empty: continue
            last_p = float(df['Close'].iloc[-1])
            atr = (df['High'] - df['Low']).rolling(window=10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            signal = "🚀 BUY" if last_p > lower_band else "📉 SELL"
            color = "#00FF00" if signal == "🚀 BUY" else "#FF3131"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "color": color})
        return results
    except: return None

# --- 4. LOGIN SYSTEM ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    
    # --- PRIVACY LOGIC (Old style) ---
    if curr_user == "shabana":
        page = "💰 Add Entry" # ശബാനയ്ക്ക് ഈ പേജ് മാത്രമേ വരൂ
    else:
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "📊 Advisor":
        st.title("🚀 Smart Advisor")
        data = get_advisor()
        if data:
            for m in data:
                st.markdown(f'<div class="purple-box" style="border-color:{m["color"]};"><h2>{m["name"]}</h2><h1 style="color:{m["color"]};">{m["signal"]}</h1><h2>₹{m["price"]:,.0f}</h2></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            total_in = pd.to_numeric(df['Credit'], errors='coerce').sum()
            total_out = pd.to_numeric(df['Debit'], errors='coerce').sum()
            st.markdown(f'<div class="purple-box"><h4>Net Balance</h4><h1>₹{total_in - total_out:,.2f}</h1></div>', unsafe_allow_html=True)
        except: st.write("Loading...")

    elif page == "💰 Add Entry":
        st.title("Atomic Voice Entry")
        
        # ബാലൻസ് നിനക്ക് മാത്രം കാണാം
        if curr_user != "shabana":
            try:
                df_bal = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
                bal = pd.to_numeric(df_bal['Credit'], errors='coerce').sum() - pd.to_numeric(df_bal['Debit'], errors='coerce').sum()
                st.markdown(f'<div class="purple-box" style="padding:15px;"><h4>Balance: ₹{bal:,.2f}</h4></div>', unsafe_allow_html=True)
            except: pass

        st.write("🎙️ 'Chaya 10' എന്ന് പറയുക...")
        voice_input = speech_to_text(language='ml-IN', start_prompt="Talk Now", key='atomic_voice')
        
        # --- ATOMIC VOICE AUTOMATION ---
        final_amount = None
        final_desc = ""
        if voice_input:
            nums = re.findall(r'\d+', voice_input)
            if nums:
                final_amount = float(nums[0])
                final_desc = voice_input.replace(nums[0], "").strip()
            else:
                final_desc = voice_input

        with st.form("entry_form", clear_on_submit=True):
            item = st.text_input("Item Description", value=final_desc)
            amount = st.number_input("Amount", min_value=0.0, value=final_amount)
            ttype = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE DATA"):
                if item and amount:
                    d, c = (amount, 0) if ttype == "Debit" else (0, amount)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {item}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("രേഖപ്പെടുത്തി! ✅")
                    st.rerun()

    elif page == "🔍 History":
        st.title("Transaction History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.write("Loading...")
