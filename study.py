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

# --- 🌗 DARK/LIGHT MODE LOGIC ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# UI Colors based on theme
if st.session_state.theme == 'dark':
    bg_color, text_color, card_bg = "#020617", "#f8fafc", "#1e293b"
else:
    bg_color, text_color, card_bg = "#f8fafc", "#020617", "#ffffff"

st.set_page_config(page_title="PAICHI AI ULTIMATE", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color}; }}
    .glass-card {{ background: {card_bg}; border-radius: 20px; padding: 25px; border: 1px solid #38bdf8; margin-bottom: 20px; color: {text_color}; }}
    .peace-card {{ background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); border-radius: 25px; padding: 30px; text-align: center; color: white; }}
    .stButton>button {{ border-radius: 12px !important; font-weight: bold; width: 100%; height: 50px; }}
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🤖 PAICHI AI")
if st.sidebar.button("🌗 Switch Theme"):
    toggle_theme()
    st.rerun()

menu = st.sidebar.selectbox("MENU:", ["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title(f"Ready, Faisal.")
    st.markdown(f'<div class="glass-card"><h3>Neural Link: {st.session_state.theme.upper()} MODE</h3><p>വോയിസ് കമാൻഡുകളും ഫോട്ടോ ഫീച്ചറും ഇപ്പോൾ ലഭ്യമാണ്.</p></div>', unsafe_allow_html=True)

# --- 🌙 PEACE MODE ---
elif menu == "🌙 Peace Mode":
    st.title("Neural Greeting 🌙")
    st.markdown('<div class="peace-card"><h1>Assalamu Alaikum</h1></div>', unsafe_allow_html=True)
    msg_body = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg_body)}"
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background:#2dd4bf; color:black; border:none; padding:15px; border-radius:12px; cursor:pointer;">SEND 🚀</button></a>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY (Voice & Photo Features) ---
elif menu == "💰 Add Entry":
    st.title("📥 Smart Input")
    
    # Voice Input
    st.write("🎙️ **Voice Command:**")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_input')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("entry_form"):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        
        # Photo Receipt Feature
        st.write("📸 **Photo Receipt:**")
        uploaded_file = st.file_uploader("ബില്ലിന്റെ ഫോട്ടോ എടുക്കുക/അപ്‌ലോഡ് ചെയ്യുക", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("SAVE EVERYTHING"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                requests.post(FORM_URL_API, data=payload)
                st.success(f"'{item}' സേവ് ചെയ്തു!")
                if uploaded_file: st.info("ഫോട്ടോ പ്രോസസ്സ് ചെയ്തു (Local Only)")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Analysis")
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
        except: return pd.DataFrame()
    
    df = load_data()
    if not df.empty:
        st.metric("Total Expenses", f"₹{df['Amount'].sum():,.2f}")
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.4, template="plotly_dark" if st.session_state.theme == 'dark' else "plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# --- 🔴 DEBT & ✅ TO-DO (Simple Versions) ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debts")
    if 'debts' not in st.session_state: st.session_state.debts = []
    d_name = st.text_input("Name")
    d_amt = st.number_input("Amount")
    if st.button("Add"): st.session_state.debts.append({"Name": d_name, "Amount": d_amt})
    st.table(pd.DataFrame(st.session_state.debts))

elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    new_t = st.text_input("New Task")
    if st.button("Add Task"): st.session_state.tasks.append(new_t); st.rerun()
    for t in st.session_state.tasks: st.write(f"🔹 {t}")

elif menu == "💬 Logs":
    st.title("💬 History")
    df = pd.read_csv(CSV_URL)
    st.dataframe(df, use_container_width=True)

st.sidebar.write(f"---")
st.sidebar.write(f"PAICHI AI v25.0 | {st.session_state.theme.upper()}")
