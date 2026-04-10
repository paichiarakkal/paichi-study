import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. AI ലോഡർ (ബിൽ സ്കാൻ ചെയ്യാൻ)
@st.cache_resource
def load_ai_reader():
    import easyocr
    return easyocr.Reader(['en'])

# 2. നിന്റെ ഗൂഗിൾ ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Super AI Hub", layout="wide")

# 3. പ്രീമിയം ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; border-radius: 10px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .wa-button { background-color: #25D366 !important; color: white !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ഡാറ്റ ലോഡ് ചെയ്യുന്ന ഫംഗ്ഷൻ
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df[df['Amount'] > 0]
    except: return pd.DataFrame()

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI AI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Voice & Manual)", "📊 Smart Analytics & WhatsApp", "📸 AI Bill Scanner", "⏰ Reminders"])

df = load_data()

# --- 1. HOME ---
if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("നിന്റെ ഫാമിലി ഹബ്ബ് ഇപ്പോൾ വോയ്‌സ് കമാൻഡും AI സ്കാനറും ഉപയോഗിച്ച് കൂടുതൽ സ്മാർട്ടായിരിക്കുന്നു.")
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total Balance Used: ₹ {total:,.2f}</div>', unsafe_allow_html=True)

# --- 2. EXPENSES (VOICE & MANUAL) ---
elif menu == "💰 Expenses (Voice & Manual)":
    st.title("💵 Add New Expense")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎤 Voice Input")
        st.write("മൈക്കിൽ അമർത്തി സാധനത്തിന്റെ പേര് പറയുക:")
        voice_text = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
        
        with st.form("manual_entry", clear_on_submit=True):
            item = st.text_input("Item Name", value=voice_text if voice_text else "")
            amt = st.number_input("Amount", min_value=0, value=None, placeholder="0")
            if st.form_submit_button("SAVE TO SHEET"):
                if item and amt:
                    payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                    requests.post(FORM_URL, data=payload)
                    st.success(f"{item} സേവ് ചെയ്തു!")
                    st.rerun()

    with col2:
        st.subheader("📋 Recent List")
        if not df.empty:
            st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])

# --- 3. ANALYTICS & WHATSAPP ---
elif menu == "📊 Smart Analytics & WhatsApp":
    st.title("📊 Expense Analytics")
    if not df.empty:
        total = df['Amount'].sum()
        
        # ഗ്രാഫ് (Pie Chart)
        fig = px.pie(df, values='Amount', names=df.columns[2], 
                     title="ചിലവുകളുടെ വിഭജനം",
                     color_discrete_sequence=px.colors.sequential.Gold_r)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📲 WhatsApp Monthly Report")
        st.write("മാസാവസാന റിപ്പോർട്ട് വാട്സാപ്പിലേക്ക് അയക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക:")
        
        report_msg = f"PAICHI REPORT\nDate: {datetime.now().strftime('%d-%m-%Y')}\nTotal Expense: ₹ {total}\nSent from Family AI Hub."
        wa_url = f"https://wa.me/?text={requests.utils.quote(report_msg)}"
        
        if st.button("📲 SEND TO WHATSAPP"):
            st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">CONFIRM & SEND ON WHATSAPP</div></a>', unsafe_allow_html=True)

# --- 4. AI BILL SCANNER ---
elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Smart Scan")
    st.write("ബില്ലിന്റെ ഫോട്ടോ ഇട്ടാൽ AI തുക കണ്ടുപിടിക്കും.")
    file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    
    if file:
        img = Image.open(file)
        st.image(img, width=300)
        if st.button("🔍 START SCAN"):
            with st.spinner("AI പരിശോധിക്കുന്നു..."):
                try:
                    reader = load_ai_reader()
                    result = reader.readtext(np.array(img))
                    prices = []
                    for res in result:
                        txt = res[1].replace(',', '').replace(' ', '')
                        try: prices.append(float(txt))
                        except: continue
                    if prices:
                        detected = max(prices)
                        st.success(f"Detected: ₹ {detected}")
                    else: st.error("തുക കണ്ടെത്താനായില്ല.")
                except: st.error("AI ലോഡ് ആയിട്ടില്ല. അല്പം കഴിഞ്ഞ് നോക്കൂ.")

st.sidebar.write("---")
st.sidebar.write("PAICHI Super AI - Faisal")
