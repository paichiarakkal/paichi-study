import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_calendar import calendar
import urllib.parse

# Config
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI v2.6", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

# ലോഗിൻ സെക്ഷൻ
if not st.session_state.auth:
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth = True
            st.rerun()
else:
    # സൈഡ്ബാർ മെനു
    menu = st.sidebar.radio("Menu", ["🏠 Dashboard", "📅 Calendar", "💰 Add Entry"])
    
    if menu == "🏠 Dashboard":
        st.title("Dashboard")
        # നിങ്ങളുടെ ഡാറ്റാ ലോജിക് ഇവിടെ...

    elif menu == "📅 Calendar":
        st.title("Transaction Calendar")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            events = []
            for _, row in df.iterrows():
                if pd.notna(row['Date']):
                    # തുക കൺവെർട്ട് ചെയ്യുന്നു
                    val = pd.to_numeric(row['Debit'], errors='coerce') or pd.to_numeric(row['Credit'], errors='coerce') or 0
                    events.append({
                        "title": f"₹{val:,.0f}", 
                        "start": row['Date'].strftime('%Y-%m-%d'),
                        "color": "#FF4444" if pd.to_numeric(row['Debit'], errors='coerce') > 0 else "#228B22"
                    })
            
            calendar(events=events, options={"initialView": "dayGridMonth", "height": 600})
        except Exception as e:
            st.error(f"Error loading data: {e}")
