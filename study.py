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

# --- FUNCTIONS ---
def get_data():
    df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df.dropna(subset=['Date'])

def send_whatsapp(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=5)
    except: pass

# --- APP ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "📅 Calendar", "🤝 Debt Tracker"])
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    if page == "📅 Calendar":
        st.title("📅 Transaction Calendar")
        df = get_data()
        events = []
        for _, row in df.iterrows():
            d = pd.to_numeric(row['Debit'], errors='coerce') or 0
            c = pd.to_numeric(row['Credit'], errors='coerce') or 0
            if d > 0: events.append({"title": f"-₹{d:,.0f}", "start": row['Date'].strftime('%Y-%m-%d'), "color": "#FF4444"})
            if c > 0: events.append({"title": f"+₹{c:,.0f}", "start": row['Date'].strftime('%Y-%m-%d'), "color": "#228B22"})
        calendar(events=events, options={"initialView": "dayGridMonth", "height": 600})

    elif page == "🏠 Dashboard":
        st.title("Financial Overview")
        # (Dashboard Logic ഇവിടെ ചേർക്കുക)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry")
        with st.form("entry", clear_on_submit=True):
            it = st.text_input("Description")
            am = st.number_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"])
            if st.form_submit_button("SAVE"):
                send_whatsapp(f"Entry: {it} - ₹{am}")
                st.success("Saved!")

    elif page == "📊 Report":
        st.title("Monthly Report")
        df = get_data()
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        sel = st.selectbox("Select Month", df['Month'].unique())
        monthly_df = df[df['Month'] == sel].copy()
        monthly_df['Debit'] = pd.to_numeric(monthly_df['Debit'], errors='coerce').fillna(0)
        
        if not monthly_df.empty:
            fig = px.pie(monthly_df[monthly_df['Debit'] > 0], values='Debit', names='Item', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    elif page == "🔍 History":
        st.title("Transaction History")
        st.dataframe(get_data().sort_values(by='Date', ascending=False))
