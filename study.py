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

st.set_page_config(page_title="PAICHI Ultimate AI Hub", layout="wide")

# സ്റ്റേറ്റ് മാനേജ്‌മെന്റ്
if 'app_logs' not in st.session_state: st.session_state.app_logs = []
if 'auth' not in st.session_state: st.session_state.auth = False

def add_log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.app_logs.insert(0, f"[{now}] {msg}")

# CSS - ഗോൾഡൻ തീം
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .box { background: #000; color: #00FF00; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; border: 3px solid #FFD700; }
    .ai-card { background: rgba(0,0,0,0.85); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 20px; }
    .log-container { background: #f0f2f6; padding: 10px; border-radius: 5px; height: 150px; overflow-y:auto; font-family:monospace; font-size: 11px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stDataFrame { background: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🔐 ലോഗിൻ സിസ്റ്റം ---
if not st.session_state.auth:
    st.title("🔐 PAICHI PRO LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("ENTER"):
            if USERS.get(u) == p:
                st.session_state.auth, st.session_state.user = True, u.capitalize()
                add_log(f"Login: {u}")
                st.rerun()
            else: 
                st.error("Invalid Login!")
                add_log(f"Failed attempt: {u}")
else:
    @st.cache_data(ttl=1)
    def load_data():
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            for c in ['Amount','Debit','Credit']: 
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            return df
        except: return None

    df = load_data()
    st.sidebar.title(f"👤 {st.session_state.user}")
    page = st.sidebar.radio("Menu", ["🏠 AI Dashboard", "💰 Entry", "🤝 Debt", "📄 Sheet Data", "📊 Report"])
    
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- 🏠 AI DASHBOARD (Advisor) ---
    if page == "🏠 AI Dashboard":
        st.title("AI Financial Advisor 🤖")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            bal = inc - deb
            st.markdown(f'<div class="box">നിലവിലെ ബാലൻസ്: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            st.subheader("💡 AI Insights")
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            exp_ratio = (deb / inc * 100) if inc > 0 else 0
            
            if exp_ratio > 80:
                st.write(f"⚠️ **ശ്രദ്ധിക്കുക!** ചിലവ് വരുമാനത്തിന്റെ {exp_ratio:.1f}% കടന്നു. മിതവ്യയം പാലിക്കുക.")
            elif exp_ratio < 50 and inc > 0:
                st.write("✅ **അടിപൊളി!** സാമ്പത്തിക നില ഭദ്രമാണ്. പണം സേവ് ചെയ്യാൻ പറ്റിയ സമയമാണിത്.")
            
            # ട്രേഡിംഗ് തിരിച്ചറിയൽ (ഉദാഹരണത്തിന് Crude Oil Profit)
            trade_df = df[df['Item'].str.contains('profit|trade|CE|PE', case=False, na=False)]
            if not trade_df.empty:
                t_profit = trade_df['Credit'].sum()
                st.write(f"📈 ട്രേഡിംഗിലൂടെ ₹{t_profit} സമ്പാദിച്ചിട്ടുണ്ട്. റിസ്ക് മാനേജ്മെന്റ് തുടരുക!")
            else:
                st.write("📊 നിങ്ങളുടെ ചിലവുകൾ ഇപ്പോൾ നോർമൽ ആണ്.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.plotly_chart(px.bar(x=["Income", "Expense"], y=[inc, deb], color=["Income", "Expense"], title="Income vs Expense Summary"))

    # --- 💰 ENTRY (0 മാറ്റിയത്) ---
    elif page == "💰 Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='v_in')
        with st.form("f", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.number_input("Amount", value=None, placeholder="തുക നൽകുക...")
            ty = st.radio("Type", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    add_log(f"Saved: {it} (₹{am})")
                    st.success("സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()

    # --- 🤝 DEBT TRACKER ---
    elif page == "🤝 Debt":
        st.title("Debt Tracker")
        with st.form("d_f", clear_on_submit=True):
            n, a = st.text_input("പേര്"), st.number_input("തുക", value=None)
            t = st.selectbox("വിഭാഗം", ["കടം വാങ്ങി", "കടം കൊടുത്തു"])
            if st.form_submit_button("ADD"):
                add_log(f"Debt Added: {n} ({a})")
                st.success("രേഖപ്പെടുത്തി!")

    # --- 📄 SHEET DATA (ഷീറ്റ് കോപ്പി) ---
    elif page == "📄 Sheet Data":
        st.title("Google Sheet Records")
        if df is not None:
            st.write("അവസാനത്തെ എൻട്രികൾ താഴെ:")
            st.dataframe(df.tail(20), use_container_width=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Excel Report", buf.getvalue(), "Full_Report.xlsx")

    # --- 📊 REPORT ---
    elif page == "📊 Report":
        st.title("Expense Analysis")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            st.plotly_chart(px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4))

    # --- 📜 LOGS (SideBar) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Activity Logs")
    st.sidebar.markdown(f'<div class="log-container">{"<br>".join(st.session_state.app_logs)}</div>', unsafe_allow_html=True)
