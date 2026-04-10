import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import random

# 1. ലിങ്കുകൾ (നിന്റെ പുതിയ ഫോം ലിങ്ക് അനുസരിച്ചുള്ളത്)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv&x={random.randint(1,1000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeF7QQUyWqBk_WZ127EMsvM33WtgpQPcJ6cQ5VDdulzLG7FhQ/formResponse"

st.set_page_config(page_title="Family Expense Tracker", layout="wide")

# ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഡാറ്റ ഇൻപുട്ട്
with st.expander("➕ പുതിയ ചെലവ് ചേർക്കുക", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        item_input = col1.text_input("Item Name (സാധനം)")
        price_input = col2.number_input("Amount (തുക)", min_value=0)
        
        if st.form_submit_button("Save to Google Sheet"):
            if item_input and price_input:
                today = datetime.now().strftime("%Y-%m-%d")
                
                # നിന്റെ പുതിയ ലിങ്കിൽ നിന്നുള്ള കൃത്യമായ ഐഡികൾ:
                payload = {
                    "entry.2064560731": today,       # Date
                    "entry.1014167909": item_input,  # Item
                    "entry.362153839": str(price_input) # Amount
                }
                
                try:
                    # ഗൂഗിൾ ഫോം വഴി ഡാറ്റ അയക്കുന്നു
                    requests.post(FORM_URL, data=payload)
                    st.success(f"സേവ് ചെയ്തു: {item_input}")
                    st.balloons()
                    st.rerun()
                except:
                    st.error("സേവ് ചെയ്യാൻ പറ്റിയില്ല!")

st.write("---")

# പ്രദർശനം
try:
    df = pd.read_csv(CSV_URL)
    if not df.empty:
        # കോളം പേരുകൾ സെറ്റ് ചെയ്യുന്നു
        df.columns = ['Timestamp', 'Date', 'Item', 'Amount'][:len(df.columns)]
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna(subset=['Amount']) # ശൂന്യമായവ ഒഴിവാക്കാൻ
        
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📋 ഹിസ്റ്ററി")
            st.dataframe(df.tail(10), use_container_width=True)
        with c2:
            st.subheader("📊 വിഭജനം")
            fig = px.pie(df, values='Amount', names='Item', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
except:
    st.info("ഡാറ്റ ലോഡ് ചെയ്യുന്നു...")
