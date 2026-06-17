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
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def get_data():
    df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month_Year'] = df['Date'].dt.strftime('%B %Y')
    return df

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
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])
    
    if page == "🔍 History":
        st.title("Transaction History")
        df = get_data()
        months = df['Month_Year'].dropna().unique()
        sel_month = st.selectbox("Select Month", months)
        
        filtered_df = df[df['Month_Year'] == sel_month]
        
        # കലണ്ടർ ഇവന്റുകൾ (60633.jpg പോലെ)
        events = []
        for _, row in filtered_df.iterrows():
            if pd.notna(row['Date']):
                debit = pd.to_numeric(row['Debit'], errors='coerce') or 0
                credit = pd.to_numeric(row['Credit'], errors='coerce') or 0
                
                if debit > 0:
                    events.append({"title": f"-₹{debit:,.0f}", "start": row['Date'].strftime('%Y-%m-%d'), "color": "#FF4444"})
                if credit > 0:
                    events.append({"title": f"+₹{credit:,.0f}", "start": row['Date'].strftime('%Y-%m-%d'), "color": "#228B22"})

        # കലണ്ടർ റെൻഡർ ചെയ്യുന്നു
        calendar(events=events, options={
            "initialView": "dayGridMonth",
            "initialDate": pd.to_datetime(sel_month, format='%B %Y').strftime('%Y-%m-01'),
            "headerToolbar": {"left": "prev,next", "center": "title", "right": "today"},
            "height": 600
        })
        
        st.subheader(f"📋 {sel_month} Transactions")
        st.dataframe(filtered_df.sort_values(by='Date', ascending=False), use_container_width=True)

    # ബാക്കി പേജുകൾ (Dashboard, Add Entry, Report, Debt) കൂടി ഇവിടെ ചേർക്കുക...
