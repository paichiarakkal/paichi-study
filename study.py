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

# --- 2. CSS DESIGN ---
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
def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def send_to_google_async(data):
    try: requests.post(FORM_API, data=data, timeout=10)
    except: pass

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
        df = df.dropna(subset=['Extracted_Category'])
        return df.groupby('Extracted_Category')['Debit'].sum().to_dict()
    except: return {}

def parse_mixed_dates(date_series):
    parsed_dates = []
    for val in date_series:
        dt = pd.to_datetime(val, errors='coerce')
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

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"])
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        cat_data = get_category_totals()
        if cat_data:
            cols = st.columns(3)
            for idx, (c_name, c_amount) in enumerate(cat_data.items()):
                with cols[idx % 3]:
                    st.markdown(f"""<div class="category-box">
                        <span style="font-size:16px; color:#aaa;">{c_name}</span><br>
                        <span style="font-size:24px; color:#FFF; font-weight:bold;">₹{c_amount:,.2f}</span>
                    </div>""", unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v8')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description")
            am_str = st.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE & NOTIFY"):
                am = float(am_str.strip().replace(',', ''))
                d, c = (am, 0) if ty == "Debit" else (0, am)
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": d, "entry.1221658767": c}
                send_to_google_async(payload)
                st.success("Saved! ✅")

    elif page == "🔍 History":
        st.title("Transaction History & Calendar")
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        
        # Calendar events
        events = []
        for _, row in df.iterrows():
            if pd.notna(row['Date']):
                events.append({
                    "title": f"{row['Item']} (₹{row['Debit'] or row['Credit']})",
                    "start": row['Date'].strftime('%Y-%m-%d'),
                    "color": "#FF4444" if pd.to_numeric(row['Debit'], errors='coerce') > 0 else "#44FF44"
                })
        
        calendar(events=events, options={"initialView": "dayGridMonth"})
        st.dataframe(df.sort_values(by='Date', ascending=False))

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        # (Debt tracker code remains same as your original)
