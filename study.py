import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. AI ലോഡർ
@st.cache_resource
def load_ai_reader():
    try:
        import easyocr
        return easyocr.Reader(['en'])
    except: return None

# 2. ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Smart Hub", layout="wide")

# 3. ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; border: 2px solid #FFD700; height: 50px; border-radius: 10px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df[df['Amount'] > 0]
    except: return pd.DataFrame()

df = load_data()
menu = st.sidebar.selectbox("Menu", ["💰 Expenses", "📊 Smart Analytics & WhatsApp", "📸 AI Scanner"])

# --- 1. EXPENSES (No Password) ---
if menu == "💰 Expenses":
    st.title("💰 Add Expense")
    st.write("🎤 വോയ്‌സ് ഇൻപുട്ട്:")
    voice_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_exp')
    
    with st.form("expense_form", clear_on_submit=True):
        item = st.text_input("സാധനം", value=voice_text if voice_text else "")
        amt = st.number_input("തുക", min_value=0, value=None)
        if st.form_submit_button("SAVE DATA"):
            if item and amt:
                requests.post(FORM_URL, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success("സേവ് ചെയ്തു!")

# --- 2. ANALYTICS & WHATSAPP (Password Protected) ---
elif menu == "📊 Smart Analytics & WhatsApp":
    if "ana_pass_correct" not in st.session_state:
        st.session_state["ana_pass_correct"] = False

    if not st.session_state["ana_pass_correct"]:
        st.title("🔐 Analytics Login")
        pwd = st.text_input("ഈ സെക്ഷൻ കാണാൻ പാസ്‌വേഡ് നൽകുക", type="password")
        if st.button("UNLOCK"):
            if pwd == "1234": # നിനക്ക് ഇഷ്ടമുള്ള പാസ്‌വേഡ് ഇവിടെ നൽകാം
                st.session_state["ana_pass_correct"] = True
                st.rerun()
            else:
                st.error("തെറ്റായ പാസ്‌വേഡ്!")
    else:
        st.title("📊 Analytics & History")
        if st.button("🔒 Lock Section"):
            st.session_state["ana_pass_correct"] = False
            st.rerun()
            
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">ഈ മാസത്തെ ചിലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("ചിലവ് വിഭജനം")
                fig = px.pie(df, values='Amount', names=df.columns[2], color_discrete_sequence=px.colors.sequential.YlOrBr)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("📋 Recent Records")
                st.table(df.iloc[:, [2, -1]].tail(15).iloc[::-1])
            
            st.markdown("---")
            report = f"PAICHI REPORT: Total Expense: ₹{total}"
            wa_url = f"https://wa.me/?text={requests.utils.quote(report)}"
            if st.button("📲 SEND TO WHATSAPP"):
                st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">CONFIRM ON WHATSAPP</div></a>', unsafe_allow_html=True)

# --- 3. AI SCANNER (No Password) ---
elif menu == "📸 AI Scanner":
    st.title("📸 AI Bill Scanner")
    file = st.file_uploader("ബില്ല് നൽകുക", type=['jpg', 'png', 'jpeg'])
    if file:
        img = Image.open(file)
        st.image(img, width=300)
        if st.button("SCAN"):
            reader = load_ai_reader()
            if reader:
                res = reader.readtext(np.array(img))
                st.success(f"Detected: {res[0][1] if res else 'Amount not found'}")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
