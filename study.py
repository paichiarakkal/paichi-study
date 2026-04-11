import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. നിങ്ങൾ നൽകിയ പുതിയ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfAsUoTDzCoAij8_2euuWhWJZRDe4TqEhx2TqWeBRNIqj2rjA/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# 2. ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: #E8E8E8 !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold !important; width: 100%; border-radius: 12px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

def process_voice(text):
    num_map = {'ഒന്ന്': '1', 'രണ്ട്': '2', 'മൂന്ന്': '3', 'നാല്': '4', 'അഞ്ച്': '5', 'പത്ത്': '10', 'ഇരുപത്': '20', 'അമ്പത്': '50', 'നൂറ്': '100'}
    words = text.split()
    item, amt = "", None
    for word in words:
        if word.isdigit(): amt = int(word)
        elif word in num_map: amt = int(num_map[word])
        else: item += word + " "
    return item.strip(), amt

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            # കോളങ്ങൾ ക്ലീൻ ചെയ്യുന്നു
            for col in df.columns:
                if any(x in col for x in ['Debit', 'Credit', 'Amount']):
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# സൈഡ്‌ബാർ
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

# --- 🏠 Dashboard ---
if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    if not df.empty:
        # ചിലവായ തുക (Debit) മാത്രം സ്ക്രീനിൽ കാണിക്കുന്നു
        debit_cols = [c for c in df.columns if 'Debit' in c]
        total_spent = df[debit_cols[0]].sum() if debit_cols else 0
        st.markdown(f'<div class="total-box">ചിലവായ തുക: ₹ {total_spent:,.2f}</div>', unsafe_allow_html=True)
    else:
        st.info("ഡാറ്റ ലോഡ് ചെയ്യാൻ Refresh ചെയ്യൂ.")

# --- 💰 Add Entry ---
elif menu == "💰 Add Entry":
    st.title("Smart Data Input") #
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    auto_item, auto_amt = process_voice(v_in) if v_in else ("", None)

    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item)
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
        # Debit/Credit തിരഞ്ഞെടുക്കാനുള്ള ഓപ്ഷൻ
        entry_type = st.radio("Type:", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                # ഫോം ഫീൽഡുകൾ അനുസരിച്ചുള്ള പേലോഡ്
                payload = {
                    "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.1896057694": item,
                    "entry.1570426033": str(amt) if "Debit" in entry_type else "0", 
                    "entry.111222333": str(amt) if "Credit" in entry_type else "0"
                }
                requests.post(FORM_URL_API, data=payload)
                st.success(f"{item} സേവ് ചെയ്തു! ✅")

# --- 💬 Logs ---
elif menu == "💬 Logs":
    st.title("History") #
    if st.button("🔄 Refresh Data"): st.rerun()
    df = load_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI v16.1 | Design by Faisal")
