import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ ഉറപ്പുവരുത്തുക
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# മൾട്ടി-ലാംഗ്വേജ് സെറ്റിംഗ്സ്
if 'lang' not in st.session_state:
    st.session_state.lang = "ML"

# ഡിസൈൻ (Gold & Black)
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
    .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
    .metric-box {{ background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; }}
    .log-card {{ background: rgba(0,0,0,0.1); padding: 12px; border-radius: 10px; border-left: 5px solid #000; margin-bottom: 8px; font-weight: bold; color: black; }}
    h1, h2, h3, label, p {{ color: black !important; font-weight: bold !important; }}
    .stButton>button {{ background-color: #000 !important; color: #FFD700 !important; border-radius: 12px; }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # 'Item' കോളം തിരിച്ചറിയുന്നു
        if 'Item' not in df.columns:
            for col in df.columns:
                if col.lower() == 'item': df.rename(columns={col: 'Item'}, inplace=True)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

# Sidebar Controls
st.sidebar.title("⚪ PAICHI AI")
st.session_state.lang = st.sidebar.radio("Language / ഭാഷ:", ["ML", "EN"], horizontal=True)

# ഭാഷാ നിഘണ്ടു
L = {
    "ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 എൻട്രി", "search": "🔍 തിരയുക...", "bal": "ബാക്കി തുക", "inc": "വരുമാനം", "exp": "ചിലവ്", "rec": "സമീപകാല എൻട്രികൾ", "save": "സേവ് ചെയ്യുക"},
    "EN": {"dash": "🏠 Dashboard", "add": "💰 Add Entry", "search": "🔍 Search items...", "bal": "Balance", "inc": "Income", "exp": "Expense", "rec": "Recent Entries", "save": "Save to Cloud"}
}[st.session_state.lang]

menu = st.sidebar.selectbox("Menu:", [L["dash"], L["add"]])
df = load_data()

# --- 🏠 ഡാഷ്‌ബോർഡ് സെക്ഷൻ ---
if menu == L["dash"]:
    st.title(L["dash"])
    if df is not None and not df.empty:
        # 1. കണക്കുകൾ
        income = df['Credit'].sum()
        expense = df['Debit'].sum() + df['Amount'].sum()
        balance = income - expense
        
        st.markdown(f'<div class="balance-box">{L["bal"]}: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="metric-box">{L["inc"]}: ₹ {income:,.2f}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-box">{L["exp"]}: ₹ {expense:,.2f}</div>', unsafe_allow_html=True)

        # 2. വിഷ്വൽ റിപ്പോർട്ടുകൾ
        st.write("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Pie Chart")
            exp_df = df.copy()
            exp_df['Total_Exp'] = exp_df['Debit'] + exp_df['Amount']
            exp_df = exp_df[exp_df['Total_Exp'] > 0]
            if not exp_df.empty:
                summary = exp_df.groupby('Item')['Total_Exp'].sum().reset_index()
                fig = px.pie(summary, values='Total_Exp', names='Item', hole=0.3, color_discrete_sequence=px.colors.sequential.Gold_r)
                st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("Monthly Trend")
            if 'Date' in df.columns:
                df['Month'] = df['Date'].dt.strftime('%b %Y')
                trend = df.groupby('Month').agg({'Credit':'sum', 'Debit':'sum', 'Amount':'sum'}).reset_index()
                trend['Total_Exp'] = trend['Debit'] + trend['Amount']
                fig_bar = px.bar(trend, x='Month', y=['Credit', 'Total_Exp'], barmode='group')
                st.plotly_chart(fig_bar, use_container_width=True)

        # 3. ഓട്ടോമാറ്റിക് ലോഗ്സ്
        st.write("---")
        st.subheader(L["rec"])
        for _, row in df.tail(5).iloc[::-1].iterrows():
            d_val = row['Debit'] + row['Amount']
            val = row['Credit'] if row['Credit'] > 0 else d_val
            label = "🟢" if row['Credit'] > 0 else "🔴"
            st.markdown(f'<div class="log-card">{label} {row["Item"]}: ₹ {val}</div>', unsafe_allow_html=True)

        # 4. സ്മാർട്ട് സെർച്ച്
        st.write("---")
        query = st.text_input(L["search"])
        if query:
            search_res = df[df['Item'].str.contains(query, case=False, na=False)]
            st.dataframe(search_res, use_container_width=True)

# --- 💰 എൻട്രി സെക്ഷൻ ---
elif menu == L["add"]:
    st.title(L["add"])
    # വോയ്‌സ് കമാൻഡ് 🎤
    audio_text = speech_to_text(language='ml' if st.session_state.lang=="ML" else 'en', key='paichi_voice')
    
    with st.form("main_form", clear_on_submit=True):
        item_val = st.text_input("Item Name / ഐറ്റം", value=audio_text if audio_text else "")
        amount_val = st.number_input("Amount / തുക", min_value=0)
        type_val = st.radio("Type / തരം:", ["Debit", "Credit"], horizontal=True)
        
        if st.form_submit_button(L["save"]):
            if item_val and amount_val:
                # നിങ്ങളുടെ വെരിഫൈഡ് ഐഡികൾ
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item_val,
                    "entry.1460982454": str(amount_val) if type_val == "Debit" else "0",
                    "entry.1221658767": str(amount_val) if type_val == "Credit" else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success("Data Saved! ✅")
                st.cache_data.clear()

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
