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
    import easyocr
    return easyocr.Reader(['en'])

# 2. ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Super Hub", layout="wide")

# 3. ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
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
menu = st.sidebar.selectbox("Menu", ["💰 Expenses", "📊 Smart Analytics", "📸 AI Scanner", "⏰ Reminders"])

df = load_data()

# --- 1. EXPENSE & VOICE SECTION ---
if menu == "💰 Expenses":
    st.title("💵 Expense & Voice Entry")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Add Entry")
        st.write("🎤 വോയ്‌സ് വഴി ചേർക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക:")
        text_from_voice = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='speech')
        
        with st.form("manual_form", clear_on_submit=True):
            item_name = st.text_input("Item Name", value=text_from_voice if text_from_voice else "")
            item_amount = st.number_input("Amount", min_value=0, value=None)
            if st.form_submit_button("SAVE DATA"):
                if item_name and item_amount:
                    payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item_name, "entry.1570426033": str(item_amount)}
                    requests.post(FORM_URL, data=payload)
                    st.success("സേവ് ചെയ്തു!")
                    st.rerun()

    with col2:
        st.subheader("📋 Recent Entries")
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])

# --- 2. ANALYTICS & WHATSAPP SECTION ---
elif menu == "📊 Smart Analytics":
    st.title("📊 Expense Analytics")
    if not df.empty:
        total = df['Amount'].sum()
        
        # ഗ്രാഫ്
        fig = px.pie(df, values='Amount', names=df.columns[2], title="ചിലവുകളുടെ തോത്",
                     color_discrete_sequence=px.colors.sequential.Gold_r)
        st.plotly_chart(fig, use_container_width=True)
        
        # വാട്സാപ്പ് റിപ്പോർട്ട്
        st.write("---")
        st.subheader("📲 WhatsApp Monthly Report")
        phone_number = "971XXXXXXXXX" # നിന്റെ ദുബായ് നമ്പർ ഇവിടെ നൽകാം
        msg = f"PAICHI HUB REPORT\nDate: {datetime.now().strftime('%d-%m-%Y')}\nTotal Expense: AED {total}\nCheck the app for details!"
        
        # WhatsApp Link Generation
        wa_url = f"https://wa.me/{phone_number}?text={requests.utils.quote(msg)}"
        
        if st.button("SEND REPORT TO WHATSAPP"):
            st.markdown(f'<a href="{wa_url}" target="_blank">Click here to confirm and Send WhatsApp</a>', unsafe_allow_html=True)

# --- 3. AI SCANNER ---
elif menu == "📸 AI Scanner":
    st.title("📸 AI Bill Scanner")
    img_file = st.file_uploader("Upload Bill", type=['jpg', 'png', 'jpeg'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300)
        if st.button("RUN AI SCAN"):
            reader = load_ai_reader()
            result = reader.readtext(np.array(img))
            prices = [float(res[1].replace(',', '')) for res in result if res[1].replace(',', '').replace('.', '').isdigit()]
            if prices:
                st.success(f"Detected Amount: {max(prices)}")
            else: st.warning("Could not find amount.")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v2.0 - Faisal")
