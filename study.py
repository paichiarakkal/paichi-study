import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. Settings & Links
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI V18", layout="wide")

# 2. Modern UI Design
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); color: #1e293b; }
    .glass-card { background: white; border-radius: 15px; padding: 20px; border: 1px solid #cbd5e1; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }
    .total-box { background: linear-gradient(135deg, #facc15 0%, #eab308 100%); color: #000 !important; padding: 25px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: 800; }
    .stButton>button { background: #0f172a !important; color: white !important; border-radius: 10px; height: 45px; font-weight: bold; width: 100%; }
    h1, h2, h3 { color: #0f172a !important; }
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
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 PAICHI AI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("MENU:", ["💰 Add Entry", "📊 Expense Tracker", "🔴 Debt Tracker", "✅ To-Do List"])

# --- 💰 ADD ENTRY (Idhilaanu WhatsApp Button ulladhu) ---
if menu == "💰 Add Entry":
    st.title("📥 New Entry")
    
    # Target WhatsApp Number
    target_no = st.text_input("WhatsApp Number", value="918714752210")
    
    v_in = speech_to_text(language='ml', start_prompt="Speak now...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=False):
        item = st.text_input("Item Name", value=v_in if v_in else "")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        save_btn = st.form_submit_button("1. SAVE TO CLOUD")

    if save_btn and item and amt:
        payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
        try:
            requests.post(FORM_URL_API, data=payload)
            st.success("Cloud-il save aayi! Ini WhatsApp-il ayakkam.")
        except: st.error("Cloud Error!")
    
    # Save cheidhu kazhinjal ee button varum
    if item and amt:
        msg = f"📢 *PAICHI AI REPORT*\n\n📅 Date: {datetime.now().strftime('%d-%m-%Y')}\n📦 Item: {item}\n💰 Amount: ₹{amt}\n\n✅ Status: Synced"
        wa_url = f"https://wa.me/{target_no}?text={urllib.parse.quote(msg)}"
        st.markdown(f'''
            <a href="{wa_url}" target="_blank">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px;">
                    2. SEND TO WHATSAPP ✅
                </button>
            </a>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 EXPENSE TRACKER ---
elif menu == "📊 Expense Tracker":
    st.title("📊 All Expenses")
    df = load_data()
    if not df.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    else: st.warning("Data illa!")

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt List")
    if 'debts' not in st.session_state: st.session_state.debts = []
    with st.form("debt_form"):
        p = st.text_input("Person Name")
        a = st.number_input("Amount", min_value=0)
        if st.form_submit_button("Add Debt"):
            if p and a: st.session_state.debts.append({"Person": p, "Amount": a})
    if st.session_state.debts:
        st.table(pd.DataFrame(st.session_state.debts))

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("New Task:")
    if st.button("Add"):
        if
