import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np
from streamlit_mic_recorder import mic_recorder, speech_to_text

# 1. AI ലോഡർ
@st.cache_resource
def load_ai_reader():
    import easyocr
    return easyocr.Reader(['en'])

# 2. ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Voice Hub", layout="wide")

# 3. ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 4px solid #FFD700; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# സൈഡ്‌ബാർ
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📸 AI Bill Scanner", "⏰ Reminders"])

if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("ഇപ്പോൾ നിനക്ക് സംസാരിച്ചും ചിലവുകൾ രേഖപ്പെടുത്താം!")

elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Add Entry")
        
        # വോയ്‌സ് ഇൻപുട്ട് സെക്ഷൻ
        st.write("🎤 വോയ്‌സ് വഴി ചേർക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യുക:")
        text_input = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='speech')
        
        with st.form("manual_form", clear_on_submit=True):
            # വോയ്‌സ് വഴി കിട്ടിയ ടെക്സ്റ്റ് ഇവിടെ വരും
            val = text_input if text_input else ""
            item_name = st.text_input("സാധനം (Item Name)", value=val)
            item_amount = st.number_input("തുക (Amount)", min_value=0, value=None)
            
            if st.form_submit_button("SAVE TO SHEET"):
                if item_name and item_amount:
                    payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item_name, "entry.1570426033": str(item_amount)}
                    requests.post(FORM_URL, data=payload)
                    st.success("സേവ് ചെയ്തു!")
                    st.rerun()

    with col2:
        st.subheader("📋 History")
        try:
            df = pd.read_csv(CSV_URL)
            if not df.empty:
                df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
                total = df[df['Amount'] > 0]['Amount'].sum()
                st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
                st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])
        except: st.info("Loading...")

elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Smart Scanner")
    # (നേരത്തെ തന്ന അതേ AI Scanner കോഡ് ഇവിടെയും വരും)
    st.info("ബില്ലിന്റെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക.")

st.sidebar.write("---")
st.sidebar.write("Voice & AI by Faisal")
