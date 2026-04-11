import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകളും സെറ്റിംഗ്സും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

# നിന്റെ വാട്സ്ആപ്പ് നമ്പറുകൾ ഇവിടെ നൽകാം
MY_NUMBER = "918714752210"
PEACE_NUMBERS = ["918714752210"] # കൂടുതൽ നമ്പറുകൾ വേണമെങ്കിൽ ["91...", "91..."] ഇങ്ങനെ നൽകാം

st.set_page_config(page_title="PAICHI AI ULTIMATE", layout="wide")

# 2. Premium Neural Design (Dark & Cyan)
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background: #1e293b !important; border-right: 1px solid #334155; }
    .glass-card { 
        background: rgba(30, 41, 59, 0.7); 
        border-radius: 20px; 
        padding: 25px; 
        border: 1px solid rgba(56, 189, 248, 0.3); 
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .peace-card {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        border-radius: 25px;
        padding: 40px;
        text-align: center;
        color: white;
        box-shadow: 0 0 30px rgba(14, 165, 233, 0.4);
        margin-bottom: 25px;
    }
    .total-box { 
        background: #facc15; color: #000 !important; 
        padding: 25px; border-radius: 15px; 
        text-align: center; font-size: 30px; font-weight: 900; 
    }
    .stButton>button { 
        background: #38bdf8 !important; color: #0f172a !important; 
        border-radius: 12px !important; font-weight: bold; width: 100%;
        height: 50px; border: none !important;
    }
    h1, h2, h3 { color: #38bdf8 !important; }
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

# Sidebar Navigation
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 PAICHI AI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMANDS:", 
    ["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title(f"Ready, Faisal.")
    st.markdown('<div class="glass-card"><h3>Neural Link Active 🟢</h3><p>എല്ലാ സിസ്റ്റങ്ങളും സജ്ജമാണ്. നിന്റെ വ്യക്തിഗത AI അസിസ്റ്റന്റ് ഇപ്പോൾ ഓൺലൈൻ ആണ്.</p></div>', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif menu == "🌙 Peace Mode":
    st.title("Morning Peace 🌙")
    st.markdown(f"""
        <div class="peace-card">
            <div style="font-size: 40px; font-weight: 900; margin-bottom: 10px;">Assalamu Alaikum</div>
            <p style="opacity: 0.9;">സമയത്തിന് മെസ്സേജ് അയക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക</p>
        </div>
    """, unsafe_allow_html=True)
    
    msg = "Assalamu Alaikum ✨"
    for num in PEACE_NUMBERS:
        wa_url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background:#facc15; color:#000; border:none; padding:15px; border-radius:12px; width:100%; font-weight:bold; cursor:pointer; margin-bottom:10px;">SEND GREETING TO {num} 🚀</button></a>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Input")
    target_wa = st.text_input("WhatsApp Sync No:", value=MY_NUMBER)
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=False):
        item = st.text_input("ഐറ്റം പേര്", value=v_in if v_in else "")
        amt = st.number_input("തുക (₹)", min_value=0, value=None)
        if st.form_submit_button("1. SAVE TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("Cloud-ലേക്ക് സേവ് ചെയ്തു!")
                except: st.error("Error!")
    
    if item and amt:
        report = f"📢 *PAICHI REPORT*\n\n📦 Item: {item}\n💰 Amount: ₹{amt}"
        wa_url = f"https://wa.me/{target_wa}?text={urllib.parse.quote(report)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:15px; border-radius:12px; width:100%; font-weight:bold; cursor:pointer;">2. SYNC TO WHATSAPP ✅</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Analysis")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Monitoring")
    if 'debts' not in st.session_state: st.session_state.debts = []
    with st.form("debt_form", clear_on_submit=True):
        p = st.text_input("പേര്")
        a = st.number_input("തുക", min_value=0)
        if st.form_submit_button("Add Debt"):
            if p and a: st.session_state.debts.append({"Person": p, "Amount": a})
    if st.session_state.debts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.debts))
        if st.button("Clear All"): st.session_state.debts = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✅ TO-DO LIST ---
elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("പുതിയ ടാസ്ക്:")
    if st.button("Add"):
        if t: st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        c1, c2 = st.columns([0.85, 0.15])
        c1.markdown(f'<div class="glass-card" style="padding:10px;">🔹 {task}</div>', unsafe_allow_html=True)
        if c2.button("X", key=f"t_{i}"):
            st.session_state.tasks.pop(i); st.rerun()

# --- 💬 LOGS ---
elif menu == "💬 Logs":
    st.title("💬 Expense History")
    df = load_data()
    if not df.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v19.0 | 2026")
