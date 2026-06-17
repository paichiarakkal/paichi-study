import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import re
import urllib.parse
from streamlit_calendar import calendar

# --- CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE = "971551347989"
WA_API_KEY = "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI EXPENSES v2.6", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- CSS DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082, #0D0214); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_data():
    df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month_Year'] = df['Date'].dt.strftime('%B %Y')
    return df

# --- MAIN APP ---
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
    
    # NAVIGATION
    menu = ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # PAGES
    if page == "🔍 History":
        st.title("Transaction History & Calendar")
        df = get_data()
        months = df['Month_Year'].dropna().unique()
        selected_month = st.selectbox("Select Month", months, index=0)
        filtered_df = df[df['Month_Year'] == selected_month]
        
        # Calendar events
        events = []
        for _, row in filtered_df.iterrows():
            if pd.notna(row['Date']):
                events.append({
                    "title": f"{row['Item']} (₹{row['Debit'] or row['Credit']})",
                    "start": row['Date'].strftime('%Y-%m-%d'),
                    "color": "#FF4444" if pd.to_numeric(row['Debit'], errors='coerce') > 0 else "#44FF44"
                })
        
        calendar(events=events, options={"initialView": "dayGridMonth", "height": 600})
        st.dataframe(filtered_df.sort_values(by='Date', ascending=False))

    elif page == "🏠 Dashboard":
        st.title("Dashboard")
        # ബാക്കി പേജുകൾ ഇവിടെ ഇതേപോലെ കൊടുക്കുക...
