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

st.set_page_config(page_title="PAICHI AI LIGHTER", layout="wide")

# 2. Lighter AI Design (Steel Grey & Gold)
st.markdown("""
    <style>
    /* കറുപ്പ് മാറ്റി കുറച്ചുകൂടി തെളിച്ചമുള്ള ചാരനിറം */
    .stApp {
        background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    
    /* സൈഡ്‌ബാർ */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #cbd5e1;
    }

    /* വ്യക്തമായി കാണാൻ കഴിയുന്ന കാർഡുകൾ */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #cbd5e1;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }

    /* Total Box - Premium Gold Style */
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

    h1, h2, h3 {
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }

    /* Input Fields Design */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: white !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
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
        st.success(f"സേവ് ചെയ്തു: {item}")
    except: st.error("Error connecting to Cloud")

# Sidebar Menu
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 PAICHI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMANDS:", ["🏠 Dashboard", "💰 Add Expense", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome, Faisal.")
    st.markdown('<div class="glass-card"><h3>System Ready 🟢</h3><p>ബാക്ക്ഗ്രൗണ്ട് ലൈറ്റ് ആക്കിയ പുതിയ ഡിസൈൻ ആണിത്. ഇപ്പോൾ വിവരങ്ങൾ കൂടുതൽ വ്യക്തമായി കാണാം.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD EXPENSE ---
elif menu == "💰 Add Expense":
    st.title("Add New Expense")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("exp_form", clear_on_submit=True):
        item = st.text_input("Item Name", value=v_in if v_in else "", placeholder="ഉദാ: Petrol")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt: send_data(item, amt)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 REPORTS ---
elif menu == "📊 Reports":
    st.title("Financial Analysis")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, 
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Data not found.")

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("Debt Tracker")
    if 'debts' not in st.session_state: st.session_state.debts = []
    
    with st.form("debt_form", clear_on_submit=True):
        person = st.text_input("പേര്")
        d_amt = st.number_input("തുക (₹)", min_value=0)
        if st.form_submit_button("Add to Debt List"):
            if person and d_amt:
                st.session_state.debts.append({"Person": person, "Amount": d_amt})
    
    if st.session_state.debts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        debt_df = pd.DataFrame(st.session_state.debts)
        st.table(debt_df)
        if st.button("Clear List"): 
            st.session_state.debts = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("Tasks for Today")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    
    new_task = st.text_input("പുതിയ ടാസ്ക് ചേർക്കുക:")
    if st.button("Add"):
        if new_task:
            st.session_state.tasks.append(new_task)
            st.rerun()
    
    if st.session_state.tasks:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for i, task in enumerate(st.session_state.tasks):
            c1, c2 = st.columns([0.85, 0.15])
            c1.write(f"🔹 {task}")
            if c2.button("X", key=f"t_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("PAICHI AI v12.0")
