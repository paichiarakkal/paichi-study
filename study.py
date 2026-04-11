import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. നിങ്ങളുടെ കൃത്യമായ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ അപ്ഡേറ്റ്
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .metric-box { background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; margin-bottom: 10px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold !important; border-radius: 12px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5) # 5 സെക്കൻഡ് കൂടുമ്പോൾ ഡാറ്റ പുതുക്കും
def load_data():
    try:
        # Cache ഒഴിവാക്കാൻ റാൻഡം നമ്പർ ചേർക്കുന്നു
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        # സംഖ്യകൾ കൃത്യമായി മാറ്റുന്നു
        for col in df.columns:
            if any(x in col for x in ['Debit', 'Credit', 'Amount']):
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return None

st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("മെനു തിരഞ്ഞെടുക്കുക:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    if df is not None and not df.empty:
        # കോളങ്ങൾ തിരിച്ചറിയുന്നു
        credit_total = df['Credit'].sum() if 'Credit' in df.columns else 0
        debit_total = df['Debit'].sum() if 'Debit' in df.columns else 0
        amount_total = df['Amount'].sum() if 'Amount' in df.columns else 0
        
        final_expense = debit_total + amount_total
        balance = credit_total - final_expense
        
        # ബാലൻസ് ഡിസ്‌പ്ലേ
        st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="metric-box">വരുമാനം: ₹ {credit_total:,.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box">ചിലവ്: ₹ {final_expense:,.2f}</div>', unsafe_allow_html=True)
        
        if st.button("🔄 REFRESH DATA"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.warning("ഷീറ്റിൽ ഡാറ്റയൊന്നുമില്ല. ദയവായി ഒരു എൻട്രി ആഡ് ചെയ്യൂ.")

elif menu == "💰 Add Entry":
    st.title("Smart Data Input")
    v_in = speech_to_text(language='ml', key='voice_v17')
    
    with st.form("main_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്")
        amt = st.number_input("തുക (₹)", min_value=0)
        type_entry = st.radio("തരം:", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                # നിങ്ങൾ അയച്ച ഫോം ഐഡികൾ പ്രകാരം
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.400506732": str(amt) if "Debit" in type_entry else "0",
                    "entry.1360010991": str(amt) if "Credit" in type_entry else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success(f"{item} സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

elif menu == "💬 Logs":
    st.title("Transaction History")
    df = load_data()
    if df is not None:
        st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI PRO v17.0")
