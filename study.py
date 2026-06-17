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

# --- 2. 🎨 PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082, #0D0214); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; width: 100%; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }
    .category-box { background: rgba(255, 255, 255, 0.08); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

def get_category_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        def extract_cat(item_str):
            item_str = str(item_str)
            if 'total' in item_str.lower(): return None
            if ':' in item_str:
                part = item_str.split(':')[0]
                return part.split(']')[1].strip().capitalize() if ']' in part else part.strip().capitalize()
            return "Others"
        df['Extracted_Category'] = df['Item'].apply(extract_cat)
        return df.dropna(subset=['Extracted_Category']).groupby('Extracted_Category')['Debit'].sum().to_dict()
    except: return {}

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C')
        pdf.ln(10)
        cols = df.columns.tolist()
        pdf.set_font("Arial", 'B', 10)
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

def parse_mixed_dates(date_series):
    parsed_dates = []
    for val in date_series:
        val_str = str(val).strip()
        dt = pd.to_datetime(val_str, errors='coerce')
        parsed_dates.append(dt)
    return pd.Series(parsed_dates)

# --- 4. APP MAIN ---
if not st.session_state.auth:
    st.title("🔐 PAICHI EXPENSES LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    t_in, t_out, balance = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:20px; color: #E0B0FF;">Available Balance</span><br>
        <span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    menu_options = ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "🔍 History":
        st.title("Transaction History & Calendar")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df = df[(df['Date'].dt.year == 2026) & (df['Date'].dt.month >= 4)]
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        months = df.sort_values(by='Date', ascending=False)['Month'].unique()

        if len(months) == 0: st.warning("No transactions found!")
        else:
            sel_hist_month = st.selectbox("Select Month for History", months)
            filtered_history = df[df['Month'] == sel_hist_month].copy()
            
            # CALENDAR EVENTS
            events = []
            for _, row in filtered_history.iterrows():
                if pd.notna(row['Date']):
                    events.append({
                        "title": f"{row['Item']}",
                        "start": row['Date'].strftime('%Y-%m-%d'),
                        "color": "#FF4444" if pd.to_numeric(row['Debit'], errors='coerce') > 0 else "#44FF44"
                    })
            calendar(events=events, options={"initialView": "dayGridMonth"})
            
            st.subheader(f"📋 {sel_hist_month} Detailed Transactions")
            st.dataframe(filtered_history.sort_values(by='Date', ascending=False), use_container_width=True)

    # --- മറ്റ് പേജുകൾ (Dashboard, Add Entry, Report, Debt Tracker) പഴയത് പോലെ തന്നെ ചേർക്കുക ---
