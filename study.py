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

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI EXPENSES v2.6", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 2. 🎨 DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082, #0D0214); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    .category-box { background: rgba(255, 255, 255, 0.08); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def parse_mixed_dates(date_series):
    return pd.to_datetime(date_series, errors='coerce', dayfirst=True)

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

def send_to_google_async(data):
    try: requests.post(FORM_API, data=data, timeout=10)
    except: pass

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI EXPENSES LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    t_in, t_out, balance = get_totals()
    st.markdown(f'''<div class="balance-banner"><h3>Available Balance</h3><h1>₹{balance:,.2f}</h1></div>''', unsafe_allow_html=True)

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])
    
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        df_cal = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df_cal.columns = df_cal.columns.str.strip()
        df_cal['Date'] = parse_mixed_dates(df_cal['Date'])
        df_cal['Credit'] = pd.to_numeric(df_cal['Credit'], errors='coerce').fillna(0)
        df_cal['Debit'] = pd.to_numeric(df_cal['Debit'], errors='coerce').fillna(0)
        daily = df_cal.groupby(df_cal['Date'].dt.date)[['Credit', 'Debit']].sum().reset_index()
        events = []
        for _, row in daily.iterrows():
            if pd.notnull(row['Date']):
                if row['Credit'] > 0: events.append({"title": f"⬆️ {row['Credit']:,.0f}", "start": str(row['Date']), "color": "#28a745"})
                if row['Debit'] > 0: events.append({"title": f"⬇️ {row['Debit']:,.0f}", "start": str(row['Date']), "color": "#dc3545"})
        calendar(events=events, options={"headerToolbar": {"left": "prev,next", "center": "title", "right": ""}, "initialView": "dayGridMonth"})

    elif page == "💰 Add Entry":
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description")
            am = st.number_input("Amount", min_value=0.0)
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c}
                send_to_google_async(payload)
                st.success("Saved!")

    elif page in ["📊 Report", "🔍 History"]:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df = df.dropna(subset=['Date'])
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        months = df.sort_values(by='Date', ascending=False)['Month'].unique()
        
        sel_month = st.selectbox("Select Month", months)
        monthly_df = df[df['Month'] == sel_month].copy()
        
        if page == "📊 Report":
            monthly_df['Debit'] = pd.to_numeric(monthly_df['Debit'], errors='coerce').fillna(0)
            st.dataframe(monthly_df[['Date', 'Item', 'Debit']])
        else:
            st.dataframe(monthly_df.iloc[::-1])

    elif page == "🤝 Debt Tracker":
        st.write("Debt Tracker Page")
