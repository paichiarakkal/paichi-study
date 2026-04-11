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
        df.columns = df.columns.str.strip()
        # തീയതി ശരിയാക്കുന്നു
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # സംഖ്യകളാക്കുന്നു
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
        # അടിസ്ഥാന കണക്കുകൾ
        total_income = df['Credit'].sum()
        total_expense = df['Debit'].sum() + df['Amount'].sum()
        balance = total_income - total_expense
        
        st.markdown(f'<div class="balance-box">നിലവിലെ ബാലൻസ്: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # 📊 Pie Chart: ചിലവുകൾ തരംതിരിച്ച് (Item-wise Expense)
        with col1:
            st.subheader("ചിലവുകൾ - ഐറ്റം തിരിച്ച്")
            # ചിലവുകൾ ഉള്ള വരികൾ മാത്രം എടുക്കുന്നു
            expense_df = df[df['Debit'] + df['Amount'] > 0].copy()
            expense_df['Total_Exp'] = expense_df['Debit'] + expense_df['Amount']
            
            if not expense_df.empty:
                fig_pie = px.pie(expense_df, values='Total_Exp', names='Item', 
                                 hole=0.4, color_discrete_sequence=px.colors.sequential.Gold_r)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.write("ചിലവുകൾ ഒന്നും രേഖപ്പെടുത്തിയിട്ടില്ല.")

        # 📈 Monthly Trend: മാസ വരുമാനവും ചിലവും
        with col2:
            st.subheader("പ്രതിമാസ ട്രെൻഡ്")
            if 'Date' in df.columns and not df['Date'].isnull().all():
                df['Month'] = df['Date'].dt.strftime('%b %Y')
                monthly_data = df.groupby('Month').agg({'Credit': 'sum', 'Debit': 'sum', 'Amount': 'sum'}).reset_index()
                monthly_data['Total_Expense'] = monthly_data['Debit'] + monthly_data['Amount']
                
                fig_trend = px.bar(monthly_data, x='Month', y=['Credit', 'Total_Expense'],
                                   barmode='group', color_discrete_map={'Credit': '#00FF00', 'Total_Expense': '#FF0000'})
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.write("ട്രെൻഡ് കാണിക്കാൻ മതിയായ ഡാറ്റയില്ല.")

        if st.button("🔄 REFRESH"):
            st.cache_data.clear()
            st.rerun()

elif menu == "💰 Add Entry":
    st.title("Data Entry")
    with st.form("entry_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര് (ഉദാ: ഭക്ഷണം, പെട്രോൾ)")
        amt = st.number_input("തുക (₹)", min_value=0)
        type_entry = st.radio("തരം:", ["Debit", "Credit"], horizontal=True)
        
        if st.form_submit_button("SAVE"):
            if item and amt:
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.1460982454": str(amt) if type_entry == "Debit" else "0",
                    "entry.1221658767": str(amt) if type_entry == "Credit" else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success(f"{item} സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

elif menu == "💬 Logs":
    st.title("Logs")
    df = load_data()
    if df is not None: st.dataframe(df, use_container_width=True)
