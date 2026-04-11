import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI V17.1", layout="wide")

# 2. Design
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%); color: #1e293b; }
    .glass-card { background: white; border-radius: 15px; padding: 20px; border: 1px solid #cbd5e1; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }
    .total-box { background: linear-gradient(135deg, #facc15 0%, #eab308 100%); color: #000 !important; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: 800; }
    .stButton>button { background: #0f172a !important; color: white !important; border-radius: 10px; height: 45px; font-weight: bold; width: 100%; }
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
menu = st.sidebar.selectbox("MENU:", ["🏠 Dashboard", "💰 Add Entry", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Ready, Faisal.")
    st.markdown('<div class="glass-card"><h3>Core Active 🟢</h3><p>എറർ പരിഹരിച്ചു. ഇപ്പോൾ സിസ്റ്റം നോർമൽ ആണ്.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Input")
    target_no = st.text_input("WhatsApp No", value="918714752210")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=False):
        item = st.text_input("Item", value=v_in if v_in else "")
        amt = st.number_input("Amount", min_value=0, value=None)
        submitted = st.form_submit_button("1. SAVE TO CLOUD")
        
        if submitted:
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("Saved!")
                except: st.error("Connection Error")
    
    if item and amt:
        msg = f"📢 *PAICHI REPORT*\n\n📦 Item: {item}\n💰 Amount: ₹{amt}"
        wa_url = f"https://wa.me/{target_no}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer; width:100%;">2. SEND TO WHATSAPP ✅</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 REPORTS ---
elif menu == "📊 Reports":
    st.title("📊 Analysis")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5)
        st.plotly_chart(fig, use_container_width=True)

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debts")
    if 'debts' not in st.session_state: st.session_state.debts = []
    p = st.text_input("Name")
    a = st.number_input("Amt", min_value=0)
    if st.button("Add Debt"):
        if p and a: st.session_state.debts.append({"Person": p, "Amount": a})
    st.table(pd.DataFrame(st.session_state.debts))

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("New Task")
    if st.button("Add"):
        if t: st.session_state.tasks.append(t); st.rerun()
    for task in st.session_state.tasks:
        st.write(f"🔹 {task}")

# --- 💬 LOGS ---
elif menu == "💬 Logs":
    st.title("💬 Expense Logs")
    df = load_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
