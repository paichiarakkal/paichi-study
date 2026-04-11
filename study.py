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

# 2. Modern AI Design
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%); color: #1e293b; }
    .glass-card { background: rgba(255, 255, 255, 0.8); border-radius: 15px; padding: 20px; border: 1px solid #cbd5e1; margin-bottom: 15px; }
    .total-box { background: linear-gradient(135deg, #facc15 0%, #eab308 100%); color: #000 !important; padding: 25px; border-radius: 15px; text-align: center; font-weight: 800; margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(90deg, #facc15, #eab308) !important; color: #000 !important; border-radius: 12px !important; font-weight: 800 !important; width: 100%; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df.columns = ['Date', 'Item', 'Amount']
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("## 🤖 PAICHI PRO")
menu = st.sidebar.selectbox("COMMANDS:", ["🏠 Dashboard", "💰 Add Entry", "📊 Intelligence", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs & Export"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome, Faisal.")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box"><p style="font-size:14px; margin:0;">TOTAL MONTHLY SPEND</p><h1 style="margin:0;">₹ {total:,.2f}</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><h3>Neural Core Active 🟢</h3><p>സിസ്റ്റം റെഡിയാണ്. ഡാറ്റ നൽകാൻ <b>Add Entry</b> ഉപയോഗിക്കുക.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY (Voice Improved) ---
elif menu == "💰 Add Entry":
    st.title("📥 Smart Data Input")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ... (ഉദാ: ചായ 10)", key='voice')
    
    # വോയ്‌സ് അനാലിസിസ് (പേരും തുകയും വേർതിരിക്കുന്നു)
    auto_item, auto_amt = "", None
    if v_in:
        words = v_in.split()
        for word in words:
            if word.isdigit(): auto_amt = int(word)
            else: auto_item += word + " "
    
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item.strip(), placeholder="Item Name")
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success(f"{item} - ₹{amt} സേവ് ചെയ്തു! ✅")

# --- 📊 INTELLIGENCE (More Graphs) ---
elif menu == "📊 Intelligence":
    st.title("📊 Deep Analysis")
    df = load_data()
    if not df.empty:
        # Pie Chart
        st.subheader("Category Split")
        fig1 = px.pie(df, values='Amount', names='Item', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Bar Chart (Daily Spend)
        st.subheader("Daily Spending Trend")
        daily_df = df.groupby('Date')['Amount'].sum().reset_index()
        fig2 = px.bar(daily_df, x='Date', y='Amount', color_discrete_sequence=['#eab308'])
        st.plotly_chart(fig2, use_container_width=True)

# --- 🔴 DEBT TRACKER (Cloud Save) ---
elif menu == "🔴 Debt Tracker":
    st.title("🔴 Debt Management")
    st.info("ഇവിടെ നൽകുന്ന കടങ്ങൾ ഗൂഗിൾ ഷീറ്റിലേക്ക് 'DEBT' എന്ന പേരിൽ സേവ് ആകും.")
    with st.form("debt_form"):
        p = st.text_input("ആർക്കാണ് പണം നൽകാനുള്ളത്?")
        a = st.number_input("തുക", min_value=0)
        if st.form_submit_button("SAVE DEBT"):
            requests.post(FORM_URL_API, data={"entry.1069832729": "DEBT", "entry.1896057694": p, "entry.1570426033": str(a)})
            st.success("കടം സേവ് ചെയ്തു! 💾")

# --- 💬 LOGS & EXPORT ---
elif menu == "💬 Logs & Export":
    st.title("💬 Data Management")
    df = load_data()
    if not df.empty:
        # Export to CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download as Excel (CSV)", data=csv, file_name=f'paichi_report_{datetime.now().date()}.csv', mime='text/csv')
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI v15.0 PRO | 2026")
