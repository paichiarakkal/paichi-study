import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI ULTIMATE v8.2", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM PURPLE GOLD THEME ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.85) !important; backdrop-filter: blur(10px); }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .purple-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 25px;
        border: 2px solid rgba(255, 215, 0, 0.3);
        text-align: center;
        margin-bottom: 25px;
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 3. APP LOGIC ---
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
    
    # 🔒 Shabana - Add Entry മാത്രം. Faisal - എല്ലാം കാണാം.
    if curr_user == "shabana":
        page = "💰 Add Entry"
    else:
        st.sidebar.title(f"👤 {curr_user.capitalize()}")
        # ഇവിടെ "💰 Add Entry" നിനക്കും കൂടി കാണാൻ പറ്റുന്ന രീതിയിൽ ഉൾപ്പെടുത്തി
        page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    # --- PAGES ---
    if page == "💰 Add Entry":
        st.title("Quick Transaction")
        v = speech_to_text(language='ml', key='voice')
        
        # ഫോം ഇവിടെ കൃത്യമായി തുടങ്ങുന്നു
        with st.form("quick_entry_form", clear_on_submit=True):
            it = st.text_input("Item Description", value=v if v else "")
            # എക്സ്ട്രാ പൂജ്യങ്ങൾ ഒഴിവാക്കി
            am = st.number_input("Amount", min_value=0, step=1, value=0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            # നിന്റെ ഫോട്ടോയിൽ കണ്ട എറർ മാറാൻ ഈ ബട്ടൺ ഇവിടെ നൽകി
            submitted = st.form_submit_button("SAVE TO SHEET")
            
            if submitted:
                if it and am > 0:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{curr_user.capitalize()}] {it}",
                        "entry.1460982454": d,
                        "entry.1221658767": c
                    })
                    st.success("വിവരങ്ങൾ വിജയകരമായി സേവ് ചെയ്തു! ✅")
                else:
                    st.error("വിവരങ്ങൾ പൂർണ്ണമായി നൽകുക!")

    elif page == "📊 Advisor" and curr_user != "shabana":
        st.title("Trading Advisor")
        st.write("Market levels and signals will appear here.")

    elif page == "🏠 Dashboard" and curr_user != "shabana":
        st.title("Finance Dashboard")
        st.write("Total income and expenses summary.")

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("Transaction History")
        # ഗൂഗിൾ ഷീറ്റിലെ ഹിസ്റ്ററി കാണാൻ

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
