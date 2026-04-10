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

st.set_page_config(page_title="PAICHI AI V8", layout="wide")

# 2. Ultra-Deep Dark Design (Gold & Silver)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid #BF953F; }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(191, 149, 63, 0.4);
        margin-bottom: 20px;
    }
    .total-box {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #FCF6BA !important;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        border: 2px solid #BF953F;
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        border: none !important;
    }
    h1, h2, h3 { color: #FCF6BA !important; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&refresh={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center;'>🤖</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("CONTROL CENTER:", ["🏠 Hub", "📥 Data Entry", "📊 Intelligence", "💬 WhatsApp Logs"])

# --- 🏠 HUB ---
if menu == "🏠 Hub":
    st.title("Neural Hub Access")
    st.markdown('<div class="glass-card"><h3>Status: Connected Faisal 🟢</h3><p>നിന്റെ വ്യക്തിഗത AI സിസ്റ്റം ഇപ്പോൾ പൂർണ്ണ സജ്ജമാണ്. ഡാറ്റയിലെ പിശകുകൾ എല്ലാം നീക്കം ചെയ്തിട്ടുണ്ട്.</p></div>', unsafe_allow_html=True)

# --- 📥 DATA ENTRY ---
elif menu == "📥 Data Entry":
    st.title("📥 Neural Ingestion")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("entry_form", clear_on_submit=True):
        item = st.text_input("Object Identity", value=v_in if v_in else "")
        amt = st.number_input("Numerical Value (₹)", min_value=0, value=None)
        if st.form_submit_button("PROCESS & SYNC"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("DATA SYNC SUCCESSFUL")
                except: st.error("CONNECTION FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE (BUG FIXED) ---
elif menu == "📊 Intelligence":
    st.title("📊 Financial Intelligence")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        # ചാർട്ടിലെ പിശക് ഇവിടെ പരിഹരിച്ചു (px.colors.qualitative.Bold ഉപയോഗിക്കുന്നു)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.6, 
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
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
        # WhatsApp എന്ന് തുടങ്ങുന്നതോ ഉള്ളതോ ആയ എൻട്രികൾ മാത്രം കാണിക്കുന്നു
        wa_data = df[df.iloc[:, 1].str.contains('WhatsApp|whatsapp|WA', case=False, na=False)]
        if not wa_data.empty:
            wa_total = wa_data['Amount'].sum()
            st.markdown(f'<div class="total-box" style="font-size:30px; padding:20px;">WA TOTAL: ₹ {wa_total}</div>', unsafe_allow_html=True)
            st.dataframe(wa_data, use_container_width=True)
        else:
            st.info("WhatsApp വിവരങ്ങളൊന്നും ഇപ്പോൾ ലഭ്യമല്ല. ഡാറ്റ എൻട്രിയിൽ 'WhatsApp' എന്ന് ചേർത്ത് നോക്കൂ.")

st.sidebar.write("---")
st.sidebar.write("Core: PAICHI AI v8.0")
