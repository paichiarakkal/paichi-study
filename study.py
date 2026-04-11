import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px

# 1. നിങ്ങളുടെ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .balance-box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        # കോളങ്ങളുടെ പേരുകൾ ക്ലീൻ ചെയ്യുന്നു
        df.columns = df.columns.str.strip()
        
        # 'Item' കോളം ഇല്ലെങ്കിൽ അത് നിർമ്മിക്കുന്നു (Error ഒഴിവാക്കാൻ)
        if 'Item' not in df.columns:
            for col in df.columns:
                if col.lower() == 'item':
                    df.rename(columns={col: 'Item'}, inplace=True)
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("മെനു:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

if menu == "🏠 Dashboard":
    st.title("Family Hub Analytics")
    df = load_data()
    
    if df is not None and not df.empty:
        # ബാലൻസ് കണക്കാക്കുന്നു
        inc = df['Credit'].sum() if 'Credit' in df.columns else 0
        deb = (df['Debit'].sum() if 'Debit' in df.columns else 0) + (df['Amount'].sum() if 'Amount' in df.columns else 0)
        balance = inc - deb
        
        st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ചിലവുകൾ - ഐറ്റം തിരിച്ച്")
            # ചിലവുകൾ മാത്രം ഫിൽട്ടർ ചെയ്യുന്നു
            exp_df = df.copy()
            exp_df['Total_Exp'] = exp_df['Debit'] + exp_df['Amount']
            exp_df = exp_df[exp_df['Total_Exp'] > 0]
            
            if not exp_df.empty and 'Item' in exp_df.columns:
                # ഓരോ ഐറ്റത്തിനും ആകെ എത്ര ചിലവായി എന്ന് നോക്കുന്നു
                summary = exp_df.groupby('Item')['Total_Exp'].sum().reset_index()
                fig_pie = px.pie(summary, values='Total_Exp', names='Item', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("വിവരങ്ങൾ ലഭ്യമല്ല")

        with col2:
            st.subheader("പ്രതിമാസ ട്രെൻഡ്")
            if 'Date' in df.columns and not df['Date'].isnull().all():
                df['Month'] = df['Date'].dt.strftime('%b %Y')
                monthly = df.groupby('Month').agg({'Credit':'sum', 'Debit':'sum', 'Amount':'sum'}).reset_index()
                monthly['Expense'] = monthly['Debit'] + monthly['Amount']
                fig_bar = px.bar(monthly, x='Month', y=['Credit', 'Expense'], barmode='group')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("ഡേറ്റ കുറവാണ്")

        if st.button("🔄 REFRESH"):
            st.cache_data.clear()
            st.rerun()

elif menu == "💰 Add Entry":
    st.title("Data Entry")
    with st.form("entry_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം")
        amt = st.number_input("തുക", min_value=0)
        type_e = st.radio("തരം:", ["Debit", "Credit"], horizontal=True)
        if st.form_submit_button("SAVE"):
            if item and amt:
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.1460982454": str(amt) if type_e == "Debit" else "0",
                    "entry.1221658767": str(amt) if type_e == "Credit" else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success("സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

elif menu == "💬 Logs":
    st.title("Logs")
    df = load_data()
    if df is not None: st.dataframe(df, use_container_width=True)
