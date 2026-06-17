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

# --- HELPER FUNCTIONS ---
def get_data():
    df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # എല്ലാ മാസവും കിട്ടാൻ ഫിൽട്ടർ ലളിതമാക്കി
    df = df.dropna(subset=['Date'])
    df['Month_Year'] = df['Date'].dt.strftime('%B %Y')
    return df

# --- MAIN APP ---
# (Login logic here...)

# --- HISTORY PAGE ---
if page == "🔍 History":
    st.title("Transaction History & Calendar")
    df = get_data()
    
    # മാസങ്ങൾ ലിസ്റ്റ് ചെയ്യുന്നു
    months = df['Month_Year'].dropna().unique()
    selected_month = st.selectbox("Select Month", months)
    
    # തിരഞ്ഞെടുത്ത മാസത്തെ മാത്രം ഫിൽട്ടർ ചെയ്യുന്നു
    filtered_df = df[df['Month_Year'] == selected_month]
    
    # കലണ്ടർ മാറാൻ തിരഞ്ഞെടുത്ത മാസത്തിന്റെ ആദ്യ തീയതി എടുക്കുന്നു
    first_date_of_month = pd.to_datetime(selected_month, format='%B %Y').strftime('%Y-%m-01')

    # Calendar events
    events = []
    for _, row in filtered_df.iterrows():
        events.append({
            "title": f"{row['Item']} (₹{row['Debit'] or row['Credit']})",
            "start": row['Date'].strftime('%Y-%m-%d'),
            "color": "#FF4444" if pd.to_numeric(row['Debit'], errors='coerce') > 0 else "#44FF44"
        })
    
    # കലണ്ടർ ഓപ്ഷനുകൾ
    calendar_options = {
        "initialView": "dayGridMonth",
        "initialDate": first_date_of_month,
        "height": 500
    }
    
    calendar(events=events, options=calendar_options)
    
    st.subheader(f"📋 {selected_month} Detailed Transactions")
    st.dataframe(filtered_df.sort_values(by='Date', ascending=False), use_container_width=True)
