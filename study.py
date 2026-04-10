import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# നിന്റെ കറക്റ്റ് ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഡാറ്റ സേവ് ചെയ്യാനുള്ള ഭാഗം
with st.form("my_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    item_val = col1.text_input("Item Name (സാധനം)")
    price_val = col2.number_input("Amount (തുക)", min_value=0)
    
    if st.form_submit_button("SAVE TO SHEET"):
        if item_name := item_val:
            # പുതിയ കണ്ടുപിടിച്ച ID-കൾ ഇവിടെ ചേർക്കുന്നു
            payload = {
                "entry.812300063": datetime.now().strftime("%Y-%m-%d"), # Date ID
                "entry.685338308": item_val,                             # Item ID
                "entry.464670068": str(price_val)                       # Amount ID
            }
            try:
                r = requests.post(FORM_URL, data=payload)
                if r.status_code == 200:
                    st.success(f"സേവ് ചെയ്തു: {item_val}")
                    st.balloons()
                else:
                    st.error("Error: ഫോമിലേക്ക് ഡാറ്റ പോയില്ല!")
            except:
                st.error("Connection Error!")

st.write("---")

# ഡാറ്റ കാണിക്കുന്ന ഭാഗം
try:
    df = pd.read_csv(CSV_URL)
    if not df.empty:
        df.columns = [f'C{i}' for i in range(len(df.columns))]
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        st.subheader("📋 Recent Purchases")
        st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])
except:
    st.info("ഡാറ്റ ലോഡ് ചെയ്യുന്നു... ആപ്പിൽ വിവരങ്ങൾ ചേർത്ത് 10 സെക്കൻഡ് കാത്തിരിക്കുക.")
