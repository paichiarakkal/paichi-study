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

# 2. നിന്റെ ലിങ്കുകൾ (Updated)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Super Hub", layout="wide")

# 3. ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
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

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | വോയ്‌സ് വഴിയോ നേരിട്ടോ വിവരങ്ങൾ സുരക്ഷിതമായി ചേർക്കാം 📢</div></div>', unsafe_allow_html=True)

def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df[df['Amount'] > 0]
    except: return pd.DataFrame()

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add Entry)", "📊 Smart Analytics & WhatsApp", "📸 AI Bill Scanner", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# --- 1. HOME ---
if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("പൈച്ചി ഫാമിലി ഹബ്ബിലേക്ക് സ്വാഗതം. ഡാറ്റ ചേർക്കാൻ Expenses പേജിൽ പോകുക.")

# --- 2. EXPENSES (ഷീറ്റും ഗൂഗിൾ ഫോമും പൂർണ്ണമായും ഒഴിവാക്കി) ---
elif menu == "💰 Expenses (Add Entry)":
    st.title("💵 Add New Entry")
    st.write("🎤 വോയ്‌സ് വഴി ചേർക്കാൻ മൈക്കിൽ അമർത്തുക:")
    
    # വോയ്‌സ് ഇൻപുട്ട്
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice_input')
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # മാനുവൽ ഇൻപുട്ട് ഫോം
    with st.container():
        st.markdown('<div style="background-color: rgba(255,255,255,0.2); padding: 30px; border-radius: 20px; border: 2px solid #000;">', unsafe_allow_html=True)
        with st.form("quick_add_form", clear_on_submit=True):
            item = st.text_input("സാധനത്തിന്റെ പേര് (Item Name)", value=v_in if v_in else "")
            amt = st.number_input("തുക (Amount)", min_value=0, value=None, placeholder="0")
            if st.form_submit_button("SAVE TO CLOUD"):
                if item and amt:
                    requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                    st.success(f"{item} വിജയകരമായി സേവ് ചെയ്തു!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ANALYTICS (പാസ്‌വേഡ് ഉണ്ടെങ്കിൽ മാത്രം ഷീറ്റും ഗ്രാഫും കാണാം) ---
elif menu == "📊 Smart Analytics & WhatsApp":
    if "is_unlocked" not in st.session_state: st.session_state["is_unlocked"] = False
    
    if not st.session_state["is_unlocked"]:
        st.title("🔐 Secure Section")
        pwd = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
        if st.button("UNLOCK"):
            if pwd == "1234":
                st.session_state["is_unlocked"] = True
                st.rerun()
            else: st.error("തെറ്റായ പാസ്‌വേഡ്!")
    else:
        st.title("📊 History & Reports")
        if st.sidebar.button("🔒 Lock Section"):
            st.session_state["is_unlocked"] = False
            st.rerun()
            
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total Balance: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("ചിലവ് വിശകലനം")
                fig = px.pie(df, values='Amount', names=df.columns[2], hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                st.subheader("പഴയ ലിസ്റ്റ് (History)")
                st.table(df.iloc[:, [2, -1]].tail(20).iloc[::-1])
            
            st.markdown("---")
            wa_text = f"PAICHI HUB REPORT\nTotal: ₹{total}"
            wa_url = f"https://wa.me/?text={requests.utils.quote(wa_text)}"
            if st.button("📲 SEND TO WHATSAPP"):
                st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">CONFIRM ON WHATSAPP</div></a>', unsafe_allow_html=True)

# --- 4. AI SCANNER ---
elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Smart Scan")
    file = st.file_uploader("Upload Image", type=['jpg','png','jpeg'])
    if file and st.button("SCAN NOW"):
        reader = load_ai_reader()
        if reader:
            res = reader.readtext(np.array(Image.open(file)))
            if res: st.success(f"Detected: {res[0][1]}")

# --- OTHERS ---
elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

else:
    st.title(menu)
    st.write("ഈ സെക്ഷൻ ഉടൻ അപ്‌ഡേറ്റ് ചെയ്യും...")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal | PAICHI AI")
