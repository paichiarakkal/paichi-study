import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI PURPLE GOLD v4.5", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 25px;
        border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 25px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. 📊 TRIPLE INDICATOR ENGINE ---
def get_triple_advisor():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        results = []
        for name, sym in symbols.items():
            df = yf.download(sym, period="5d", interval="5m", progress=False)
            if df.empty: continue
            last_p = float(df['Close'].iloc[-1])
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            atr = (df['High'] - df['Low']).rolling(window=10).mean().iloc[-1]
            lower_band = ((df['High'] + df['Low']) / 2).iloc[-1] - (3 * atr)
            st_buy = last_p > lower_band
            if last_p > pivot and rsi > 55 and st_buy: signal, color = "🚀 BUY", "#00FF00"
            elif last_p < pivot and rsi < 45 and not st_buy: signal, color = "📉 SELL", "#FF3131"
            else: signal, color = "⚖️ WAIT", "#FFFF00"
            if name == "Crude Fut": last_p = last_p * 83.5 * 1.15
            results.append({"name": name, "price": last_p, "signal": signal, "rsi": float(rsi), "color": color})
        return results
    except: return None

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History"])

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    if page == "📊 Advisor":
        st.title("🚀 Live Signals")
        markets = get_triple_advisor()
        if markets:
            for m in markets:
                st.markdown(f'<div class="purple-box" style="border-color:{m["color"]};"><h2>{m["name"]}</h2><h1 style="color:{m["color"]};">{m["signal"]}</h1><h3>₹{m["price"]:,.0f}</h3><p>RSI: {m["rsi"]:.1f}</p></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Add Transaction")
        st.write("🎙️ Malayalam-il parayu (e.g. 'Biriyani 150')")
        
        # Voice input logic
        voice_text = speech_to_text(language='ml-IN', start_prompt="Talk now...", key='recorder')
        
        with st.form("entry_form", clear_on_submit=True):
            item = st.text_input("Description", value=voice_text if voice_text else "")
            amount = st.number_input("Amount", min_value=0.0, value=None)
            ttype = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE TO GOOGLE SHEET"):
                if item and amount:
                    d, c = (amount, 0) if ttype == "Debit" else (0, amount)
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {item}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    }
                    requests.post(FORM_API, data=payload)
                    st.success("Successfully Saved! ✅")
                    st.rerun()

    elif page == "🔍 History":
        st.title("History")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            st.dataframe(df.iloc[::-1], use_container_width=True)
        except: st.error("Spreadsheet load aayilla.")
