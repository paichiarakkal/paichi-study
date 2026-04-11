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

if 'lang' not in st.session_state: st.session_state.lang = "ML"

# ഡിസൈൻ
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
    .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
    .metric-box {{ background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; }}
    .log-card {{ background: rgba(0,0,0,0.1); padding: 12px; border-radius: 10px; border-left: 5px solid #000; margin-bottom: 8px; font-weight: bold; color: black; }}
    h1, h2, h3, label, p {{ color: black !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Item കോളം കേസ് സെൻസിറ്റീവ് ആവാതിരിക്കാൻ
        for c in df.columns:
            if c.lower() == 'item': df.rename(columns={c: 'Item'}, inplace=True)
        
        if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

# Sidebar
st.sidebar.title("⚪ PAICHI AI")
st.session_state.lang = st.sidebar.radio("Language:", ["ML", "EN"], horizontal=True)
L = {
    "ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 എൻട്രി", "bal": "ബാക്കി തുക", "inc": "വരുമാനം", "exp": "ചിലവ്"},
    "EN": {"dash": "🏠 Dashboard", "add": "💰 Add Entry", "bal": "Balance", "inc": "Income", "exp": "Expense"}
}[st.session_state.lang]

menu = st.sidebar.selectbox("Menu:", [L["dash"], L["add"]])
df = load_data()

if menu == L["dash"]:
    st.title(L["dash"])
    if df is not None and not df.empty:
        # തുക കണക്കാക്കൽ
        income = df['Credit'].sum()
        expense = df['Debit'].sum() + df['Amount'].sum()
        st.markdown(f'<div class="balance-box">{L["bal"]}: ₹ {income-expense:,.2f}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="metric-box">{L["inc"]}: ₹ {income:,.2f}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-box">{L["exp"]}: ₹ {expense:,.2f}</div>', unsafe_allow_html=True)

        # പൈ ചാർട്ട് - എറർ ഫിക്സ്
        st.write("---")
        st.subheader("Pie Chart")
        exp_df = df.copy()
        # തുകയുള്ള കോളങ്ങൾ മാത്രം എടുക്കുന്നു
        exp_df['Total_Exp'] = exp_df['Debit'] + exp_df['Amount']
        exp_df = exp_df[exp_df['Total_Exp'] > 0]
        
        if not exp_df.empty and 'Item' in exp_df.columns:
            #reset_index ഉപയോഗിച്ച് കോളങ്ങൾ വ്യക്തമാക്കുന്നു
            summary = exp_df.groupby('Item')['Total_Exp'].sum().reset_index()
            fig = px.pie(summary, values='Total_Exp', names='Item', hole=0.3, 
                         color_discrete_sequence=px.colors.sequential.Gold_r)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ഡാറ്റ ലഭ്യമല്ല.")

        # സമീപകാല ചരിത്രം
        st.write("---")
        st.subheader("Recent Entries")
        for _, row in df.tail(5).iloc[::-1].iterrows():
            val = row['Credit'] if row['Credit'] > 0 else (row['Debit'] + row['Amount'])
            label = "🟢" if row['Credit'] > 0 else "🔴"
            st.markdown(f'<div class="log-card">{label} {row["Item"]}: ₹ {val}</div>', unsafe_allow_html=True)

elif menu == L["add"]:
    st.title(L["add"])
    v_text = speech_to_text(language='ml' if st.session_state.lang=="ML" else 'en', key='v_input')
    with st.form("entry_form", clear_on_submit=True):
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        t_type = st.radio("Type:", ["Debit", "Credit"], horizontal=True)
        if st.form_submit_button("SAVE"):
            if item and amt:
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.1460982454": str(amt) if t_type == "Debit" else "0",
                    "entry.1221658767": str(amt) if t_type == "Credit" else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success("സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()
