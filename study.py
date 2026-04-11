import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# മൾട്ടി-ലാംഗ്വേജ് സെറ്റിംഗ്സ്
if 'lang' not in st.session_state: st.session_state.lang = "ML"

# ഡിസൈൻ
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
    .balance-box {{ background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
    .log-card {{ background: rgba(0,0,0,0.1); padding: 10px; border-radius: 10px; border-left: 5px solid #000; margin-bottom: 5px; font-weight: bold; }}
    h1, h2, h3, label, p {{ color: black !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

# Sidebar
st.sidebar.title("⚪ PAICHI AI")
st.session_state.lang = st.sidebar.radio("Language:", ["ML", "EN"], horizontal=True)
L = {
    "ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 പുതിയ എൻട്രി", "search": "🔍 സെർച്ച്", "bal": "ബാക്കി തുക", "exp": "ചിലവ്", "inc": "വരുമാനം"},
    "EN": {"dash": "🏠 Dashboard", "add": "💰 Add Entry", "search": "🔍 Search", "bal": "Balance", "exp": "Expense", "inc": "Income"}
}[st.session_state.lang]

menu = st.sidebar.selectbox("Menu:", [L["dash"], L["add"]])

df = load_data()

if menu == L["dash"]:
    st.title(L["dash"])
    if df is not None:
        # ബാലൻസ്
        inc = df['Credit'].sum()
        deb = df['Debit'].sum() + df['Amount'].sum()
        st.markdown(f'<div class="balance-box">{L["bal"]}: ₹ {inc-deb:,.2f}</div>', unsafe_allow_html=True)
        
        # ഓട്ടോമാറ്റിക് ലോഗ്സ് (Recent 5)
        st.subheader("Recent Entries 📋")
        for _, row in df.tail(5).iterrows():
            st.markdown(f'<div class="log-card">{row["Date"].date() if "Date" in df.columns else ""} | {row["Item"]}: ₹ {row["Debit"]+row["Credit"]+row["Amount"]}</div>', unsafe_allow_html=True)

        # സ്മാർട്ട് സെർച്ച് 🔍
        st.write("---")
        search_query = st.text_input(L["search"])
        if search_query:
            filtered_df = df[df['Item'].str.contains(search_query, case=False, na=False)]
            st.dataframe(filtered_df)

elif menu == L["add"]:
    st.title(L["add"])
    # വോയ്‌സ് കമാൻഡ് 🎤
    audio_text = speech_to_text(language='ml' if st.session_state.lang=="ML" else 'en', key='voice_v179')
    
    with st.form("entry_form", clear_on_submit=True):
        item = st.text_input("Item", value=audio_text if audio_text else "")
        amt = st.number_input("Amount", min_value=0)
        type_e = st.radio("Type:", ["Debit", "Credit"], horizontal=True)
        
        if st.form_submit_button("SAVE"):
            if item and amt:
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.1460982454": str(amt) if type_e == "Debit" else "0",
                    "entry.1221658767": str(amt) if type_e == "Credit" else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success("Success! ✅")
                st.cache_data.clear()
