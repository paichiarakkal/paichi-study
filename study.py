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

st.set_page_config(page_title="PAICHI PRO V30", layout="wide")

# --- 🧠 NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# --- 🌗 PREMIUM DARK UI ---
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    [data-testid="stSidebar"] { background: #0f172a !important; padding-top: 20px; }
    .stRadio > div { gap: 15px; } /* സൈഡ്ബാറിലെ ഓപ്ഷനുകൾ തമ്മിൽ ഗ്യാപ്പ് വരാൻ */
    label[data-testid="stWidgetLabel"] { font-size: 20px !important; color: #38bdf8 !important; }
    .glass-card { background: #1e293b; border-radius: 20px; padding: 25px; border: 1px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Menu
st.sidebar.markdown("<h1 style='text-align: center; color: #38bdf8;'>🤖 PAICHI</h1>", unsafe_allow_html=True)
menu_options = ["🏠 Dashboard", "🌙 Peace Mode", "💰 Transactions", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List"]
st.session_state.page = st.sidebar.radio("CHOOSE ACTION:", menu_options, index=menu_options.index(st.session_state.page))

# --- 🏠 DASHBOARD ---
if st.session_state.page == "🏠 Dashboard":
    st.title("Financial Overview 💹")
    
    # കണക്കുകൾ ലോഡ് ചെയ്യുന്നു
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total_spent = df['Amount'].sum()
    except:
        total_spent = 0

    st.markdown(f'''
        <div class="glass-card">
            <p style="color: #94a3b8; margin: 0;">Total Spent This Month</p>
            <h1 style="color: #2dd4bf; margin: 0; font-size: 45px;">₹ {total_spent:,.2f}</h1>
        </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    st.info("ഇടതുവശത്തെ മെനു ഉപയോഗിച്ച് മറ്റ് സെക്ഷനുകളിലേക്ക് പോകാം.")

# --- 🌙 PEACE MODE ---
elif st.session_state.page == "🌙 Peace Mode":
    st.title("Neural Greeting 🌙")
    msg = "🔵🔴🟢🟡🔵🔴🟢🟡\n*ASSALAMU ALAIKUM*\n━━━━━━━━━━━━━━\n🔵🔴🟢🟡🔵🔴🟢🟡"
    wa_url = f"https://wa.me/{MY_NUMBER}?text={urllib.parse.quote(msg)}"
    
    st.markdown(f'''
        <div style="background: linear-gradient(135deg, #0ea5e9, #2563eb); padding: 50px; border-radius: 25px; text-align: center;">
            <h1 style="color: white !important;">Assalamu Alaikum</h1>
            <p style="color: white; opacity: 0.8;">സന്ദേശം അയക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക</p>
            <br>
            <a href="{wa_url}" target="_blank">
                <button style="background: #facc15; border: none; padding: 15px 40px; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 18px;">SEND 🚀</button>
            </a>
        </div>
    ''', unsafe_allow_html=True)

# --- 💰 TRANSACTIONS ---
elif st.session_state.page == "💰 Transactions":
    st.title("Add Transaction 📥")
    v_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_in')
    
    with st.form("entry_form"):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success("സേവ് ചെയ്തു!")

# --- 📊 REPORTS ---
elif st.session_state.page == "📊 Reports":
    st.title("Reports 📊")
    try:
        df = pd.read_csv(CSV_URL)
        st.plotly_chart(px.pie(df, values=df.columns[-1], names=df.columns[1], hole=0.4))
        st.dataframe(df, use_container_width=True)
    except:
        st.error("ഡാറ്റ ലഭ്യമല്ല.")

# --- 🔴 DEBT & ✅ TO-DO (ഇവയും സൈഡ്ബാർ വഴി ആക്സസ് ചെയ്യാം) ---
elif st.session_state.page == "🔴 Debt Tracker":
    st.title("Debt Monitoring 🔴")
    st.info("കടങ്ങൾ ഇവിടെ രേഖപ്പെടുത്താം.")

elif st.session_state.page == "✅ To-Do List":
    st.title("Tasks 📝")
    st.info("ചെയ്യേണ്ട കാര്യങ്ങൾ ഇവിടെ രേഖപ്പെടുത്താം.")

st.sidebar.write("---")
st.sidebar.caption(f"PAICHI AI PRO v30.0 | {datetime.now().strftime('%Y')}")
