import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI NEURAL", layout="wide")

# 2. Modern AI Glass Design (Lighter Dark & Silver)
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #334155;
    }
    /* AI Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    /* Total Box - Silver Chrome Style */
    .total-box {
        background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 50%, #cbd5e1 100%);
        color: #0f172a !important;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        font-size: 38px;
        font-weight: 900;
        border: 1px solid #ffffff;
        box-shadow: 0 0 20px rgba(148, 163, 184, 0.4);
    }
    .stButton>button {
        background: linear-gradient(90deg, #facc15, #eab308) !important;
        color: #000 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: none !important;
        height: 45px;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(234, 179, 8, 0.4); }
    h1, h2, h3 { color: #fde047 !important; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.title("🤖 PAICHI AI")
menu = st.sidebar.selectbox("System Menu:", 
    ["🏠 Home", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 WhatsApp Logs"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    st.title(f"Hello Faisal,")
    st.markdown('<div class="glass-card"><h3>Neural Core Active 🟢</h3><p>നിന്റെ വ്യക്തിഗത AI സിസ്റ്റം ഇപ്പോൾ പൂർണ്ണ സജ്ജമാണ്. ഡാറ്റ എന്റർ ചെയ്യാൻ മെനു ഉപയോഗിക്കുക.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Ingestion")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("സാധനത്തിന്റെ പേര്", value=v_in if v_in else "")
        amt = st.number_input("തുക (₹)", min_value=0, value=None)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("Successfully Synced!")
                except: st.error("Link Error!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Intelligence Analysis")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
