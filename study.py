import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import urllib.parse
import io

# 1. കോൺഫിഗറേഷൻ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# ലോഗിൻ പാസ്‌വേഡ്
USER_PASSWORD = "123" 

st.set_page_config(page_title="PAICHI Ultimate Hub v25.7", layout="wide")

# ലോഗിൻ സ്റ്റേറ്റ് ചെക്കിംഗ്
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ലോഗിൻ പേജ് ഡിസൈൻ
def login_page():
    st.markdown(f"""
        <style>
        .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }}
        .login-box {{ background: rgba(0,0,0,0.8); color: #FFD700; padding: 40px; border-radius: 20px; text-align: center; border: 2px solid #FFD700; }}
        h1 {{ color: #000 !important; }}
        </style>
        """, unsafe_allow_html=True)
    
    st.title("🔐 PAICHI PRO SECURE LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        pwd = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
        if st.button("ENTER"):
            if pwd == USER_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("തെറ്റായ പാസ്‌വേഡ്!")
        st.markdown('</div>', unsafe_allow_html=True)

# ആപ്പ് ബോഡി
if not st.session_state.logged_in:
    login_page()
else:
    # മെയിൻ ഡിസൈൻ
    st.markdown(f"""
        <style>
        .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
        .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
        .metric-card {{ background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; font-size: 18px; }}
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

    # Sidebar Menu
    st.sidebar.title("⚪ PAICHI PRO AI")
    query_params = st.query_params
    url_user = query_params.get("user", "Faisal") 
    st.sidebar.markdown(f"**👤 ലോഗിൻ: {url_user}**")
    
    lang = st.sidebar.radio("ഭാഷ:", ["ML", "EN"], horizontal=True)
    L = {"ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 എൻട്രി", "debt": "🤝 കടം", "rep": "📊 റിപ്പോർട്ട്", "set": "⚙️ ബജറ്റ്"},
         "EN": {"dash": "🏠 Dashboard", "add": "💰 Entry", "debt": "🤝 Debt", "rep": "📊 Reports", "set": "⚙️ Budget"}}[lang]

    page = st.sidebar.radio("Menu:", [L["dash"], L["add"], L["debt"], L["rep"], L["set"]])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    df = load_data()

    # --- 🏠 ഡാഷ്‌ബോർഡ് ---
    if page == L["dash"]:
        st.title(f"Welcome, {url_user}")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            st.markdown(f'<div class="balance-box">ബാക്കി: ₹ {inc-deb:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1: st.markdown(f'<div class="metric-card">വരുമാനം: ₹ {inc:,.2f}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">ചിലവ്: ₹ {deb:,.2f}</div>', unsafe_allow_html=True)
            
            limit = st.session_state.get('b_limit', 10000)
            percent = min(deb / limit, 1.0)
            st.write(f"**ബജറ്റ് ഉപയോഗം: {percent*100:.1f}%**")
            st.progress(percent)

    # --- 💰 എൻട്രി + Voice Input ---
    elif page == L["add"]:
        st.title(L["add"])
        v_text = speech_to_text(language='ml' if lang=="ML" else 'en', key='voice_input')
        with st.form("main_form"):
            item = st.text_input("Item", value=v_text if v_text else "")
            amt = st.number_input("Amount", min_value=0)
            t_type = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if item and amt:
                    full_item = f"[{url_user}] {item}"
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_item, "entry.1460982454": str(amt) if t_type=="Debit" else "0", "entry.1221658767": str(amt) if t_type=="Credit" else "0"}
                    requests.post(FORM_URL_API, data=payload)
                    st.success("സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()

    # --- 🤝 കടം ട്രാക്കർ ---
    elif page == L["debt"]:
        st.title(L["debt"])
        with st.form("debt_form"):
            p_name = st.text_input("പേര്")
            d_amt = st.number_input("തുക", min_value=0)
            d_type = st.selectbox("വിഭാഗം", ["കടം വാങ്ങി", "കടം കൊടുത്തു"])
            if st.form_submit_button("Add Debt"):
                label = f"🤝 കടം: {p_name} ({d_type}) - {url_user}"
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": label, "entry.1460982454": str(d_amt) if "കൊടുത്തു" in d_type else "0", "entry.1221658767": str(d_amt) if "വാങ്ങി" in d_type else "0"}
                requests.post(FORM_URL_API, data=payload)
                st.success("രേഖപ്പെടുത്തി! ✅")

    # --- 📊 റിപ്പോർട്ട് (Excel Fix) ---
    elif page == L["rep"]:
        st.title(L["rep"])
        if df is not None:
            sum_df = df.groupby('Item').agg({'Debit': 'sum', 'Amount': 'sum'}).sum(axis=1).reset_index(name='Total')
            fig = px.pie(sum_df[sum_df['Total']>0], values='Total', names='Item', hole=0.3, color_discrete_sequence=px.colors.sequential.Sunset)
            st.plotly_chart(fig, use_container_width=True)
            
            # Excel Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 ഡൗൺലോഡ് എക്സൽ റിപ്പോർട്ട്", data=buffer.getvalue(), file_name="Finance_Report.xlsx")

    # --- ⚙️ ബജറ്റ് സെറ്റിംഗ്സ് ---
    elif page == L["set"]:
        st.title(L["set"])
        new_limit = st.number_input("മാസ ബജറ്റ് പരിധി:", value=st.session_state.get('b_limit', 10000))
        if st.button("Update"):
            st.session_state.b_limit = new_limit
            st.success("ബജറ്റ് അപ്‌ഡേറ്റ് ചെയ്തു!")
