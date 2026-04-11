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

st.set_page_config(page_title="PAICHI AI NEURAL", layout="wide")

# 2. Modern Lighter AI Design (Steel Grey & Gold)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #cbd5e1;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #cbd5e1;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .total-box {
        background: linear-gradient(135deg, #facc15 0%, #eab308 100%);
        color: #000 !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 35px;
        font-weight: 800;
        box-shadow: 0 10px 15px rgba(234, 179, 8, 0.2);
    }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    .stButton>button {
        background: linear-gradient(90deg, #facc15, #eab308) !important;
        color: #000 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: none !important;
        height: 45px;
    }
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

# Sidebar Menu
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 PAICHI AI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMANDS:", 
    ["🏠 Dashboard", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 WhatsApp Logs"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome, Faisal.")
    st.markdown('<div class="glass-card"><h3>Neural Core Active 🟢</h3><p>സിസ്റ്റം സജ്ജമാണ്. ഡാറ്റ നൽകാൻ <b>Add Entry</b> ഉപയോഗിക്കുക.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Input")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=v_in if v_in else "", placeholder="ഉദാ: Food")
        amt = st.number_input("തുക (₹)", min_value=0, value=None)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("സേവ് ചെയ്തു!")
                except: st.error("Error connecting to Cloud")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Intelligence Analysis")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Data not found.")

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Monitoring")
    if 'debts' not in st.session_state: st.session_state.debts = []
    with st.form("debt_form", clear_on_submit=True):
        p = st.text_input("ആർക്കാണ് പണം നൽകാനുള്ളത്?")
        a = st.number_input("തുക", min_value=0)
        if st.form_submit_button("Add Debt"):
            if p and a: st.session_state.debts.append({"Person": p, "Amount": a})
    if st.session_state.debts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.debts))
        if st.button("Clear List"): st.session_state.debts = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Tasks for Today")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("പുതിയ ടാസ്ക് ചേർക്കുക:")
    if st.button("Add Task"):
        if t: st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        c1, c2 = st.columns([0.85, 0.15])
        c1.markdown(f'<div class="glass-card" style="padding:10px;">🔹 {task}</div>', unsafe_allow_html=True)
        if c2.button("X", key=f"t_{i}"):
            st.session_state.tasks.pop(i); st.rerun()

# --- 💬 WHATSAPP LOGS (Updated: All entries show here) ---
elif menu == "💬 WhatsApp Logs":
    st.title("💬 Expense Tracker")
    df = load_data()
    if not df.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        wa_total = df['Amount'].sum()
        st.markdown(f'<div class="total-box" style="font-size:25px; padding:20px;">ആകെ ചിലവ്: ₹ {wa_total:,.2f}</div>', unsafe_allow_html=True)
    else: st.info("വിവരങ്ങൾ ഒന്നും ലഭ്യമല്ല.")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v14.0 | 2026")
