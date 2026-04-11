import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Balance Hub", layout="wide")

# ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .metric-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #FFD700; margin-bottom: 10px; }
    .balance-box { background: linear-gradient(to right, #000, #434343); color: #00FF00; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold !important; border-radius: 12px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        # എല്ലാ സംഖ്യാ കോളങ്ങളും ക്ലീൻ ചെയ്യുന്നു
        for col in df.columns:
            if any(x in col for x in ['Debit', 'Credit', 'Amount']):
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return None

def process_voice(text):
    if not text: return "", None
    num_map = {'ഒന്ന്': 1, 'രണ്ട്': 2, 'മൂന്ന്': 3, 'നാല്': 4, 'അഞ്ച്': 5, 'പത്ത്': 10, 'ഇരുപത്': 20, 'അമ്പത്': 50, 'നൂറ്': 100}
    words = text.split()
    item, amt = "", None
    for word in words:
        if word.isdigit(): amt = int(word)
        elif word in num_map: amt = num_map[word]
        else: item += word + " "
    return item.strip(), amt

st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("മെനു:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

# --- 🏠 Dashboard ---
if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    if df is not None and not df.empty:
        # നിങ്ങളുടെ ഷീറ്റിലെ കോളങ്ങൾ (Debit 4-ാമതും Credit 5-ാമതും ആണെന്ന് കരുതുന്നു)
        debit_val = df.iloc[:, 3].sum() # Debit Column
        credit_val = df.iloc[:, 4].sum() # Credit Column
        balance = credit_val - debit_val
        
        # ബാലൻസ് ഡിസ്‌പ്ലേ
        st.markdown(f'<div class="balance-box">ബാക്കി തുക: ₹ {balance:,.2f}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-box"><p style="color:#FFD700 !important;">ആകെ വരുമാനം</p><h3>₹ {credit_val:,.2f}</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><p style="color:#FFD700 !important;">ആകെ ചിലവ്</p><h3>₹ {debit_val:,.2f}</h3></div>', unsafe_allow_html=True)
    else: st.info("ഡാറ്റ ലോഡ് ആകുന്നു...")

# --- 💰 Add Entry ---
elif menu == "💰 Add Entry":
    st.title("Smart Data Input")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    auto_item, auto_amt = process_voice(v_in) if v_in else ("", None)

    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item)
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
        type_entry = st.radio("ഇനം:", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                # നിങ്ങൾ അയച്ച ഫോമിലെ ശരിയായ Entry ID-കൾ
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.400506732": str(amt) if "Debit" in type_entry else "0",
                    "entry.1360010991": str(amt) if "Credit" in type_entry else "0"
                }
                res = requests.post(FORM_URL_API, data=payload)
                if res.status_code == 200 or res.status_code == 0:
                    st.success(f"{item} - {type_entry} ആയി സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()

elif menu == "💬 Logs":
    st.title("History")
    df = load_data()
    if df is not None: st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI v16.7 | 2026")
