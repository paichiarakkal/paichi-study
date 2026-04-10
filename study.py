import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ ക്ലൗഡ് ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI GOLD NEURAL AI", layout="wide")

# 2. Advanced Neural Design (Gold & Deep Obsidian)
st.markdown("""
    <style>
    /* Deep Obsidian Background with Radial Glow */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a1a 0%, #000000 100%);
        color: #e0e0e0;
    }
    
    /* Neon Gold Sidebar */
    [data-testid="stSidebar"] {
        background: #050505 !important;
        border-right: 2px solid #BF953F;
    }

    /* Glassmorphism Cards with Neon Border */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(191, 149, 63, 0.3);
        box-shadow: 0 0 15px rgba(191, 149, 63, 0.1);
        margin-bottom: 25px;
    }

    /* Hyper-Premium Gold Box */
    .total-box {
        background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%);
        color: #000 !important;
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        box-shadow: 0 10px 40px rgba(191, 149, 63, 0.5);
        border: 1px solid #ffffff;
        text-transform: uppercase;
    }

    /* Breathing AI Button */
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: #000 !important;
        border-radius: 50px !important;
        padding: 18px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        border: none !important;
        transition: 0.5s all ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.8);
        transform: scale(1.05);
    }

    /* Status Ticker */
    .status-bar {
        background: #BF953F;
        color: #000;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 10px rgba(191, 149, 63, 0.4);
    }

    h1, h2, h3 {
        color: #FCF6BA !important;
        font-family: 'Space Grotesk', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="status-bar">⚡ PAICHI NEURAL CORE ONLINE | UPLOADING DATA TO CLOUD ⚡</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            # തുകയുള്ള കോളം കൃത്യമായി എടുക്കുന്നു
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h2 style='text-align: center; color: #BF953F;'>💎 PAICHI AI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMANDS:", ["🛰️ Overview", "📥 Input Hub", "📈 Intelligence", "🎓 Academy", "⏰ Sync"])

# --- 🛰️ OVERVIEW ---
if menu == "🛰️ Overview":
    st.title("Neural Dashboard")
    st.markdown("""
    <div class="glass-card">
    <h3>Access Granted, Faisal.</h3>
    <p>നിന്റെ വ്യക്തിഗത AI സിസ്റ്റം ഇപ്പോൾ പൂർണ്ണ സജ്ജമാണ്. ഡാറ്റ നൽകാൻ <b>Input Hub</b> തിരഞ്ഞെടുക്കുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 📥 INPUT HUB ---
elif menu == "📥 Input Hub":
    st.title("📥 Data Ingestion")
    st.write("🎤 വോയ്‌സ് നൽകാൻ മൈക്ക് ഉപയോഗിക്കുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening to Faisal...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Object Identity", value=v_in if v_in else "", placeholder="Item name...")
        amt = st.number_input("Numerical Value (₹)", min_value=0, value=None)
        if st.form_submit_button("PROCESS & SYNC"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("DATA TRANSMISSION SUCCESSFUL")
                except: st.error("SYNC FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📈 INTELLIGENCE (ANALYTICS) ---
elif menu == "📈 Intelligence":
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if not st.session_state["auth"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Identity Key", type="password")
        if st.button("VERIFY"):
            if pwd == "1234":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("UNAUTHORIZED ACCESS")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📈 Neural Analytics")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.6, 
                             color_discrete_sequence=["#BF953F", "#FCF6BA", "#B38728", "#E5E4E2"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Activity Data")
                st.dataframe(df.tail(10), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info("Synchronizing Neural Path...")

st.sidebar.write("---")
st.sidebar.write("Version: NEURAL CORE 5.0 GOLD")
