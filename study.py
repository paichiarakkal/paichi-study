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

st.set_page_config(page_title="PAICHI ULTIMATE v8.5", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM THEME ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.85) !important; backdrop-filter: blur(10px); }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #FFD700;
        text-align: center;
        margin-bottom: 20px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- BALANCE FETCH FUNCTION ---
def get_current_balance():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        total_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        total_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return total_in - total_out
    except: return 0

# --- 3. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    if curr_user == "shabana": page = "💰 Add Entry"
    else:
        st.sidebar.title(f"👤 {curr_user.capitalize()}")
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Quick Transaction")
        
        # --- മുകളിൽ ബാലൻസ് കാണിക്കുന്നു ---
        bal = get_current_balance()
        st.markdown(f'<div class="balance-box"><p style="margin:0;">Current Balance</p><h2 style="color:#FFD700; margin:0;">₹{bal:,.0f}</h2></div>', unsafe_allow_html=True)

        v = speech_to_text(language='ml', key='voice')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            
            # --- 0 ഒഴിവാക്കാൻ value=None നൽകി ---
            am = st.number_input("Amount", min_value=1, step=1, value=None, placeholder="Enter amount here...")
            
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            submitted = st.form_submit_button("SAVE DATA")
            
            if submitted:
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {it}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("സേവ് ചെയ്തു! ✅")
                    st.rerun()

    elif page == "📊 Advisor":
        st.title("Market Advisor")
        # (Trading Advisor code goes here)

    elif page == "🏠 Dashboard":
        st.title("Dashboard")
        bal = get_current_balance()
        st.write(f"Total Balance: ₹{bal}")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
