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

st.set_page_config(page_title="PAICHI AI V9", layout="wide")

# 2. Soft Dark AI Design (Silver & Gold Mix)
st.markdown("""
    <style>
    /* കടുത്ത കറുപ്പിന് പകരം തെളിച്ചമുള്ള Deep Grey/Navy */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* സൈഡ്‌ബാർ - Silver Border */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 2px solid #94a3b8;
    }

    /* Glass Card - വ്യക്തമായി കാണാൻ കഴിയുന്ന രീതിയിൽ */
    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(148, 163, 184, 0.3);
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Total Box - Silver to Gold Gradient */
    .total-box {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 50%, #fde047 100%);
        color: #0f172a !important;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        font-size: 40px;
        font-weight: 900;
        box-shadow: 0 10px 30px rgba(253, 224, 71, 0.3);
        border: 2px solid #ffffff;
    }

    /* AI Button - Premium Gold */
    .stButton>button {
        background: linear-gradient(90deg, #facc15, #eab308) !important;
        color: #000000 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: 900 !important;
        border: none !important;
        width: 100%;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(234, 179, 8, 0.5);
    }

    h1, h2, h3 {
        color: #fde047 !important; /* Gold titles */
        font-family: 'Inter', sans-serif;
    }

    /* Input Fields */
    input {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&refresh={random.randint(1, 99999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 PAICHI AI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMAND:", ["🏠 Dashboard", "📥 Input Hub", "📊 Intelligence", "💬 WhatsApp Logs"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Neural Dashboard")
    st.markdown('<div class="glass-card"><h3>System Active Faisal 🟢</h3><p>കണ്ണുകൾക്ക് ആയാസമില്ലാത്ത പുതിയ ഡിസൈൻ സെറ്റ് ചെയ്തിട്ടുണ്ട്. ഡാറ്റ നൽകാൻ <b>Input Hub</b> ഉപയോഗിക്കുക.</p></div>', unsafe_allow_html=True)

# --- 📥 INPUT HUB ---
elif menu == "📥 Input Hub":
    st.title("📥 Data Ingestion")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Entry Identity", value=v_in if v_in else "", placeholder="Item name...")
        amt = st.number_input("Numerical Value (₹)", min_value=0, value=None)
        if st.form_submit_button("PROCESS & SYNC"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("SYNC SUCCESSFUL")
                except: st.error("CONNECTION ERROR")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Intelligence Report")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        # Error ഇല്ലാത്ത Pie Chart
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("Recent Activity Log")
        st.dataframe(df.tail(15), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else: st.warning("ക്ലൗഡിൽ ഡാറ്റയൊന്നും കണ്ടില്ല.")

# --- 💬 WHATSAPP LOGS ---
elif menu == "💬 WhatsApp Logs":
    st.title("💬 WhatsApp Tracker")
    df = load_data()
    if not df.empty:
        wa_data = df[df.iloc[:, 1].str.contains('WhatsApp|whatsapp|WA', case=False, na=False)]
        if not wa_data.empty:
            wa_total = wa_data['Amount'].sum()
            st.markdown(f'<div class="total-box" style="font-size:30px; padding:20px;">WA SPENT: ₹ {wa_total}</div>', unsafe_allow_html=True)
            st.dataframe(wa_data, use_container_width=True)
        else:
            st.info("WhatsApp വിവരങ്ങളൊന്നും ഇപ്പോൾ ലഭ്യമല്ല.")

st.sidebar.write("---")
st.sidebar.write("Core: PAICHI AI v9.0")
