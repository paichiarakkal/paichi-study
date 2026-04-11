import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI", layout="wide")

# 2. ലൈറ്റ് മോഡേൺ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #1e293b;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #cbd5e1;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #cbd5e1;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .total-box {
        background: linear-gradient(135deg, #facc15 0%, #eab308 100%);
        color: #000 !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 32px;
        font-weight: 800;
    }
    h1, h2, h3 { color: #0f172a !important; }
    .stButton>button {
        background: #0f172a !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("🤖 പൈച്ചി മെനു")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 ഹോം", "📥 പുതിയ ചിലവ് ചേർക്കുക", "📊 അനാലിസിസ്", "🔴 കടങ്ങൾ (Debts)", "✅ ചെയ്യേണ്ട കാര്യങ്ങൾ", "💬 എല്ലാ എൻട്രികളും"])

# --- 🏠 ഹോം ---
if menu == "🏠 ഹോം":
    st.title("സ്വാഗതം ഫൈസൽ!")
    st.markdown('<div class="glass-card"><h3>സിസ്റ്റം ഓൺലൈൻ ആണ് 🟢</h3><p>ചിലവുകൾ രേഖപ്പെടുത്താനും വിശകലനം ചെയ്യാനും സൈഡ്‌ബാർ ഉപയോഗിക്കുക.</p></div>', unsafe_allow_html=True)

# --- 📥 പുതിയ ചിലവ് ചേർക്കുക ---
elif menu == "📥 പുതിയ ചിലവ് ചേർക്കുക":
    st.title("📥 ചിലവ് ചേർക്കുക")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("സാധനത്തിന്റെ പേര്", value=v_in if v_in else "")
        amt = st.number_input("തുക (₹)", min_value=0, value=None)
        if st.form_submit_button("സേവ് ചെയ്യുക"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("വിജയകരമായി ചേർത്തു!")
                except: st.error("കണക്ഷൻ പിശക്!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 അനാലിസിസ് ---
elif menu == "📊 അനാലിസിസ്":
    st.title("📊 സാമ്പത്തിക വിശകലനം")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">ആകെ ചിലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("ഡാറ്റ ലഭ്യമല്ല.")

# --- 🔴 കടങ്ങൾ (Debts) ---
elif menu == "🔴 കടങ്ങൾ (Debts)":
    st.title("🔴 പണം നൽകാനുള്ളവർ")
    if 'debts' not in st.session_state: st.session_state.debts = []
    with st.form("debt_form", clear_on_submit=True):
        p = st.text_input("പേര്")
        a = st.number_input("തുക", min_value=0)
        if st.form_submit_button("ലിസ്റ്റിൽ ചേർക്കുക"):
            if p and a: st.session_state.debts.append({"പേര്": p, "തുക": a})
    if st.session_state.debts:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.debts))
        if st.button("ലിസ്റ്റ് ക്ലിയർ ചെയ്യുക"): st.session_state.debts = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- ✅ ചെയ്യേണ്ട കാര്യങ്ങൾ ---
elif menu == "✅ ചെയ്യേണ്ട കാര്യങ്ങൾ":
    st.title("✅ ചെയ്യേണ്ട കാര്യങ്ങൾ (To-Do)")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("പുതിയ ടാസ്ക് ചേർക്കുക:")
    if st.button("ചേർക്കുക"):
        if t: st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        c1, c2 = st.columns([0.85, 0.15])
        c1.markdown(f'<div class="glass-card" style="padding:10px;">🔹 {task}</div>', unsafe_allow_html=True)
        if c2.button("X", key=f"t_{i}"):
            st.session_state.tasks.pop(i); st.rerun()

# --- 💬 എല്ലാ എൻട്രികളും ---
elif menu == "💬 എല്ലാ എൻട്രികളും":
    st.title("💬 മുഴുവൻ വിവരങ്ങൾ")
    df = load_data()
    if not df.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.info(f"ആകെ തുക: ₹ {df['Amount'].sum()}")
    else: st.info("വിവരങ്ങൾ ഒന്നുമില്ല.")

st.sidebar.write("---")
st.sidebar.write("ഡിസൈൻ: ഫൈസൽ | PAICHI AI")
