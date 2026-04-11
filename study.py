import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import urllib.parse
import io

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Ultimate Hub v25.4", layout="wide")

# ഓട്ടോ ലോഗിൻ
query_params = st.query_params
url_user = query_params.get("user", "Guest") 

if 'lang' not in st.session_state: st.session_state.lang = "ML"

# ഡിസൈൻ - ഗോൾഡൻ തീം
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }}
    .balance-box {{ background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }}
    .metric-box {{ background: #000; color: #FFD700; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #FFD700; }}
    .whatsapp-btn {{ background-color: #25D366; color: white !important; padding: 12px 25px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 15px; border: 2px solid white; }}
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
st.sidebar.title("⚪ PAICHI PRO AI")
st.sidebar.markdown(f"**👤 ലോഗിൻ: {url_user}**")
st.session_state.lang = st.sidebar.radio("ഭാഷ:", ["ML", "EN"], horizontal=True)

L = {"ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 എൻട്രി", "debt": "🤝 കടം", "rep": "📊 റിപ്പോർട്ട്", "set": "⚙️ ബജറ്റ്"},
     "EN": {"dash": "🏠 Dashboard", "add": "💰 Entry", "debt": "🤝 Debt", "rep": "📊 Reports", "set": "⚙️ Budget"}}[st.session_state.lang]

page = st.sidebar.radio("Menu:", [L["dash"], L["add"], L["debt"], L["rep"], L["set"]])
df = load_data()

# --- പേജ് 1: ഡാഷ്‌ബോർഡ് ---
if page == L["dash"]:
    st.title(L["dash"])
    if df is not None:
        inc = df['Credit'].sum()
        deb = df['Debit'].sum() + df['Amount'].sum()
        st.markdown(f'<div class="balance-box">ബാക്കി: ₹ {inc-deb:,.2f}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="metric-box">വരുമാനം: ₹ {inc:,.2f}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-box">ചിലവ്: ₹ {deb:,.2f}</div>', unsafe_allow_html=True)

# --- പേജ് 2: എൻട്രി + വാട്സാപ്പ് ഷെയറിംഗ് ---
elif page == L["add"]:
    st.title(L["add"])
    v_text = speech_to_text(language='ml' if st.session_state.lang=="ML" else 'en', key='voice_input')
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
                
                # WhatsApp Link (ഇതാണ് മെയിൻ ഫീച്ചർ)
                msg = f"*PAICHI FINANCE UPDATE*\n👤: {url_user}\n📦: {item}\n💰: ₹{amt}\n📝: {t_type}"
                w_url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{w_url}" target="_blank" class="whatsapp-btn">📲 Share to WhatsApp</a>', unsafe_allow_html=True)
                st.cache_data.clear()

# --- പേജ് 3: കടം ട്രാക്കർ ---
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

# --- പേജ് 4: റിപ്പോർട്ടുകൾ (എറർ ഫ്രീ) ---
elif page == L["rep"]:
    st.title(L["rep"])
    if df is not None:
        sum_df = df.groupby('Item').agg({'Debit': 'sum', 'Amount': 'sum'}).sum(axis=1).reset_index(name='Total')
        # 'Gold_r' എറർ ഒഴിവാക്കാൻ Sunset പാരറ്റ് ഉപയോഗിച്ചു
        fig = px.pie(sum_df[sum_df['Total']>0], values='Total', names='Item', hole=0.3, color_discrete_sequence=px.colors.sequential.Sunset)
        st.plotly_chart(fig, use_container_width=True)
        
        # Excel ഡൗൺലോഡ് (ഇപ്പോൾ xlsxwriter ഉള്ളതിനാൽ വർക്ക് ചെയ്യും)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        st.download_button(label="📥 Download Excel Report", data=buffer.getvalue(), file_name=f"Report_{datetime.now().date()}.xlsx", mime="application/vnd.ms-excel")

# --- പേജ് 5: ബജറ്റ് ---
elif page == L["set"]:
    st.title(L["set"])
    new_limit = st.number_input("മാസ ബജറ്റ് പരിധി:", value=st.session_state.get('b_limit', 10000))
    if st.button("Update"):
        st.session_state.b_limit = new_limit
        st.success("ബജറ്റ് സെറ്റ് ചെയ്തു!")
