import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import random

# 1. ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,1000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="Family Expense", layout="wide")

# ക്ലീൻ ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 30px; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    .stButton>button { background-color: #000; color: #FFD700; border-radius: 10px; border: 2px solid #FFD700; width: 100%; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ആദ്യം തന്നെ ടോട്ടൽ കാണിക്കുന്നു
try:
    df = pd.read_csv(CSV_URL)
    if not df.empty:
        df.columns = ['Timestamp', 'Date', 'Item', 'Amount'][:len(df.columns)]
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
except:
    pass

# ഇൻപുട്ട് ഭാഗം - ഫോമിന്റെ ഫോട്ടോ ഒന്നും വരില്ല, വെറും ബോക്സുകൾ മാത്രം
st.subheader("➕ Add New Item")
with st.form("my_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    item_input = col1.text_input("Item (സാധനം)")
    price_input = col2.number_input("Amount (തുക)", min_value=0)
    
    if st.form_submit_button("SAVE"):
        if item_input and price_input:
            payload = {
                "entry.206977218": datetime.now().strftime("%Y-%m-%d"),
                "entry.1989669677": item_input,
                "entry.483984534": str(price_input)
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success(f"{item_input} saved!")
                st.rerun()
            except:
                st.error("Error!")

st.write("---")

# ഹിസ്റ്ററി കാണിക്കുന്ന ഭാഗം
if 'df' in locals() and not df.empty:
    st.subheader("📋 Recent Items")
    # വെറും Item, Amount മാത്രം കാണിക്കുന്നു
    display_df = df[['Item', 'Amount']].tail(10).iloc[::-1] 
    st.table(display_df) 
