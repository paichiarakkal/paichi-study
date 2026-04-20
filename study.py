import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GLASS v14.0", layout="wide")
st_autorefresh(interval=30000, key="auto_refresh")

# --- 2. 🎨 PREMIUM GLASS DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1A0521 0%, #4B0082 50%, #1A0521 100%); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.7) !important; backdrop-filter: blur(15px) !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    .glass-card { background: rgba(255, 255, 255, 0.07); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); text-align: center; margin-bottom: 20px; }
    .balance-card { background: rgba(255, 215, 0, 0.1); border: 1px solid #FFD700; padding: 15px; border-radius: 15px; margin-bottom: 20px; text-align: center; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stButton>button { background: linear-gradient(90deg, #FFD700, #FFA500); color: #000; border-radius: 12px; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. FUNCTIONS ---
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        # തീയതി ഫോർമാറ്റ് നിർബന്ധമായും D/M/Y ആക്കി മാറ്റുന്നു
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
        return df
    except: return None

def calculate_balance(df):
    if df is not None:
        # നമ്പറുകളാണെന്ന് ഉറപ്പുവരുത്തുന്നു
        cr = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        db = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return cr - db
    return 0

# --- 4. APP LOGIC ---
if not st.session_state.auth:
    st.title("🔐 PAICHI FINANCE")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p: st.session_state.auth, st.session_state.user = True, u; st.rerun()
else:
    user = st.session_state.user
    df = load_data()
    bal = calculate_balance(df)
    
    if user == "shabana": page = "💰 Add Entry"
    else: page = st.sidebar.radio("Menu", ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "🔍 History"])

    if page == "💰 Add Entry":
        st.title("Transaction Entry")
        st.markdown(f'<div class="balance-card"><h3>Total Balance</h3><h1 style="color:#FFD700 !important; margin:0;">₹{bal:,.0f}</h1></div>', unsafe_allow_html=True)
        v = speech_to_text(language='ml', key='v')
        with st.form("entry_form"):
            it = st.text_input("Details", value=v if v else "")
            am = st.number_input("Amount", min_value=1, value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE TO SHEET"):
                if it and am:
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    # സേവ് ചെയ്യുമ്പോൾ ഇന്ത്യൻ ഫോർമാറ്റിൽ സേവ് ചെയ്യുന്നു
                    requests.post(FORM_API, data={
                        "entry.1044099436": datetime.now().strftime("%d/%m/%Y"), 
                        "entry.2013476337": f"[{user.capitalize()}] {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    })
                    st.success("സേവ് ചെയ്തു! ✅"); st.rerun()

    elif page == "🔍 History":
        st.title("History")
        if df is not None:
            # പുതിയ എൻട്രികൾ മുകളിൽ വരാൻ വേണ്ടി സോർട്ട് ചെയ്യുന്നു
            st.dataframe(df.iloc[::-1], use_container_width=True)

    # ബാക്കി പേജുകൾ (Advisor, Dashboard) പഴയതുപോലെ തുടരും...
    elif page == "📊 Advisor":
        st.title("Smart Advisor")
        st.write("ഈ സെക്ഷൻ റെഡി ആയി വരുന്നു...")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
