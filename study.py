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
MY_NUMBER = "918714752210"

st.set_page_config(page_title="PAICHI PRO ACCOUNTANT", layout="wide")

# --- 🧠 AI LOGIC & THEME ---
if 'theme' not in st.session_state: st.session_state.theme = 'dark'
bg, txt, card = ("#020617", "#f8fafc", "#1e293b") if st.session_state.theme == 'dark' else ("#f8fafc", "#020617", "#ffffff")

st.markdown(f"<style>.stApp {{ background: {bg}; color: {txt}; }} .glass-card {{ background: {card}; border-radius: 15px; padding: 20px; border: 1px solid #38bdf8; margin-bottom: 10px; }}</style>", unsafe_allow_html=True)

def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.title("🤖 PAICHI AI PRO")
menu = st.sidebar.selectbox("MENU:", ["🏠 Dashboard", "🌙 Peace Mode", "💰 Transactions", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List"])

# --- 🏠 DASHBOARD (Balance & Budget) ---
if menu == "🏠 Dashboard":
    st.title("Financial Overview 💹")
    df = load_data()
    
    # കണക്കുകൾ
    total_spent = df['Amount'].sum() if not df.empty else 0
    monthly_budget = 15000  # നിനക്ക് ഇഷ്ടമുള്ള ബജറ്റ് ഇവിടെ നൽകാം
    balance = monthly_budget - total_spent

    col1, col2, col3 = st.columns(3)
    col1.metric("ആകെ ചിലവ്", f"₹{total_spent:,.2f}")
    col2.metric("ബജറ്റ്", f"₹{monthly_budget:,.2f}")
    col3.metric("ബാക്കി", f"₹{balance:,.2f}", delta_color="normal")

    if balance < 1000:
        st.warning("⚠️ ബജറ്റ് തീരാറായി! സൂക്ഷിച്ചു ചിലവാക്കുക.")

    st.markdown('<div class="glass-card"><h3>Smart Notifications</h3><p>ഇന്ന് ചെയ്യാനുള്ള കാര്യങ്ങൾ ടാസ്ക് ലിസ്റ്റിൽ പരിശോധിക്കുക.</p></div>', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif menu == "🌙 Peace Mode":
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<div style="background:linear-gradient(to right, #00c6ff, #0072ff); padding:50px; border-radius:20px; text-align:center;"><h1 style="color:white;">Assalamu Alaikum</h1><br><a href="{wa_url}" target="_blank"><button style="padding:15px 30px; border-radius:10px; border:none; background:white; font-weight:bold; cursor:pointer;">SEND WHATSAPP 🚀</button></a></div>', unsafe_allow_html=True)

# --- 💰 TRANSACTIONS (Income & Expense) ---
elif menu == "💰 Transactions":
    st.title("📥 Add Transaction")
    t_type = st.radio("Type:", ["Expense (ചിലവ്)", "Income (വരവ്)"], horizontal=True)
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_in')
    
    with st.form("trans_form"):
        item = st.text_input("Item/Source", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE TRANSACTION"):
            if item and amt:
                final_item = f"[{t_type}] {item}"
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": final_item, "entry.1570426033": str(amt)}
                requests.post(FORM_URL_API, data=payload)
                st.success(f"{item} സേവ് ചെയ്തു!")

# --- 📊 REPORTS ---
elif menu == "📊 Reports":
    st.title("📊 Financial Analysis")
    df = load_data()
    if not df.empty:
        fig = px.bar(df, x=df.columns[0], y='Amount', color=df.columns[1], title="Daily Expenses")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

# --- 🔴 DEBT & ✅ TO-DO ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Monitoring")
    if 'debts' not in st.session_state: st.session_state.debts = []
    with st.form("debt"):
        n = st.text_input("പേര്"); a = st.number_input("തുക")
        if st.form_submit_button("Add"): st.session_state.debts.append({"Name":n, "Amt":a})
    st.table(pd.DataFrame(st.session_state.debts))

elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("New Task")
    if st.button("Add"): st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        st.write(f"🔹 {task}")

st.sidebar.write("---")
st.sidebar.write("PAICHI PRO v27.0")
