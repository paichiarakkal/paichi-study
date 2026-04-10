import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. AI ബിൽ റീഡർ ലോഡർ
@st.cache_resource
def load_ai_reader():
    try:
        import easyocr
        return easyocr.Reader(['en'])
    except: return None

# 2. നിന്റെ ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Family Hub", layout="wide")

# 3. ഒറിജിനൽ ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് | വോയ്‌സ് കമാൻഡും AI സ്കാനറും ഇപ്പോൾ ലഭ്യമാണ് 📢</div></div>', unsafe_allow_html=True)

def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df[df['Amount'] > 0]
    except: return pd.DataFrame()

df = load_data()

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Voice & Manual)", "📊 Smart Analytics & WhatsApp", "📸 AI Bill Scanner", "⏰ Reminders"])

# --- 1. HOME ---
if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("താഴെയുള്ള മെനുവിൽ നിന്ന് നിങ്ങൾക്ക് വേണ്ടത് തിരഞ്ഞെടുക്കുക.")

# --- 2. EXPENSES (Voice & Manual - No List) ---
elif menu == "💰 Expenses (Voice & Manual)":
    st.title("💵 Add New Expense")
    st.write("🎤 വോയ്‌സ് വഴി ചേർക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക:")
    voice_input = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='v_exp')
    
    with st.form("entry_form", clear_on_submit=True):
        item_name = st.text_input("സാധനം (Item Name)", value=voice_input if voice_input else "")
        item_amount = st.number_input("തുക (Amount)", min_value=0, value=None, placeholder="Amount അടിക്കുക")
        
        if st.form_submit_button("SAVE TO SHEET"):
            if item_name and item_amount:
                payload = {
                    "entry.1069832729": datetime.now().strftime("%Y-%m-%d"),
                    "entry.1896057694": item_name,
                    "entry.1570426033": str(item_amount)
                }
                requests.post(FORM_URL, data=payload)
                st.success(f"സേവ് ചെയ്തു: {item_name}")

# --- 3. ANALYTICS & WHATSAPP (Password Protected) ---
elif menu == "📊 Smart Analytics & WhatsApp":
    if "ana_unlocked" not in st.session_state:
        st.session_state["ana_unlocked"] = False

    if not st.session_state["ana_unlocked"]:
        st.title("🔐 Secure Access")
        pwd = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
        if st.button("UNLOCK"):
            if pwd == "1234": # നിനക്ക് ഇഷ്ടമുള്ള പാസ്‌വേഡ് ഇവിടെ നൽകാം
                st.session_state["ana_unlocked"] = True
                st.rerun()
            else:
                st.error("തെറ്റായ പാസ്‌വേഡ്!")
    else:
        st.title("📊 Analysis & History")
        if st.button("🔒 Lock Section"):
            st.session_state["ana_unlocked"] = False
            st.rerun()

        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("ചിലവ് വിഭജനം")
                fig = px.pie(df, values='Amount', names=df.columns[2], hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📋 Expense History")
                st.table(df.iloc[:, [2, -1]].tail(15).iloc[::-1])
            
            st.markdown("---")
            st.subheader("📲 WhatsApp Report")
            report_msg = f"PAICHI HUB REPORT\nDate: {datetime.now().strftime('%d-%m-%Y')}\nTotal Expense: ₹ {total}"
            wa_link = f"https://wa.me/?text={requests.utils.quote(report_msg)}"
            if st.button("SEND TO WHATSAPP"):
                st.markdown(f'<a href="{wa_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">CONFIRM ON WHATSAPP</div></a>', unsafe_allow_html=True)

# --- 4. AI BILL SCANNER ---
elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Smart Scanner")
    file = st.file_uploader("ബില്ല് അപ്‌ലോഡ് ചെയ്യുക", type=['jpg', 'png', 'jpeg'])
    if file:
        img = Image.open(file)
        st.image(img, width=300)
        if st.button("🔍 SCAN BILL"):
            reader = load_ai_reader()
            if reader:
                with st.spinner("AI പരിശോധിക്കുന്നു..."):
                    result = reader.readtext(np.array(img))
                    if result:
                        st.success(f"Detected: {result[0][1]}")
                    else: st.warning("തുക കണ്ടെത്താനായില്ല.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

st.sidebar.write("---")
st.sidebar.write("Design & AI by Faisal")
