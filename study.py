import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഡാറ്റ സേവ് ചെയ്യൽ
with st.form("my_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    item_val = col1.text_input("Item Name (സാധനം)")
    
    # ഇവിടെയാണ് മാറ്റം വരുത്തിയത്: value=None കൊടുത്താൽ ആ പഴയ 0 അവിടെ കാണില്ല
    price_val = col2.number_input("Amount (തുക)", min_value=0, value=None, placeholder="Amount അടിക്കുക")
    
    if st.form_submit_button("SAVE TO SHEET"):
        if item_val and price_val:
            payload = {
                "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                "entry.1896057694": item_val,                             
                "entry.1570426033": str(price_val)                       
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success(f"സേവ് ചെയ്തു: {item_val}")
                st.rerun()
            except:
                st.error("Error!")

st.write("---")

# ലിസ്റ്റ് കാണിക്കുന്ന ഭാഗം
try:
    df = pd.read_csv(CSV_URL)
    if not df.empty:
        df.columns = [f'C{i}' for i in range(len(df.columns))]
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        df = df[df['Amount'] > 0]
        
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        st.subheader("📋 Recent History")
        if not df.empty:
            display_df = df.iloc[:, [2, -1]].tail(10).iloc[::-1]
            display_df.columns = ['സാധനം', 'തുക']
            st.table(display_df)
except:
    st.info("Refresh ചെയ്യുക.")

if st.button("🔄 Refresh Data"):
    st.rerun()
