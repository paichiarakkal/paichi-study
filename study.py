import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .metric-box { background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; margin-bottom: 10px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold !important; border-radius: 12px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        # സംഖ്യകൾ ക്ലീൻ ചെയ്യുന്നു
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("മെനു:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    if df is not None and not df.empty:
        # ഷീറ്റിലെ ഓരോ വരിയും പരിശോധിച്ച് വരുമാനവും ചിലവും വേർതിരിക്കുന്നു
        total_income = 0
        total_expense = 0
        
        income_keywords = ['salary', 'Salary', 'credit', 'Credit', 'വരുമാനം', 'ലാഭം', 'profit', 'Advance']
        
        for index, row in df.iterrows():
            item_name = str(row['Item']) if 'Item' in df.columns else ""
            amt = row['Amount'] if 'Amount' in df.columns else 0
            deb = row['Debit'] if 'Debit' in df.columns else 0
            cre = row['Credit'] if 'Credit' in df.columns else 0
            
            # വരുമാനം കൂട്ടുന്നു
            if any(key in item_name for key in income_keywords) or cre > 0:
                total_income += (amt + cre)
            else:
                total_expense += (amt + deb)
        
        balance = total_income - total_expense
        
        st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box">ആകെ വരുമാനം: ₹ {total_income:,.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box">ആകെ ചിലവ്: ₹ {total_expense:,.2f}</div>', unsafe_allow_html=True)
        
        if st.button("🔄 REFRESH"):
            st.cache_data.clear()
            st.rerun()

elif menu == "💰 Add Entry":
    st.title("Smart Data Input")
    v_in = speech_to_text(language='ml', key='voice_input')
    with st.form("entry_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്")
        amt = st.number_input("തുക (₹)", min_value=0)
        type_entry = st.radio("തരം:", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                # Credit ഐഡി ഷീറ്റിലെ ശരിയായ കോളത്തിലേക്ക് അയക്കുന്നു
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
    st.title("Logs")
    df = load_data()
    if df is not None: st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI v17.2")
