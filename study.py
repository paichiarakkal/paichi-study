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
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI Ultimate AI", layout="wide")

# ലോഗ്സ് & ഓത്ത് സ്റ്റേറ്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 25px; border: 2px solid #FFD700; }
    .log-container { background: #f0f2f6; padding: 10px; border-radius: 5px; height: 150px; overflow-y: auto; border: 1px solid #ccc; font-family: monospace; font-size: 11px; }
    .stDataFrame { background: white; border-radius: 10px; padding: 5px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 ലോഗിൻ ---
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("ENTER"):
        if USERS.get(u.lower()) == p:
            st.session_state.auth, st.session_state.user = True, u.capitalize()
            add_log(f"Login: {u}")
            st.rerun()
        else: add_log("Login Failed")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: 
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except Exception as e:
            add_log(f"Load Error: {str(e)}")
            return None

    df = load_data()
    st.sidebar.title(f"👤 {st.session_state.user}")
    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Entry", "🤝 Debt", "📊 Report", "📄 Sheet Data"])
    
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- 🏠 ഡാഷ്‌ബോർഡ് + AI ---
    if page == "🏠 Dashboard":
        st.title("AI Financial Advisor")
        if df is not None:
            inc, deb = df['Credit'].sum(), df['Debit'].sum() + df['Amount'].sum()
            st.markdown(f'<div class="box">ബാക്കി: ₹{inc-deb:,.2f}</div>', unsafe_allow_html=True)
            st.write(f"വരുമാനം: ₹{inc} | ചിലവ്: ₹{deb}")

    # --- 💰 എൻട്രി (0 ഇല്ലാതെ) ---
    elif page == "💰 Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='v')
        with st.form("f", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None, placeholder="തുക...")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE") and it and am:
                d, c = (am, 0) if ty == "Debit" else (0, am)
                payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                requests.post(FORM_API, data=payload)
                add_log(f"Saved: {it} (₹{am})")
                st.success("സേവ് ചെയ്തു! ✅")
                st.cache_data.clear()

    # --- 📄 ഷീറ്റ് ഡാറ്റ (പുതിയ ഫീച്ചർ) ---
    elif page == "📄 Sheet Data":
        st.title("Google Sheet Records")
        if df is not None:
            st.write("ഷീറ്റിലെ അവസാന എൻട്രികൾ താഴെ കാണാം:")
            # ഷീറ്റിലെ വിവരങ്ങൾ ടേബിൾ ആയി കാണിക്കുന്നു
            st.dataframe(df.tail(20), use_container_width=True) 
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Full Sheet (Excel)", buf.getvalue(), "Finance_Full.xlsx")

    # --- 🤝 കടം ---
    elif page == "🤝 Debt":
        st.title("Debt Tracker")
        with st.form("d", clear_on_submit=True):
            n, a = st.text_input("പേര്"), st.number_input("തുക", value=None)
            t = st.selectbox("Type", ["Borrowed", "Lent"])
            if st.form_submit_button("ADD"):
                add_log(f"Debt: {n} ({a})")
                st.success("രേഖപ്പെടുത്തി!")

    # --- 📊 റിപ്പോർട്ട് ---
    elif page == "📊 Report":
        st.title("Analysis")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            st.plotly_chart(px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4))

    # --- 📜 ആക്ടിവിറ്റി ലോഗ് ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Activity Logs")
    st.sidebar.markdown(f'<div class="log-container">{"<br>".join(st.session_state.app_logs)}</div>', unsafe_allow_html=True)
