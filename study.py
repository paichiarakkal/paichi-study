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

# --- 👤 യൂസർ പാസ്‌വേഡ് ലിസ്റ്റ് (ഇവിടെ നിങ്ങൾക്ക് പുതിയ ആളുകളെ ചേർക്കാം) ---
USER_DB = {
    "faisal": "faisal123",
    "admin": "paichi786",
    "guest": "123"
}

st.set_page_config(page_title="PAICHI Ultimate Hub v25.8", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

# --- 🔐 ലോഗിൻ സ്ക്രീൻ ഡിസൈൻ ---
def login_page():
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
        .login-box { background: rgba(0,0,0,0.85); color: #FFD700; padding: 40px; border-radius: 20px; text-align: center; border: 3px solid #FFD700; margin-top: 50px; }
        .stButton>button { background-color: #FFD700 !important; color: black !important; font-weight: bold; width: 100%; }
        </style>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown('<div class="login-box"><h1>🔐 PAICHI PRO LOGIN</h1>', unsafe_allow_html=True)
        u_name = st.text_input("Username (പേര്)").lower()
        u_pwd = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u_name in USER_DB and USER_DB[u_name] == u_pwd:
                st.session_state.logged_in = True
                st.session_state.user_name = u_name.capitalize()
                st.rerun()
            else:
                st.error("പേരോ പാസ്‌വേഡോ തെറ്റാണ്!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 🏠 ആപ്പ് ബോഡി ---
if not st.session_state.logged_in:
    login_page()
else:
    # ഗോൾഡൻ തീം ഡിസൈൻ
    st.markdown(f"""
        <style>
        .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
        .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
        .metric-card {{ background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; }}
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
    st.sidebar.markdown(f"**👤 User: {st.session_state.user_name}**")
    lang = st.sidebar.radio("ഭാഷ:", ["ML", "EN"], horizontal=True)
    
    L = {"ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 എൻട്രി", "debt": "🤝 കടം", "rep": "📊 റിപ്പോർട്ട്", "set": "⚙️ ബജറ്റ്"},
         "EN": {"dash": "🏠 Dashboard", "add": "💰 Entry", "debt": "🤝 Debt", "rep": "📊 Reports", "set": "⚙️ Budget"}}[lang]

    page = st.sidebar.radio("Menu:", [L["dash"], L["add"], L["debt"], L["rep"], L["set"]])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    df = load_data()

    # --- പേജ് 1: ഡാഷ്‌ബോർഡ് ---
    if page == L["dash"]:
        st.title(f"ഹലോ, {st.session_state.user_name} 👋")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            st.markdown(f'<div class="balance-box">ബാക്കി: ₹ {inc-deb:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1: st.markdown(f'<div class="metric-card">വരുമാനം: ₹ {inc:,.2f}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">ചിലവ്: ₹ {deb:,.2f}</div>', unsafe_allow_html=True)

    # --- പേജ് 2: എൻട്രി (Voice Input) ---
    elif page == L["add"]:
        st.title(L["add"])
        v_text = speech_to_text(language='ml' if lang=="ML" else 'en', key='voice_input')
        with st.form("main_form"):
            item = st.text_input("Item", value=v_text if v_text else "")
            amt = st.number_input("Amount", min_value=0)
            t_type = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if item and amt:
                    full_item = f"[{st.session_state.user_name}] {item}"
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": full_item, "entry.1460982454": str(amt) if t_type=="Debit" else "0", "entry.1221658767": str(amt) if t_type=="Credit" else "0"}
                    requests.post(FORM_URL_API, data=payload)
                    st.success("സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()

    # --- പേജ് 3: കടം ---
    elif page == L["debt"]:
        st.title(L["debt"])
        with st.form("debt_form"):
            p_name = st.text_input("പേര്")
            d_amt = st.number_input("തുക", min_value=0)
            d_type = st.selectbox("വിഭാഗം", ["കടം വാങ്ങി", "കടം കൊടുത്തു"])
            if st.form_submit_button("Add"):
                label = f"🤝 കടം: {p_name} ({d_type}) - {st.session_state.user_name}"
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": label, "entry.1460982454": str(d_amt) if "കൊടുത്തു" in d_type else "0", "entry.1221658767": str(d_amt) if "വാങ്ങി" in d_type else "0"}
                requests.post(FORM_URL_API, data=payload)
                st.success("രേഖപ്പെടുത്തി! ✅")

    # --- പേജ് 4: റിപ്പോർട്ടുകൾ ---
    elif page == L["rep"]:
        st.title(L["rep"])
        if df is not None:
            sum_df = df.groupby('Item').agg({'Debit': 'sum', 'Amount': 'sum'}).sum(axis=1).reset_index(name='Total')
            fig = px.pie(sum_df[sum_df['Total']>0], values='Total', names='Item', hole=0.3, color_discrete_sequence=px.colors.sequential.Sunset)
            st.plotly_chart(fig, use_container_width=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Download Excel Report", data=buffer.getvalue(), file_name="Report.xlsx")
