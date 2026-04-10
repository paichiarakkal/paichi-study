import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ക്ലൗഡ് കണക്ഷൻ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI CORE", layout="wide")

# 2. Futuristic Gold & Silver AI Styling
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് - Gold & Silver Gradient */
    .stApp {
        background: radial-gradient(circle at top left, #2c2c2c, #000000);
        background-attachment: fixed;
        color: #e0e0e0;
    }
    
    /* സൈഡ്‌ബാർ */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.95) !important;
        border-right: 2px solid #BF953F;
    }

    /* AI Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 30px;
        border: 1px solid rgba(192, 192, 192, 0.2); /* Silver border */
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }

    /* Total Box - Premium Gold & Silver Mix */
    .total-box {
        background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 20%, #C0C0C0 50%, #FCF6BA 80%, #B38728 100%);
        color: #000 !important;
        padding: 45px;
        border-radius: 20px;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        box-shadow: 0 0 40px rgba(191, 149, 63, 0.4);
        border: 1px solid #ffffff;
        letter-spacing: -1px;
    }

    /* Cyber Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #C0C0C0, #BF953F) !important; /* Silver to Gold */
        color: #000 !important;
        border-radius: 12px !important;
        padding: 18px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border: none !important;
        width: 100%;
        transition: 0.5s all;
    }
    .stButton>button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(191, 149, 63, 0.6);
    }

    /* Ticker / Status */
    .status-line {
        background: rgba(191, 149, 63, 0.1);
        border: 1px solid #BF953F;
        color: #FCF6BA;
        padding: 10px;
        border-radius: 50px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
    }

    h1, h2, h3 {
        color: #FCF6BA !important;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 0 10px rgba(191, 149, 63, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="status-line">💎 PAICHI NEURAL CORE v5.0 | GOLD-SILVER HYBRID INTERFACE 💎</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center; color: #BF953F;'>🤖 PAICHI</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("System Commands:", ["🏠 Dashboard", "📥 Data Input", "📊 Analytics", "🎓 Academy", "⏰ Sync"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Neural Access Granted")
    st.markdown("""
    <div class="glass-card">
    <h3>System Online, Faisal.</h3>
    <p>നിന്റെ ക്ലൗഡ് നെറ്റ്വർക്ക് ഇപ്പോൾ ഗോൾഡ്-സിൽവർ ഹൈബ്രിഡ് മോഡലിൽ പ്രവർത്തിക്കുന്നു. ഡാറ്റ കൈകാര്യം ചെയ്യാൻ മെനു ഉപയോഗിക്കുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 📥 DATA INPUT ---
elif menu == "📥 Data Input":
    st.title("📥 Data Ingestion")
    st.write("🎤 വോയ്‌സ് നൽകാൻ മൈക്ക് ഉപയോഗിക്കുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening to Neural Path...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Entry Identity", value=v_in if v_in else "", placeholder="Item name...")
        amt = st.number_input("Numerical Value (₹)", min_value=0, value=None)
        if st.form_submit_button("UPLOAD TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("SYNC SUCCESSFUL")
                except: st.error("SYNC FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 ANALYTICS ---
elif menu == "📊 Analytics":
    if "is_auth" not in st.session_state: st.session_state["is_auth"] = False
    if not st.session_state["is_auth"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Access Key", type="password")
        if st.button("DECRYPT"):
            if pwd == "1234":
                st.session_state["is_auth"] = True
                st.rerun()
            else: st.error("UNAUTHORIZED ACCESS")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📊 Intelligence Report")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.6, 
                             color_discrete_sequence=["#BF953F", "#C0C0C0", "#808080", "#E5E4E2"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Activity Data")
                st.dataframe(df.tail(15), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info("System Synchronizing...")

st.sidebar.write("---")
st.sidebar.write("Core: PAICHI AI v5.0")
