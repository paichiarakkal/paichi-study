import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. കോൺഫിഗറേഷൻ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഭാഷാ ക്രമീകരണം
if 'lang' not in st.session_state: st.session_state.lang = "ML"

# ഡിസൈൻ
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
    .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
    .metric-box {{ background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; }}
    .log-card {{ background: rgba(0,0,0,0.1); padding: 12px; border-radius: 10px; border-left: 5px solid #000; margin-bottom: 8px; font-weight: bold; color: black; }}
    .budget-warn {{ background: #ff4b4b; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }}
    h1, h2, h3, label, p {{ color: black !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 999999)}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
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
    "ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 പുതിയ എൻട്രി", "search": "🔍 തിരയുക", "rep": "📊 റിപ്പോർട്ടുകൾ", "set": "⚙️ സെറ്റിംഗ്സ്", "bal": "ബാക്കി തുക", "inc": "വരുമാനം", "exp": "ചിലവ്"},
    "EN": {"dash": "🏠 Dashboard", "add": "💰 New Entry", "search": "🔍 Search", "rep": "📊 Reports", "set": "⚙️ Settings", "bal": "Balance", "inc": "Income", "exp": "Expense"}
}[st.session_state.lang]

page = st.sidebar.radio("Menu:", [L["dash"], L["add"], L["search"], L["rep"], L["set"]])
df = load_data()

# --- പേജ് 1: ഡാഷ്‌ബോർഡ് ---
if page == L["dash"]:
    st.title(L["dash"])
    if df is not None:
        inc = df['Credit'].sum()
        deb = df['Debit'].sum() + df['Amount'].sum()
        bal = inc - deb
        st.markdown(f'<div class="balance-box">{L["bal"]}: ₹ {bal:,.2f}</div>', unsafe_allow_html=True)
        
        # ബജറ്റ് പരിശോധന
        monthly_budget = st.session_state.get('budget_limit', 10000)
        if deb > monthly_budget:
            st.markdown(f'<div class="budget-warn">⚠️ ബജറ്റ് കവിഞ്ഞു! (Limit: ₹{monthly_budget})</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="metric-box">{L["inc"]}: ₹ {inc:,.2f}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-box">{L["exp"]}: ₹ {deb:,.2f}</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("Recent Activity 📋")
        for _, row in df.tail(8).iloc[::-1].iterrows():
            val = row['Credit'] if row['Credit'] > 0 else (row['Debit'] + row['Amount'])
            icon = "🟢" if row['Credit'] > 0 else "🔴"
            st.markdown(f'<div class="log-card">{icon} {row["Item"]} - ₹{val}</div>', unsafe_allow_html=True)

# --- പേജ് 2: പുതിയ എൻട്രി ---
elif page == L["add"]:
    st.title(L["add"])
    v_text = speech_to_text(language='ml' if st.session_state.lang=="ML" else 'en', key='voice_v20')
    with st.form("entry_v20", clear_on_submit=True):
        item = st.text_input("Item Name", value=v_text if v_text else "")
        amt = st.number_input("Amount (₹)", min_value=0)
        t_type = st.radio("Transaction Type:", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
        if st.form_submit_button("SAVE DATA"):
            if item and amt:
                is_credit = "Credit" in t_type
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.1460982454": str(amt) if not is_credit else "0",
                    "entry.1221658767": str(amt) if is_credit else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success(f"{item} സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

# --- പേജ് 3: തിരയുക ---
elif page == L["search"]:
    st.title(L["search"])
    search_q = st.text_input("തിരയേണ്ട ഐറ്റം ടൈപ്പ് ചെയ്യുക (ഉദാ: Salary, Food)")
    if df is not None and search_q:
        filtered = df[df['Item'].str.contains(search_q, case=False, na=False)]
        st.write(f"Results for '{search_q}':")
        st.dataframe(filtered, use_container_width=True)

# --- പേജ് 4: റിപ്പോർട്ടുകൾ & ഡൗൺലോഡ് ---
elif page == L["rep"]:
    st.title(L["rep"])
    if df is not None:
        # പൈ ചാർട്ട്
        exp_df = df.copy()
        exp_df['Total_Exp'] = exp_df['Debit'] + exp_df['Amount']
        exp_df = exp_df[exp_df['Total_Exp'] > 0]
        
        if not exp_df.empty:
            summary = exp_df.groupby('Item')['Total_Exp'].sum().reset_index()
            fig = px.pie(summary, values='Total_Exp', names='Item', hole=0.35,
                         title="Expense Breakdown", color_discrete_sequence=px.colors.sequential.Sunset)
            st.plotly_chart(fig, use_container_width=True)
            
            # ഡൗൺലോഡ് ബട്ടൺ (Excel)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Finance_Report')
            st.download_button(label="📥 Download Report (Excel)", data=buffer.getvalue(), 
                               file_name=f"Report_{datetime.now().date()}.xlsx", mime="application/vnd.ms-excel")
        else:
            st.info("റിപ്പോർട്ടുകൾ കാണിക്കാൻ ആവശ്യമായ ചിലവുകൾ ലഭ്യമല്ല.")

# --- പേജ് 5: സെറ്റിംഗ്സ് ---
elif page == L["set"]:
    st.title(L["set"])
    st.subheader("Monthly Budget Setting")
    b_limit = st.number_input("മാസ ബജറ്റ് സെറ്റ് ചെയ്യുക (₹):", value=st.session_state.get('budget_limit', 10000))
    if st.button("Update Budget"):
        st.session_state.budget_limit = b_limit
        st.success("ബജറ്റ് അപ്‌ഡേറ്റ് ചെയ്തു!")
