import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. നിങ്ങളുടെ പബ്ലിഷ് ചെയ്ത ഷീറ്റ് ലിങ്ക്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfAsUoTDzCoAij8_2euuWhWJZRDe4TqEhx2TqWeBRNIqj2rjA/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        # ഡാറ്റ കൃത്യമായി ലോഡ് ആകുന്നുണ്ടെന്ന് ഉറപ്പുവരുത്തുന്നു
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        data = pd.read_csv(url)
        return data
    except:
        return None # ഡാറ്റ ഇല്ലെങ്കിൽ None നൽകുന്നു

def process_voice(text):
    num_map = {'ഒന്ന്': '1', 'രണ്ട്': '2', 'മൂന്ന്': '3', 'നാല്': '4', 'അഞ്ച്': '5', 'പത്ത്': '10', 'ഇരുപത്': '20', 'അമ്പത്': '50', 'നൂറ്': '100'}
    words = text.split()
    item, amt = "", None
    for word in words:
        if word.isdigit(): amt = int(word)
        elif word in num_map: amt = int(num_map[word])
        else: item += word + " "
    return item.strip(), amt

# സൈഡ്‌ബാർ
st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

# --- 🏠 Dashboard ---
if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    
    # AttributeError ഒഴിവാക്കാൻ ഇവിടെ മാറ്റം വരുത്തി
    if df is not None and not df.empty:
        # Debit കോളം കണ്ടുപിടിക്കുന്നു
        debit_cols = [c for c in df.columns if 'Debit' in c]
        if debit_cols:
            df[debit_cols[0]] = pd.to_numeric(df[debit_cols[0]], errors='coerce').fillna(0)
            total_spent = df[debit_cols[0]].sum()
            st.markdown(f'<div class="total-box">ചിലവായ തുക: ₹ {total_spent:,.2f}</div>', unsafe_allow_html=True)
        else:
            st.warning("Debit കോളം കണ്ടെത്താനായില്ല.")
    else:
        st.error("ഡാറ്റ ലഭ്യമല്ല. ഷീറ്റിൽ വിവരങ്ങൾ ഉണ്ടെന്നും അത് പബ്ലിഷ് ചെയ്തിട്ടുണ്ടെന്നും ഉറപ്പാക്കുക.")

# --- 💰 Add Entry ---
elif menu == "💰 Add Entry":
    st.title("Smart Data Input")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    auto_item, auto_amt = process_voice(v_in) if v_in else ("", None)

    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item)
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
        entry_type = st.radio("Type:", ["Debit (ചിലവ്)", "Credit (വരുമാനം)"], horizontal=True)
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                payload = {
                    "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.1896057694": item,
                    "entry.1570426033": str(amt) if "Debit" in entry_type else "0",
                    "entry.111222333": "0" if "Debit" in entry_type else str(amt)
                }
                requests.post(FORM_URL_API, data=payload)
                st.success(f"{item} സേവ് ചെയ്തു! ✅")

# --- 💬 Logs ---
elif menu == "💬 Logs":
    st.title("History")
    df = load_data()
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("ചരിത്രം ലഭ്യമല്ല.")

st.sidebar.write("---")
st.sidebar.write(f"PAICHI v16.2 | 2026")
