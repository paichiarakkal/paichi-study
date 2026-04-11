import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold !important; border-radius: 12px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        return pd.read_csv(url)
    except: return None

# വോയ്‌സ് പ്രോസസ്സിംഗ് തിരുത്തിയത് (ValueError പരിഹരിച്ചു)
def process_voice(text):
    if not text: return "", None
    num_map = {'ഒന്ന്': 1, 'രണ്ട്': 2, 'മൂന്ന്': 3, 'നാല്': 4, 'അഞ്ച്': 5, 'പത്ത്': 10, 'ഇരുപത്': 20, 'അമ്പത്': 50, 'നൂറ്': 100}
    words = text.split()
    item, amt = "", None
    for word in words:
        if word.isdigit(): 
            amt = int(word)
        elif word in num_map: 
            amt = num_map[word]
        else: 
            item += word + " "
    return item.strip(), amt

st.sidebar.title("⚪ PAICHI AI")
menu = st.sidebar.selectbox("COMMANDS:", ["🏠 Dashboard", "💰 Add Entry", "💬 Logs"])

if menu == "🏠 Dashboard":
    st.title("Family Hub Dashboard")
    df = load_data()
    if df is not None and not df.empty:
        debit_col = df.columns[3] if len(df.columns) > 3 else df.columns[-1]
        df[debit_col] = pd.to_numeric(df[debit_col], errors='coerce').fillna(0)
        total_spent = df[debit_col].sum()
        st.markdown(f'<div class="total-box">ചിലവായ തുക: ₹ {total_spent:,.2f}</div>', unsafe_allow_html=True)
    else: st.info("ഡാറ്റ ലോഡ് ആകുന്നു...")

elif menu == "💰 Add Entry":
    st.title("Smart Data Input")
    # വോയ്‌സ് റെക്കോർഡർ
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ (ഉദാ: ചായ 10)...", key='voice')
    
    auto_item, auto_amt = "", None
    if v_in:
        auto_item, auto_amt = process_voice(v_in)

    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item)
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
        
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                payload = {
                    "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.2013476337": item,
                    "entry.400506732": str(amt)
                }
                res = requests.post(FORM_URL_API, data=payload)
                if res.status_code == 200 or res.status_code == 0:
                    st.success(f"{item} സേവ് ചെയ്തു! ✅")
                    st.cache_data.clear()
                else:
                    st.error("സേവ് ചെയ്യാൻ പറ്റിയില്ല.")

elif menu == "💬 Logs":
    st.title("History")
    df = load_data()
    if df is not None: st.dataframe(df, use_container_width=True)

st.sidebar.write("---")
st.sidebar.write("PAICHI v16.5 | 2026")
