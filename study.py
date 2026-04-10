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

st.set_page_config(page_title="PAICHI AI MULTI", layout="wide")

# 2. Modern Design (Clear & Eye-Friendly)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
    }
    .total-box {
        background: linear-gradient(135deg, #fde047 0%, #eab308 100%);
        color: #000 !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 35px;
        font-weight: 800;
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #fde047 !important; }
    </style>
    """, unsafe_allow_html=True)

# Data Functions
def load_data():
    try:
        url = f"{CSV_URL}&cb={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

def send_data(item, amt):
    payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
    try:
        requests.post(FORM_URL_API, data=payload)
        st.success(f"സേവ് ചെയ്തു: {item} - ₹{amt}")
    except: st.error("Sync Failed")

# Sidebar Menu
st.sidebar.title("🤖 PAICHI AI")
menu = st.sidebar.selectbox("COMMANDS:", ["🏠 Dashboard", "💰 Add Expense", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title(f"Welcome back, Faisal.")
    st.markdown('<div class="glass-card"><h3>System Status: Active 🟢</h3><p>നിന്റെ ചിലവുകളും കടങ്ങളും ഇവിടെ നിയന്ത്രിക്കാം.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD EXPENSE ---
elif menu == "💰 Add Expense":
    st.title("Add New Expense")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("exp_form", clear_on_submit=True):
        item = st.text_input("Item Name", value=v_in if v_in else "")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        if st.form_submit_button("SAVE"):
            if item and amt: send_data(item, amt)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 REPORTS ---
elif menu == "📊 Reports":
    st.title("Expense Intelligence")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Data not found.")

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Tracker (കടങ്ങൾ)")
    if 'debts' not in st.session_state: st.session_state.debts = []
    
    with st.form("debt_form", clear_on_submit=True):
        person = st.text_input("ആർക്കാണ് പണം നൽകാനുള്ളത്?")
        d_amt = st.number_input("എത്ര രൂപ?", min_value=0)
        if st.form_submit_button("Add Debt"):
            if person and d_amt:
                st.session_state.debts.append({"Person": person, "Amount": d_amt})
    
    if st.session_state.debts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        debt_df = pd.DataFrame(st.session_state.debts)
        st.table(debt_df)
        st.write(f"ആകെ കടം: ₹{debt_df['Amount'].sum()}")
        if st.button("Clear All Debts"): 
            st.session_state.debts = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Today's Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    
    new_task = st.text_input("പുതിയ കാര്യം ചേർക്കുക:", placeholder="ഉദാ: Trading പഠിക്കുക...")
    if st.button("Add Task"):
        if new_task:
            st.session_state.tasks.append(new_task)
            st.rerun()
    
    if st.session_state.tasks:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for i, task in enumerate(st.session_state.tasks):
            col1, col2 = st.columns([0.8, 0.2])
            col1.write(f"{i+1}. {task}")
            if col2.button("Done", key=f"task_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("PAICHI AI v11.0")
