import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import urllib.parse, threading, base64
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"

# നിങ്ങളുടെ പുതിയ ലിങ്ക് ഇവിടെ ചേർത്തു
SCRIPT_API = "https://script.google.com/macros/s/AKfycbzmbiWOQ-vpyOtaM6n4fosAkHRIaXyno-JyGPbxG9uZIl4W-6QzFy3hVVb-o7ctD7hl/exec"

WA_PHONE, WA_API_KEY = "+971551347989", "7463030"
IMGBB_API_KEY = "7b08945ff15a43258cc137387e6038d5" 
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI PRO", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. UTILITY ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def send_wa(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except: pass

# --- 3. UI & AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🚀 PAICHI AI PRO")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOG IN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    df_main = get_data()
    balance = pd.to_numeric(df_main['Credit'], errors='coerce').fillna(0).sum() - pd.to_numeric(df_main['Debit'], errors='coerce').fillna(0).sum() if not df_main.empty else 0
    
    st.metric("BALANCE", f"₹{balance:,.2f}")

    page = st.sidebar.radio("Menu", ["💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        with st.form("entry_fm", clear_on_submit=True):
            it = st.text_input("Item Name")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE"):
                if it and am_input:
                    am = float(am_input)
                    # പുതിയ ലിങ്ക് വഴി ഡാറ്റ അയക്കുന്നു
                    text_p = f"[{curr_user.capitalize()}] {it} {am} {ty[0].lower()}"
                    res = requests.get(f"{SCRIPT_API}?text={urllib.parse.quote(text_p)}")
                    
                    if res.status_code == 200:
                        st.success(f"Saved: {it}")
                        threading.Thread(target=send_wa, args=(f"✅ Saved: {it} - ₹{am}",)).start()
                        st.rerun()
                    else:
                        st.error("Error connecting to Sheet!")
