import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. AI ബിൽ റീഡർ
@st.cache_resource
def load_ai_reader():
    try:
        import easyocr
        return easyocr.Reader(['en'])
    except: return None

# 2. ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL_IFRAME = "https://forms.gle/R3wVocUKRJ3BLnyP7" 
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Hub", layout="wide")

# 3. ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 4px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് | ഡാറ്റ എന്റർ ചെയ്യാൻ താഴെ കാണുന്ന വോയ്‌സ് അല്ലെങ്കിൽ ഫോം ഉപയോഗിക്കുക 📢</div></div>', unsafe_allow_html=True)

def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df[df['Amount'] > 0]
    except: return pd.DataFrame()

# സൈഡ്‌ബാർ
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add Entry)", "📊 Smart Analytics & WhatsApp", "📸 AI Bill Scanner", "⏰ Reminders"])

# --- 1. HOME ---
if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("ഡാറ്റ ചേർക്കാൻ Expenses പേജിലും, ഹിസ്റ്ററി കാണാൻ Analytics പേജിലും പോകുക.")

# --- 2. EXPENSES (ഇവിടെ ഷീറ്റോ കണക്കോ ഒന്നും കാണിക്കില്ല) ---
elif menu == "💰 Expenses (Add Entry)":
    st.title("💵 Add New Entry")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎤 Voice Input")
        v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
        with st.form("quick_add", clear_on_submit=True):
            item = st.text_input("Item Name", value=v_in if v_in else "")
            amt = st.number_input("Amount", min_value=0, value=None)
            if st.form_submit_button("SAVE"):
                if item and amt:
                    requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                    st.success("Saved Successfully!")
    with col2:
        st.subheader("📝 Manual Form")
        st.components.v1.iframe(FORM_URL_IFRAME, height=500)

# --- 3. ANALYTICS (ഷീറ്റും ഹിസ്റ്ററിയും ഇവിടെ മാത്രം) ---
elif menu == "📊 Smart Analytics & WhatsApp":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    
    if not st.session_state["unlocked"]:
        st.title("🔐 Secure Section")
        pwd = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
        if st.button("UNLOCK"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("തെറ്റായ പാസ്‌വേഡ്!")
    else:
        st.title("📊 History & Reports")
        if st.button("🔒 Lock"):
            st.session_state["unlocked"] = False
            st.rerun()
        
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total Balance: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.pie(df, values='Amount', names=df.columns[2]), use_container_width=True)
            with c2:
                st.table(df.iloc[:, [2, -1]].tail(20).iloc[::-1])
            
            st.markdown("---")
            wa_url = f"https://wa.me/?text={requests.utils.quote(f'PAICHI REPORT: ₹{total}')}"
            if st.button("📲 SEND TO WHATSAPP"):
                st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">CONFIRM WHATSAPP</div></a>', unsafe_allow_html=True)

# --- 4. AI SCANNER ---
elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Scan")
    file = st.file_uploader("Upload", type=['jpg','png','jpeg'])
    if file and st.button("SCAN"):
        reader = load_ai_reader()
        if reader:
            res = reader.readtext(np.array(Image.open(file)))
            if res: st.success(f"Detected: {res[0][1]}")

st.sidebar.write("---")
st.sidebar.write("PAICHI Hub v3.0")
