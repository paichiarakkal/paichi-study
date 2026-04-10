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

st.set_page_config(page_title="PAICHI ULTRA AI", layout="wide")

# 2. Premium Neural Design (Modern & Clear)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(160deg, #111827 0%, #1f2937 100%);
        color: #f3f4f6;
    }
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #374151;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
    }
    .total-box {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: #000 !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 35px;
        font-weight: 800;
        box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3);
    }
    .quick-btn {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        background: #374151;
        border-radius: 10px;
        cursor: pointer;
        border: 1px solid #4b5563;
    }
    h1, h2, h3 { color: #fbbf24 !important; }
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

def send_data(item, amt):
    payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
    try:
        requests.post(FORM_URL_API, data=payload)
        st.success(f"Synced: {item} - ₹{amt}")
    except: st.error("Sync Failed")

# Sidebar
st.sidebar.title("🤖 PAICHI AI")
menu = st.sidebar.selectbox("COMMAND:", ["🏠 Home", "📝 Ingestion", "📊 Analytics", "💬 WhatsApp"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    now = datetime.now().hour
    greeting = "Good Morning" if now < 12 else "Good Afternoon" if now < 18 else "Good Evening"
    st.title(f"{greeting}, Faisal.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    if col1.button("☕ Tea (₹10)"): send_data("Tea", 10)
    if col2.button("⛽ Petrol (₹100)"): send_data("Petrol", 100)
    if col3.button("🍲 Food (₹150)"): send_data("Food", 150)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📝 INGESTION ---
elif menu == "📝 Ingestion":
    st.title("Data Entry")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    with st.form("main_form", clear_on_submit=True):
        item = st.text_input("എന്താണ് ചിലവാക്കിയത്?", value=v_in if v_in else "")
        amt = st.number_input("തുക (₹)", min_value=0, value=None)
        if st.form_submit_button("SAVE"):
            if item and amt: send_data(item, amt)

# --- 📊 ANALYTICS ---
elif menu == "📊 Analytics":
    st.title("Intelligence")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        # ബജറ്റ് വാണിംഗ് (ഉദാഹരണത്തിന് 5000 രൂപ)
        if total > 5000:
            st.error("⚠️ ശ്രദ്ധിക്കുക: നീ നിന്റെ ബജറ്റ് (5000) മറികടന്നിരിക്കുന്നു!")
        
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.tail(10), use_container_width=True)

# --- 💬 WHATSAPP ---
elif menu == "💬 WhatsApp":
    st.title("WhatsApp Tracker")
    df = load_data()
    if not df.empty:
        wa_data = df[df.iloc[:, 1].str.contains('WhatsApp|whatsapp|WA', case=False, na=False)]
        if not wa_data.empty:
            st.table(wa_data.tail(10))
        else: st.info("WhatsApp വിവരങ്ങൾ ലഭ്യമല്ല.")

st.sidebar.markdown("---")
st.sidebar.write("PAICHI v10.0")
