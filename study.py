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

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AUTO-TRADER Pro", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px;
        border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 TRADING ENGINE ---
def get_trading_signals():
    try:
        symbols = {"Nifty 50": "^NSEI", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.download(sym, period="5d", interval="5m", progress=False)
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

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Balance", "💰 Add Entry", "🔍 History"])

    if page == "📊 Advisor":
        st.title("🚀 Market Signals")
        m_data = get_trading_signals()
        if m_data:
            for m in m_data:
                st.markdown(f'<div class="purple-box" style="border-color:{m["color"]};"><h2>{m["name"]}</h2><h1 style="color:{m["color"]};">{m["signal"]}</h1><h2>₹{m["price"]:,.0f}</h2></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Voice Auto-Entry")
        
        # Live Balance Display
        try:
            df_bal = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            bal = pd.to_numeric(df_bal['Credit'], errors='coerce').sum() - pd.to_numeric(df_bal['Debit'], errors='coerce').sum()
            st.markdown(f'<div class="purple-box"><h4>Current Balance</h4><h1>₹{bal:,.2f}</h1></div>', unsafe_allow_html=True)
        except: pass

        st.write("🎙️ 'Chaya 10' ennu parayu...")
        voice_input = speech_to_text(language='ml-IN', start_prompt="Talk Now", key='voice_recorder')
        
        # --- AUTOMATION LOGIC ---
        detected_amount = None
        description = ""
        if voice_input:
            # വോയിസിൽ നിന്ന് നമ്പറുകൾ മാത്രം എടുക്കുന്നു
            numbers = re.findall(r'\d+', voice_input)
            if numbers:
                detected_amount = float(numbers[0])
                # നമ്പറിനെ ഒഴിവാക്കി ബാക്കി വാക്ക് ഡിസ്ക്രിപ്ഷൻ ആക്കുന്നു
                description = voice_input.replace(numbers[0], "").strip()
            else:
                description = voice_input

        with st.form("entry_form", clear_on_submit=True):
            item = st.text_input("Item", value=description)
            amount = st.number_input("Amount", min_value=0.0, value=detected_amount)
            ttype = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE TO SHEET"):
                if item and amount:
                    d, c = (amount, 0) if ttype == "Debit" else (0, amount)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {item}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("Saved Successfully! ✅")
                    st.rerun()

    elif page == "🔍 History":
        st.title("History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Data Error!")
