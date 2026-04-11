import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
import io

# 1. ലിങ്കുകൾ & കോൺഫിഗറേഷൻ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI Hub v26.2", layout="wide")

# CSS - ഗോൾഡൻ തീം & AI ബോക്സ്
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .box { background: #000; color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    .ai-card { background: rgba(0,0,0,0.8); color: #FFD700; padding: 20px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 🔐 ലോഗിൻ സിസ്റ്റം ---
if not st.session_state.auth:
    st.title("🔐 PAICHI PRO LOGIN")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if USERS.get(u) == p:
                st.session_state.auth = True
                st.session_state.user = u.capitalize()
                st.rerun()
            else: st.error("തെറ്റായ വിവരങ്ങൾ!")
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
    page = st.sidebar.radio("Menu", ["🏠 AI Dashboard", "💰 Entry", "🤝 Debt", "📊 Report", "⚙️ Budget"])
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # --- 🏠 AI DASHBOARD ---
    if page == "🏠 AI Dashboard":
        st.title(f"AI Advisor Dashboard")
        if df is not None:
            inc = df['Credit'].sum()
            deb = df['Debit'].sum() + df['Amount'].sum()
            bal = inc - deb
            st.markdown(f'<div class="box">ബാക്കി: ₹{bal:,.2f}</div>', unsafe_allow_html=True)
            
            # AI Insights
            st.subheader("🤖 AI അഡ്വൈസർ പറയുന്നു:")
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            if deb > inc * 0.8:
                st.write(f"⚠️ {st.session_state.user}, സൂക്ഷിക്കുക! നിങ്ങളുടെ വരുമാനത്തിന്റെ ഭൂരിഭാഗവും ചിലവായി കഴിഞ്ഞു.")
            elif bal > 5000:
                st.write(f"✅ മികച്ച രീതിയിൽ മുന്നോട്ട് പോകുന്നു. ഈ മാസം നല്ലൊരു തുക സമ്പാദിക്കാൻ സാധിക്കും.")
            else:
                st.write("📊 നിങ്ങളുടെ ചിലവുകൾ മിതമായ രീതിയിലാണ്. അനാവശ്യ ചിലവുകൾ ഒഴിവാക്കാൻ ശ്രദ്ധിക്കുക.")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- 💰 ENTRY (0 മാറ്റിയത്) ---
    elif page == "💰 Entry":
        st.title("New Entry")
        v = speech_to_text(language='ml', key='v_input')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item Name", value=v if v else "")
            am = st.number_input("Amount", value=None, placeholder="തുക നൽകുക...")
            ty = st.radio("Type", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
            if st.form_submit_button("SAVE"):
                if it and am:
                    d, c = (am, 0) if "Debit" in ty else (0, am)
                    payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"[{st.session_state.user}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                    requests.post(FORM_API, data=payload)
                    st.success("വിജയകരമായി സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()

    # --- 🤝 DEBT TRACKER ---
    elif page == "🤝 Debt":
        st.title("Debt Tracker")
        with st.form("debt_form", clear_on_submit=True):
            n = st.text_input("ആളുടെ പേര്")
            a = st.number_input("തുക", value=None, placeholder="തുക നൽകുക...")
            t = st.selectbox("വിഭാഗം", ["Borrowed (വാങ്ങി)", "Lent (കൊടുത്തു)"])
            if st.form_submit_button("ADD DEBT"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                payload = {"entry.1044099436": datetime.now().date(), "entry.2013476337": f"🤝 കടം: {n} ({t})", "entry.1460982454": d, "entry.1221658767": c}
                requests.post(FORM_API, data=payload)
                st.success("കടം രേഖപ്പെടുത്തി! ✅")
                st.cache_data.clear()

    # --- 📊 REPORT & EXCEL ---
    elif page == "📊 Report":
        st.title("Financial Report")
        if df is not None:
            sdf = df.groupby('Item')[['Debit','Amount']].sum().sum(axis=1).reset_index(name='T')
            fig = px.pie(sdf[sdf['T']>0], values='T', names='Item', hole=0.4, color_discrete_sequence=px.colors.sequential.Sunset)
            st.plotly_chart(fig, use_container_width=True)
            
            # Excel Download
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Excel Report", buf.getvalue(), "Report.xlsx")

    # --- ⚙️ BUDGET SETTINGS ---
    elif page == "⚙️ Budget":
        st.title("Budget Settings")
        lim = st.number_input("മാസ ബജറ്റ് പരിധി:", value=st.session_state.get('b_lim', 10000))
        if st.button("Update Budget"):
            st.session_state.b_lim = lim
            st.success("ബജറ്റ് അപ്‌ഡേറ്റ് ചെയ്തു!")
