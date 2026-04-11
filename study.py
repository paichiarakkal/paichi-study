import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. സെറ്റിംഗ്സ് & ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

PEACE_NUMBERS = ["918714752210"] # നിനക്ക് മെസ്സേജ് അയക്കേണ്ട നമ്പറുകൾ ഇവിടെ ചേർക്കാം

st.set_page_config(page_title="PAICHI AI V22", layout="wide")

# 2. Premium AI Dark UI Design
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    [data-testid="stSidebar"] { background: #0f172a !important; border-right: 1px solid #1e293b; }
    .glass-card { 
        background: #1e293b; border-radius: 20px; padding: 25px; 
        border: 1px solid #38bdf8; margin-bottom: 20px;
    }
    .peace-card {
        background: linear-gradient(135deg, #2dd4bf 0%, #3b82f6 100%);
        border-radius: 25px; padding: 40px; text-align: center;
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.4); margin-bottom: 25px;
    }
    .stButton>button { 
        background: #3b82f6 !important; color: white !important; 
        border-radius: 12px !important; font-weight: bold; width: 100%; height: 50px;
    }
    h1, h2, h3 { color: #2dd4bf !important; }
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

# സമയം നോക്കി ഓട്ടോമാറ്റിക് മെനു മാറ്റുന്നു
now = datetime.now()
default_menu = "🌙 Peace Mode" if (4 <= now.hour < 5) else "🏠 Dashboard"

# Sidebar
st.sidebar.title("🤖 PAICHI AI")
menu = st.sidebar.selectbox("COMMANDS:", 
    ["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"],
    index=["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"].index(default_menu))

# --- 🌙 PEACE MODE ---
if menu == "🌙 Peace Mode":
    st.title("Neural Greetings 🌙")
    st.markdown('<div class="peace-card"><h1 style="color:white !important; font-size:45px;">Assalamu Alaikum</h1><p style="color:white; opacity:0.9;">AI സന്ദേശം അയക്കാൻ തയ്യാറാണ്</p></div>', unsafe_allow_html=True)
    
    # കളർഫുൾ ആയ AI ലുക്ക് മെസ്സേജ് (ലിങ്കുകൾ ഒന്നുമില്ല)
    msg_body = """
🔵🔴🟢🟡🔵🔴🟢🟡
*ASSALAMU ALAIKUM*
━━━━━━━━━━━━━━━
🤖 *PAICHI AI SYSTEM*
✨ _Neural Greeting Mode_ ✨
━━━━━━━━━━━━━━━
Have a blessed and 
peaceful morning! 🌙
━━━━━━━━━━━━━━━
🚀 *SYSTEM ACTIVE*
🔵🔴🟢🟡🔵🔴🟢🟡
    """
    
    for num in PEACE_NUMBERS:
        wa_url = f"https://wa.me/{num}?text={urllib.parse.quote(msg_body)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background:#2dd4bf; color:#000; padding:15px; border-radius:12px; width:100%; font-weight:bold; cursor:pointer; border:none; margin-bottom:10px;">SEND TO {num} 🚀</button></a>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Ingestion")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form"):
        item = st.text_input("Item", value=v_in if v_in else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("1. SAVE TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                requests.post(FORM_URL_API, data=payload)
                st.success("Saved!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE (REPORT) ---
elif menu == "📊 Intelligence":
    st.title("📊 Analysis")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div style="background:#2dd4bf; color:black; padding:20px; border-radius:15px; text-align:center; font-size:25px; font-weight:bold;">TOTAL: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debts")
    if 'debts' not in st.session_state: st.session_state.debts = []
    p = st.text_input("Name")
    a = st.number_input("Amt", min_value=0)
    if st.button("Add Debt"):
        st.session_state.debts.append({"Person": p, "Amount": a})
    st.table(pd.DataFrame(st.session_state.debts))

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("Task")
    if st.button("Add"):
        st.session_state.tasks.append(t); st.rerun()
    for task in st.session_state.tasks: st.write(f"🔹 {task}")

# --- 💬 LOGS ---
elif menu == "💬 Logs":
    st.title("💬 History")
    df = load_data()
    if not df.empty: st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v22.0")
