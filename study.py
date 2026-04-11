import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Hub", layout="wide")

# ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; }
    .metric-box { background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; margin-top: 10px; border: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        # പേര് മാറ്റം വരുത്തിയ കോളങ്ങൾ വൃത്തിയാക്കുന്നു
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) if any(x in col for x in ['Debit', 'Credit', 'Amount']) else df[col]
        return df
    except: return None

st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("മെനു:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    if df is not None and not df.empty:
        # നിങ്ങളുടെ ഷീറ്റിലെ കോളങ്ങൾ കൃത്യമായി പരിശോധിക്കുന്നു
        debit_total = df['Debit'].sum() if 'Debit' in df.columns else 0
        credit_total = df['Credit'].sum() if 'Credit' in df.columns else 0
        # Amount കോളത്തിൽ ഡാറ്റ ഉണ്ടെങ്കിൽ അത് ഡെബിറ്റ് ആയി കൂട്ടുന്നു
        extra_debit = df['Amount'].sum() if 'Amount' in df.columns else 0
        
        final_debit = debit_total + extra_debit
        balance = credit_total - final_debit
        
        st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-box">വരുമാനം: ₹ {credit_total}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-box">ചിലവ്: ₹ {final_debit}</div>', unsafe_allow_html=True)
    else: st.info("ഡാറ്റ ലോഡ് ചെയ്യുന്നു...")

elif menu == "💰 Add Entry":
    st.title("Add Transaction")
    v_in = speech_to_text(language='ml', key='v')
    with st.form("f", clear_on_submit=True):
        item = st.text_input("Item")
        amt = st.number_input("Amount", min_value=0)
        mode = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        if st.form_submit_button("SAVE"):
            payload = {
                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                "entry.2013476337": item,
                "entry.400506732": str(amt) if mode == "Debit" else "0",
                "entry.1360010991": str(amt) if mode == "Credit" else "0"
            }
            requests.post(FORM_URL_API, data=payload)
            st.success("Saved! ✅")

elif menu == "💬 Logs":
    st.title("Logs")
    df = load_data()
    if df is not None: st.dataframe(df)
