import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. Config & Auth
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Lite", layout="wide")

# CSS - Golden Theme
st.markdown("<style>.stApp{background:linear-gradient(135deg,#BF953F,#FCF6BA,#AA771C); color:#000;} .box{background:#000; color:#00FF00; padding:20px; border-radius:15px; text-align:center; font-size:30px; border:2px solid #FFD700;}</style>", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# Login Logic
if not st.session_state.auth:
    st.title("🔐 Login")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Login") and USERS.get(u.lower()) == p:
        st.session_state.auth, st.session_state.user = True, u.capitalize()
        st.rerun()
else:
    @st.cache_data(ttl=1)
    def load():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load()
    st.sidebar.title(f"👤 {st.session_state.user}")
    page = st.sidebar.radio("Menu", ["🏠 Home", "💰 Entry", "🤝 Debt", "📊 Report"])
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- Pages ---
    if page == "🏠 Home":
        st.title("Dashboard")
        if df is not None:
            bal = df['Credit'].sum() - (df['Debit'].sum() + df['Amount'].sum())
            st.markdown(f'<div class="box">Balance: ₹{bal:,.2f}</div>', unsafe_allow_html=True)

    elif page == "💰 Entry":
        st.title("Add Entry")
        v = speech_to_text(language='ml', key='v')
        with st.form("f", clear_on_submit=True):
            it, am = st.text_input("Item", value=v if v else ""), st.number_input("Amount", value=None)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("Save") and it and am:
                d, c = (am, 0) if ty == "Debit" else (0, am)
                payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                requests.post(FORM_API, data=payload)
                st.success("Saved! ✅"); st.cache_data.clear()

    elif page == "🤝 Debt":
        st.title("Debt Tracker")
        with st.form("d", clear_on_submit=True):
            n, a = st.text_input("Name"), st.number_input("Amount", value=None)
            t = st.selectbox("Type", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("Add") and n and a:
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"🤝 Debt: {n} ({t})", "entry.1460982454": d, "entry.1221658767": c}
                requests.post(FORM_API, data=payload)
                st.success("Added! ✅"); st.cache_data.clear()

    elif page == "📊 Report":
        st.title("Report")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            st.plotly_chart(px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4))
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Excel", buf.getvalue(), "Report.xlsx")
