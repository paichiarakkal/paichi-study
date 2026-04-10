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
    except:
        return None

# 2. ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Hub", layout="wide")

# 3. ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; border-radius: 10px; }
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

# സൈഡ്‌ബാർ മെനു
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses", "📊 Smart Analytics & WhatsApp", "📸 AI Bill Scanner"])

df = load_data()

# --- 1. HOME ---
if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total Expense: ₹ {total:,.2f}</div>', unsafe_allow_html=True)

# --- 2. EXPENSES ---
elif menu == "💰 Expenses":
    st.title("💰 Add Expense")
    col1, col2 = st.columns(2)
    with col1:
        voice_text = speech_to_text(language='ml', start_prompt="വോയ്‌സ് വഴി ചേർക്കാൻ അമർത്തുക", key='v1')
        with st.form("f1", clear_on_submit=True):
            item = st.text_input("Item Name", value=voice_text if voice_text else "")
            amt = st.number_input("Amount", min_value=0, value=None)
            if st.form_submit_button("SAVE"):
                if item and amt:
                    requests.post(FORM_URL, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                    st.success("സേവ് ചെയ്തു!")
                    st.rerun()
    with col2:
        if not df.empty: st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])

# --- 3. ANALYTICS & WHATSAPP (ഇവിടെയാണ് എറർ ശരിയാക്കിയത്) ---
elif menu == "📊 Smart Analytics & WhatsApp":
    st.title("📊 Analytics & WhatsApp Report")
    if not df.empty:
        total = df['Amount'].sum()
        
        # ഗ്രാഫ് (കളർ എറർ ശരിയാക്കി)
        fig = px.pie(df, values='Amount', names=df.columns[2], title="ചിലവുകൾ")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📲 Send Report to WhatsApp")
        report_msg = f"PAICHI REPORT\nDate: {datetime.now().strftime('%d-%m-%Y')}\nTotal: ₹ {total}"
        # ലിങ്ക് ശരിയാക്കി
        wa_url = f"https://wa.me/?text={requests.utils.quote(report_msg)}"
        
        if st.button("📲 WHATSAPP-ലേക്ക് അയക്കുക"):
            st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">ഇവിടെ ക്ലിക്ക് ചെയ്ത് വാട്സാപ്പ് തുറക്കൂ</div></a>', unsafe_allow_html=True)
    else:
        st.write("ഡാറ്റ ലഭ്യമല്ല.")

# --- 4. AI SCANNER ---
elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Scanner")
    file = st.file_uploader("ബില്ല് അപ്‌ലോഡ് ചെയ്യുക", type=['jpg', 'png', 'jpeg'])
    if file:
        img = Image.open(file)
        st.image(img, width=300)
        if st.button("SCAN NOW"):
            reader = load_ai_reader()
            if reader:
                res = reader.readtext(np.array(img))
                st.write("AI കണ്ടെത്തിയത്:", res[0][1] if res else "തുക കിട്ടിയില്ല.")
            else: st.error("AI സെറ്റപ്പിലാണ്, അല്പം കഴിഞ്ഞ് നോക്കൂ.")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
