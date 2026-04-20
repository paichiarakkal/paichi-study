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
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GLASS v13.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM GLASS DESIGN ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { 
        background: linear-gradient(135deg, #1A0521 0%, #4B0082 50%, #1A0521 100%); 
        color: #fff; 
    }
    
    /* Black Glass Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Glass Boxes */
    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        text-align: center;
        margin-bottom: 20px;
    }
    
    .balance-card {
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid #FFD700;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }

    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { 
        background: linear-gradient(90deg, #FFD700, #FFA500); 
        color: #000; border-radius: 12px; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. CORE FUNCTIONS ---
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return None

def calculate_balance(df):
    if df is not None:
        cr = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        db = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return cr - db
    return 0

def get_market_signals():
    results = []
    for name, sym in {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}.items():
        try:
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            lp = df['Close'].iloc[-1]
            # Pivot Point & RSI simplified for speed
            h, l, c = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (h + l + c) / 3
            if lp > pivot: sig, col = "🚀 BUY", "#00FF00"
            else: sig, col = "📉 SELL", "#FF3131"
            if name == "Crude Fut": lp = lp * 83.5 * 1.15
            results.append({"name": name, "price": lp, "sig": sig, "col": col})
        except: continue
    return results

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    user = st.session_state.user
    df = load_data()
    bal = calculate_balance(df)
    
    # Navigation
    if user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    # 💰 ADD ENTRY PAGE (Balance visible for both)
    if page == "💰 Add Entry":
        st.title("Transaction Entry")
        st.markdown(f'<div class="balance-card"><h3>Current Balance</h3><h1 style="color:#FFD700 !important; margin:0;">₹{bal:,.0f}</h1></div>', unsafe_allow_html=True)
        
        v = speech_to_text(language='ml', key='v')
        with st.form("entry_form"):
            it = st.text_input("Details", value=v if v else "")
            am = st.number_input("Amount", min_value=1, value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE TO SHEET"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                    st.success("Saved! ✅"); st.rerun()

    # 📊 ADVISOR PAGE
    elif page == "📊 Advisor":
        st.title("Smart Advisor")
        for s in get_market_signals():
            st.markdown(f'<div class="glass-card" style="border-bottom: 2px solid {s["col"]}"><h3>{s["name"]}</h3><h1 style="color:{s["col"]} !important;">{s["sig"]}</h1><h2>₹{s["price"]:,.0f}</h2></div>', unsafe_allow_html=True)

    # 🏠 DASHBOARD
    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f'<div class="glass-card"><h1>Total Net Balance</h1><h1 style="color:gold !important; font-size:60px;">₹{bal:,.0f}</h1></div>', unsafe_allow_html=True)

    # 🔍 HISTORY
    elif page == "🔍 History":
        st.title("History")
        if df is not None: st.dataframe(df.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
