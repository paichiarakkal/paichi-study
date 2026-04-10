import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ പുതിയ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI CYBER AI", layout="wide")

# 2. Futuristic Cyber AI Design
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് - Deep Space Black */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #050505 100%);
        color: #ffffff;
    }
    
    /* സൈഡ്ബാർ - Neon Border */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid #BF953F;
    }

    /* AI Glass Card - Neon Glow */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(191, 149, 63, 0.4);
        box-shadow: 0 0 20px rgba(191, 149, 63, 0.1);
        margin-bottom: 25px;
    }

    /* Total Box - Neon Gold/Silver Gradient */
    .total-box {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #FCF6BA !important;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        border: 2px solid #BF953F;
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.3);
        margin: 20px 0;
        text-shadow: 0 0 10px rgba(252, 246, 186, 0.5);
    }

    /* AI Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 18px !important;
        font-weight: 900 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: 0.5s;
    }
    .stButton>button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(191, 149, 63, 0.5);
    }

    /* Ticker - Cyber Line */
    .ticker-wrap {
        background: #BF953F;
        color: #000;
        padding: 12px;
        font-weight: 900;
        border-radius: 5px;
        text-align: center;
        box-shadow: 0 0 15px rgba(191, 149, 63, 0.4);
        margin-bottom: 30px;
    }

    h1, h2, h3 {
        color: #FCF6BA !important;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
    }

    /* Inputs */
    input {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid #BF953F !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="ticker-wrap">⚡ SYSTEM CONNECTED: PAICHI AI CORE V4.0 ⚡</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center; font-size: 40px;'>👾</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMAND CENTER:", ["🏠 Dashboard", "💰 Add Data", "📊 Analytics", "🎓 SSLC", "🎓 Plus Two", "⏰ Alerts"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome Faisal.")
    st.markdown("""
    <div class="glass-card">
    <h3 style="color: #BF953F !important;">AI Status: Optimal 🔵</h3>
    <p>നിന്റെ എല്ലാ സാമ്പത്തിക വിവരങ്ങളും ഇവിടെ സുരക്ഷിതമാണ്. ഡാറ്റ സിങ്ക് ചെയ്യാൻ <b>Add Data</b> ഉപയോഗിക്കുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 💰 ADD DATA ---
elif menu == "💰 Add Data":
    st.title("🧬 Neural Entry")
    st.write("🎤 Voice input active:")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("ai_cyber_form", clear_on_submit=True):
        item = st.text_input("Entry Name", value=v_in if v_in else "")
        amt = st.number_input("Value (₹)", min_value=0, value=None)
        if st.form_submit_button("EXECUTE SYNC"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("SYNC COMPLETE")
                except: st.error("CONNECTION ERROR")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 ANALYTICS ---
elif menu == "📊 Analytics":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    if not st.session_state["unlocked"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Master Key", type="password")
        if st.button("DECRYPT"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📊 Data Visualization")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.6, 
                             color_discrete_sequence=["#BF953F", "#FCF6BA", "#808080", "#333333"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.dataframe(df.tail(15), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info("System Updating...")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI HUB v4.0")
