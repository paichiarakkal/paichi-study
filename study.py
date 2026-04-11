import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Ultimate Hub", layout="wide")

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
        for c in df.columns:
            if c.lower() == 'item': df.rename(columns={c: 'Item'}, inplace=True)
        if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

# Sidebar
st.sidebar.title("⚪ PAICHI PRO AI")
st.session_state.lang = st.sidebar.radio("Language:", ["ML", "EN"], horizontal=True)

L = {
    "ML": {"dash": "🏠 ഡാഷ്‌ബോർഡ്", "add": "💰 എൻട്രി", "debt": "🤝 കടം (Debt)", "rep": "📊 റിപ്പോർട്ട്", "set": "⚙️ ബജറ്റ്", "user": "👤 അംഗങ്ങൾ"},
    "EN": {"dash": "🏠 Dashboard", "add": "💰 Entry", "debt": "🤝 Debt Tracker", "rep": "📊 Reports", "set": "⚙️ Budget", "user": "👤 Users"}
}[st.session_state.lang]

page = st.sidebar.radio("Menu:", [L["dash"], L["add"], L["debt"], L["rep"], L["set"]])
df = load_data()

# --- പേജ് 1: ഡാഷ്‌ബോർഡ് ---
if page == L["dash"]:
    st.title(L["dash"])
    if df is not None:
        inc = df['Credit'].sum()
        deb = df['Debit'].sum() + df['Amount'].sum()
        st.markdown(f'<div class="balance-box">ബാക്കി: ₹ {inc-deb:,.2f}</div>', unsafe_allow_html=True)
        
        # ബജറ്റ് അലേർട്ട്
        limit = st.session_state.get('b_limit', 10000)
        if deb > limit: st.error(f"⚠️ ബജറ്റ് പരിധി (₹{limit}) കവിഞ്ഞു!")

        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="metric-box">വരുമാനം: ₹ {inc:,.2f}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-box">ചിലവ്: ₹ {deb:,.2f}</div>', unsafe_allow_html=True)

# --- പേജ് 2: പുതിയ എൻട്രി (Multi-User Support) ---
elif page == L["add"]:
    st.title(L["add"])
    users = ["ഫൈസൽ", "ഉമ്മ", "ഉപ്പ", "അനിയൻ"] # യൂസർ ലിസ്റ്റ്
    v_text = speech_to_text(language='ml' if st.session_state.lang=="ML" else 'en', key='v_p')
    with st.form("pro_entry"):
        u_name = st.selectbox("ആരാണ് ചിലവാക്കിയത്?", users)
        item = st.text_input("Item", value=v_text if v_text else "")
        amt = st.number_input("Amount", min_value=0)
        t_type = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        if st.form_submit_button("SAVE"):
            if item and amt:
                # യൂസർ പേര് കൂടി ഐറ്റത്തോടൊപ്പം ചേർക്കുന്നു
                full_item = f"[{u_name}] {item}"
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": full_item,
                    "entry.1460982454": str(amt) if t_type == "Debit" else "0",
                    "entry.1221658767": str(amt) if t_type == "Credit" else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success("സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

# --- പേജ് 3: കടം ട്രാക്കർ (Debt Tracker) ---
elif page == L["debt"]:
    st.title(L["debt"])
    st.info("കടം നൽകിയതും വാങ്ങിയതും ഇവിടെ രേഖപ്പെടുത്താം")
    with st.form("debt_form"):
        p_name = st.text_input("ആളുടെ പേര്")
        d_amt = st.number_input("തുക", min_value=0)
        d_type = st.selectbox("വിഭാഗം", ["കടം വാങ്ങി (I Borrowed)", "കടം കൊടുത്തു (I Lent)"])
        if st.form_submit_button("ADD DEBT"):
            label = f"🤝 DEBT: {p_name} ({d_type})"
            payload = {
                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                "entry.2013476337": label,
                "entry.1460982454": str(d_amt) if "Lent" in d_type else "0",
                "entry.1221658767": str(d_amt) if "Borrowed" in d_type else "0"
            }
            requests.post(FORM_URL_API, data=payload)
            st.success("രേഖപ്പെടുത്തി! ✅")

# --- പേജ് 4: റിപ്പോർട്ടുകൾ & ഡൗൺലോഡ് ---
elif page == L["rep"]:
    st.title(L["rep"])
    if df is not None:
        # പൈ ചാർട്ട്
        sum_df = df.groupby('Item').agg({'Debit': 'sum', 'Amount': 'sum'}).sum(axis=1).reset_index(name='Total')
        sum_df = sum_df[sum_df['Total'] > 0]
        fig = px.pie(sum_df, values='Total', names='Item', hole=0.3, color_discrete_sequence=px.colors.sequential.Sunset)
        st.plotly_chart(fig, use_container_width=True)
        
        # Excel ഡൗൺലോഡ്
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, header=True)
        st.download_button("📥 Download Excel Report", data=towrite.getvalue(), file_name="family_finance.xlsx")

# --- പേജ് 5: ബജറ്റ് സെറ്റിംഗ്സ് ---
elif page == L["set"]:
    st.title(L["set"])
    new_limit = st.number_input("മാസ ബജറ്റ് സെറ്റ് ചെയ്യുക:", value=st.session_state.get('b_limit', 10000))
    if st.button("Update Limit"):
        st.session_state.b_limit = new_limit
        st.success(f"പുതിയ ബജറ്റ് ₹{new_limit} ആയി സെറ്റ് ചെയ്തു!")
