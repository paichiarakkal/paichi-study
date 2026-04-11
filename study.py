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
MY_NUMBER = "918714752210"

# --- 🧠 AI CATEGORIZATION LOGIC ---
def get_category(item):
    food_items = ['tea', 'coffee', 'food', 'biriyani', 'snacks', 'ചായ', 'ഭക്ഷണം', 'കടി']
    travel_items = ['petrol', 'diesel', 'bus', 'taxi', 'auto', 'പെട്രോൾ', 'യാത്ര']
    item_lower = item.lower()
    if any(x in item_lower for x in food_items): return "🍔 Food"
    elif any(x in item_lower for x in travel_items): return "🚗 Travel"
    else: return "📦 Others"

# --- 🌗 THEME SETUP ---
if 'theme' not in st.session_state: st.session_state.theme = 'dark'
bg, txt, card = ("#020617", "#f8fafc", "#1e293b") if st.session_state.theme == 'dark' else ("#f8fafc", "#020617", "#ffffff")

st.set_page_config(page_title="PAICHI AI V26", layout="wide")
st.markdown(f"<style>.stApp {{ background: {bg}; color: {txt}; }} .glass-card {{ background: {card}; border-radius: 20px; padding: 20px; border: 1px solid #38bdf8; margin-bottom: 15px; }} .stButton>button {{ border-radius: 12px; font-weight: bold; width: 100%; }}</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🤖 PAICHI AI")
if st.sidebar.button("🌗 Switch Theme"):
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    st.rerun()

menu = st.sidebar.selectbox("MENU:", ["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"])

# --- 🏠 DASHBOARD (With Smart Reminders) ---
if menu == "🏠 Dashboard":
    st.title(f"Ready, Faisal.")
    # Smart Reminder Logic
    if 'tasks' in st.session_state and st.session_state.tasks:
        st.markdown(f'<div style="background: rgba(250, 204, 21, 0.2); padding: 15px; border-radius: 15px; border: 1px solid #facc15; margin-bottom: 20px;">⚠️ <b>Smart Reminder:</b> നിനക്ക് ഇന്ന് {len(st.session_state.tasks)} കാര്യങ്ങൾ ചെയ്യാനുണ്ട്!</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card"><h3>System Active 🟢</h3><p>AI Categorization & Smart Reminders ഇപ്പോൾ വർക്കിംഗ്‌ ആണ്.</p></div>', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif menu == "🌙 Peace Mode":
    st.title("Neural Greeting 🌙")
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<div style="background: linear-gradient(135deg, #0ea5e9, #2563eb); padding: 40px; border-radius: 25px; text-align: center; color: white;"><h1>Assalamu Alaikum</h1><br><a href="{wa_url}" target="_blank"><button style="background:#facc15; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">SEND TO WHATSAPP 🚀</button></a></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY (Smart AI Ingestion) ---
elif menu == "💰 Add Entry":
    st.title("📥 Smart Input")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_in')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("smart_form"):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        uploaded_file = st.file_uploader("📸 Receipt (Optional)", type=['jpg','png'])
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                cat = get_category(item)
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": f"{item} ({cat})", "entry.1570426033": str(amt)}
                requests.post(FORM_URL_API, data=payload)
                st.success(f"സേവ് ചെയ്തു! Category: {cat}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Analysis")
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        st.metric("Total Expenses", f"₹{df['Amount'].sum():,.2f}")
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.4, template="plotly_dark" if st.session_state.theme == 'dark' else "plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    except: st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

# --- 🔴 DEBT & ✅ TO-DO ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debts")
    if 'debts' not in st.session_state: st.session_state.debts = []
    p = st.text_input("Name"); a = st.number_input("Amount")
    if st.button("Add"): st.session_state.debts.append({"Name": p, "Amount": a})
    st.table(pd.DataFrame(st.session_state.debts))

elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("New Task")
    if st.button("Add Task"): st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        c1, c2 = st.columns([0.9, 0.1])
        c1.write(f"🔹 {task}")
        if c2.button("X", key=f"del_{i}"): st.session_state.tasks.pop(i); st.rerun()

elif menu == "💬 Logs":
    st.title("💬 History")
    try:
        df = pd.read_csv(CSV_URL)
        st.dataframe(df, use_container_width=True)
    except: st.write("No logs found.")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v26.0")
