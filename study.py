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

st.set_page_config(page_title="PAICHI AI PRO", layout="wide")

# 2. Modern AI Design (Steel Grey & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%); color: #1e293b; }
    [data-testid="stSidebar"] { background-color: #f8fafc !important; border-right: 1px solid #cbd5e1; }
    .glass-card { background: rgba(255, 255, 255, 0.8); border-radius: 15px; padding: 20px; border: 1px solid #cbd5e1; margin-bottom: 15px; }
    .total-box { 
        background: linear-gradient(135deg, #facc15 0%, #eab308 100%); 
        color: #000 !important; padding: 25px; border-radius: 15px; 
        text-align: center; font-weight: 800; margin-bottom: 20px; 
    }
    .stButton>button {
        background: linear-gradient(90deg, #facc15, #eab308) !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; width: 100%; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df.columns = ['Date', 'Item', 'Amount']
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# 🧠 വോയ്‌സ് കമാൻഡ് നമ്പറുകളെ തിരിച്ചറിയാൻ
def process_voice(text):
    num_map = {'ഒന്ന്': '1', 'രണ്ട്': '2', 'മൂന്ന്': '3', 'നാല്': '4', 'അഞ്ച്': '5', 
               'ആറ്': '6', 'ഏഴ്': '7', 'എട്ട്': '8', 'ഒൻപത്': '9', 'പത്ത്': '10', 
               'ഇരുപത്': '20', 'അമ്പത്': '50', 'നൂറ്': '100'}
    words = text.split()
    item_parts = []
    amt = None
    for word in words:
        if word.isdigit(): amt = int(word)
        elif word in num_map: amt = int(num_map[word])
        else: item_parts.append(word)
    return " ".join(item_parts), amt

# --- SIDEBAR MENU ---
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 PAICHI AI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMANDS:", 
    ["🏠 Dashboard", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome, Faisal.")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><h3>Neural Core Active 🟢</h3><p>സൈഡ് ബാർ ഉപയോഗിച്ച് പേജുകൾ മാറ്റാം.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Input")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    
    auto_item, auto_amt = "", None
    if v_in:
        auto_item, auto_amt = process_voice(v_in)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item)
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success("സേവ് ചെയ്തു! ✅")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    st.title("📊 Analysis")
    df = load_data()
    if not df.empty:
        st.plotly_chart(px.pie(df, values='Amount', names='Item', hole=0.5), use_container_width=True)
        # Daily Bar Chart
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        daily = df.groupby(df['Date'].dt.date)['Amount'].sum().reset_index()
        st.plotly_chart(px.bar(daily, x='Date', y='Amount', color_discrete_sequence=['#eab308']), use_container_width=True)

# --- 🔴 DEBT TRACKER ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Cloud")
    with st.form("debt"):
        p = st.text_input("Person")
        a = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            requests.post(FORM_URL_API, data={"entry.1069832729": "DEBT", "entry.1896057694": p, "entry.1570426033": str(a)})
            st.success("Saved!")

# --- 💬 LOGS ---
elif menu == "💬 Logs":
    st.title("💬 History")
    df = load_data()
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Excel", data=csv, file_name='report.csv')
        st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI v15.3 | 2026")
