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

st.set_page_config(page_title="PAICHI NEURAL AI", layout="wide")

# 2. Hyper-Futuristic AI Design (Cyber-Glow Theme)
st.markdown("""
    <style>
    /* Neural Dark Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0d1117 0%, #010409 100%);
        color: #c9d1d9;
    }
    
    /* Neon Sidebar */
    [data-testid="stSidebar"] {
        background: #010409 !important;
        border-right: 2px solid #58a6ff;
        box-shadow: 5px 0 15px rgba(88, 166, 255, 0.1);
    }

    /* Floating Glass Card */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid #30363d;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
        transition: 0.3s ease;
    }
    .glass-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.2);
    }

    /* Neural Total Box */
    .total-box {
        background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
        color: #ffffff !important;
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        font-size: 45px;
        font-weight: 800;
        letter-spacing: -1px;
        box-shadow: 0 10px 40px rgba(31, 111, 235, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Neon Cyber Button */
    .stButton>button {
        background: transparent !important;
        color: #58a6ff !important;
        border: 2px solid #58a6ff !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s all;
    }
    .stButton>button:hover {
        background: #58a6ff !important;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(88, 166, 255, 0.6);
        transform: scale(1.02);
    }

    /* AI Status Ticker */
    .ai-ticker {
        background: #238636;
        color: white;
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(35, 134, 54, 0.4);
    }

    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar Setup
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 NEURAL CORE</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMAND:", ["🛰️ Overview", "📥 Data Entry", "📈 Intelligence", "🎓 Academy", "⏰ Sync"])

# --- 🛰️ OVERVIEW ---
if menu == "🛰️ Overview":
    st.markdown('<div class="ai-ticker">SYSTEM STATUS: OPTIMAL</div>', unsafe_allow_html=True)
    st.title("Neural Hub Access")
    st.markdown("""
    <div class="glass-card">
    <h3>Welcome, User: Faisal</h3>
    <p>നിന്റെ ക്ലൗഡ് ഡാറ്റാബേസ് ഇപ്പോൾ സുരക്ഷിതമായി കണക്ട് ചെയ്തിരിക്കുന്നു. വോയ്‌സ് കമാൻഡുകൾ നൽകാൻ <b>Data Entry</b> ഉപയോഗിക്കുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 📥 DATA ENTRY ---
elif menu == "📥 Data Entry":
    st.title("📥 Neural Input")
    st.write("🎤 വോയ്‌സ് റെക്കോർഡിംഗ് ആരംഭിക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening to Neural Path...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Entry Identity", value=v_in if v_in else "", placeholder="Item name...")
        amt = st.number_input("Numerical Value (₹)", min_value=0, value=None)
        if st.form_submit_button("UPLOAD TO NEURAL CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("DATA SYNC SUCCESSFUL")
                except: st.error("SYNC FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📈 INTELLIGENCE (ANALYTICS) ---
elif menu == "📈 Intelligence":
    if "is_auth" not in st.session_state: st.session_state["is_auth"] = False
    if not st.session_state["is_auth"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Security Key", type="password")
        if st.button("VERIFY"):
            if pwd == "1234":
                st.session_state["is_auth"] = True
                st.rerun()
            else: st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📈 Data Intelligence")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.7, 
                             color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Activity Log")
                st.dataframe(df.tail(15), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info("Module Synchronizing...")

st.sidebar.write("---")
st.sidebar.write("Core: PAICHI NEURAL v5.0")
