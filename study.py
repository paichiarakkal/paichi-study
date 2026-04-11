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

# 2. Premium AI Design (Lighter Dark & Silver Blue)
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #334155;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 20px;
    }
    .total-box {
        background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 50%, #cbd5e1 100%);
        color: #0f172a !important;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        font-size: 35px;
        font-weight: 900;
        border: 1px solid #ffffff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #facc15, #eab308) !important;
        color: #000 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        border: none !important;
        height: 45px;
    }
    h1, h2, h3 { color: #fde047 !important; }
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
menu = st.sidebar.selectbox("COMMANDS:", 
    ["🏠 Home", "📥 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 WhatsApp Logs"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    st.title(f"Ready to Work, Faisal.")
    st.markdown('<div class="glass-card"><h3>Neural Core Active 🟢</h3><p>സിസ്റ്റം ഇപ്പോൾ ഓൺലൈൻ ആണ്. നിനക്ക് ആവശ്യമുള്ള സെക്ഷൻ സൈഡ്‌ബാർ മെനുവിൽ നിന്നും തിരഞ്ഞെടുക്കാം.</p></div>', unsafe_allow_html=True)

# --- 📥 ADD ENTRY ---
elif menu == "📥 Add Entry":
    st.title("📥 Data Input")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("സാധനത്തിന്റെ പേര്", value=v_in if v_in else "")
        amt = st.number_input("തുക (₹)", min_value=0, value=None)
        if st.form_submit_button("SYNC TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("വിജയകരമായി സേവ് ചെയ്തു!")
                except: st.error("കണക്ഷൻ എറർ!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Intelligence Report")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">NET EXPENSE: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("ഡാറ്റ ലഭ്യമല്ല.")

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Monitoring")
    if 'debts' not in st.session_state: st.session_state.debts = []
    with st.form("debt_form", clear_on_submit=True):
        p = st.text_input("ആർക്കാണ് പണം നൽകാനുള്ളത്?")
        a = st.number_input("എത്ര രൂപ?", min_value=0)
        if st.form_submit_button("Add Debt"):
            if p and a: st.session_state.debts.append({"Person": p, "Amount": a})
    if st.session_state.debts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.debts))
        if st.button("Clear All"): st.session_state.debts = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Today's Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("ചെയ്യേണ്ട കാര്യം ടൈപ്പ് ചെയ്യുക:")
    if st.button("Add Task"):
        if t: st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        col1, col2 = st.columns([0.8, 0.2])
        col1.markdown(f'<div class="glass-card">🔹 {task}</div>', unsafe_allow_html=True)
        if col2.button("Done", key=f"t_{i}"):
            st.session_state.tasks.pop(i); st.rerun()

# --- 💬 WHATSAPP LOGS ---
elif menu == "💬 WhatsApp Logs":
    st.title("💬 WhatsApp Tracker")
    df = load_data()
    if not df.empty:
        wa = df[df.iloc[:, 1].str.contains('WhatsApp|whatsapp|WA', case=False, na=False)]
        if not wa.empty:
            st.dataframe(wa, use_container_width=True)
        else: st.info("WhatsApp എൻട്രികൾ ഒന്നുമില്ല.")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v13.0 | 2026")
