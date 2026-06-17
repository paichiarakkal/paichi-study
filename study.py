import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re
import urllib.parse
from streamlit_calendar import calendar

# --- CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI v2.6", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- CSS ---
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082, #0D0214); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; }
    h1, h2, h3 { color: white !important; }
</style>""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

# --- MAIN ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    t_in, t_out, balance = get_totals()
    st.markdown(f'''<div class="balance-banner"><h3>Available Balance</h3><h1>₹{balance:,.2f}</h1></div>''', unsafe_allow_html=True)

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])
    
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        
        # കലണ്ടർ ഡാറ്റ തയ്യാറാക്കുന്നു
        df_cal = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df_cal.columns = df_cal.columns.str.strip()
        df_cal['Date'] = pd.to_datetime(df_cal['Date'], errors='coerce')
        df_cal['Debit'] = pd.to_numeric(df_cal['Debit'], errors='coerce').fillna(0)
        df_cal['Credit'] = pd.to_numeric(df_cal['Credit'], errors='coerce').fillna(0)
        daily = df_cal.groupby(df_cal['Date'].dt.date)[['Credit', 'Debit']].sum().reset_index()
        
        events = []
        for _, row in daily.iterrows():
            if pd.notnull(row['Date']):
                if row['Credit'] > 0:
                    events.append({"title": f"⬆️ ₹{row['Credit']:,.0f}", "start": str(row['Date']), "color": "#28a745"})
                if row['Debit'] > 0:
                    events.append({"title": f"⬇️ ₹{row['Debit']:,.0f}", "start": str(row['Date']), "color": "#dc3545"})
        
        st.subheader("📅 P&L Calendar")
        calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": ""}, "initialView": "dayGridMonth"})

    elif page == "💰 Add Entry":
        st.write("Add Entry Page") # നിങ്ങളുടെ പഴയ കോഡ് ഇവിടെ ചേർക്കുക
        
    elif page == "📊 Report":
        st.write("Report Page") # നിങ്ങളുടെ പഴയ കോഡ് ഇവിടെ ചേർക്കുക
        
    elif page == "🔍 History":
        st.write("History Page") # നിങ്ങളുടെ പഴയ കോഡ് ഇവിടെ ചേർക്കുക
        
    elif page == "🤝 Debt Tracker":
        st.write("Debt Tracker Page") # നിങ്ങളുടെ പഴയ കോഡ് ഇവിടെ ചേർക്കുക
