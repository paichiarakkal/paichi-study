import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import random

# ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv&x={random.randint(1,1000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeF7QQUyWqBk_WZ127EMsvM33WtgpQPcJ6cQ5VDdulzLG7FhQ/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

with st.expander("➕ പുതിയ ചെലവ് ചേർക്കുക", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        item_input = col1.text_input("Item Name (സാധനം)")
        price_input = col2.number_input("Amount (തുക)", min_value=0)
        today = datetime.now().strftime("%Y-%m-%d")
        
        submit = st.form_submit_button("Save to Google Sheet")
        
        if submit:
            if item_input and price_input:
                form_data = {
                    "entry.2064560731": today,
                    "entry.1014167909": item_input,
                    "entry.362153839": str(price_input)
                }
                try:
                    requests.post(FORM_URL, data=form_data)
                    st.success(f"സേവ് ചെയ്തു: {item_input} - ₹{price_input}")
                    st.balloons()
                    st.rerun()
                except:
                    st.error("സേവ് ചെയ്യാൻ പറ്റിയില്ല!")

st.write("---")

try:
    df = pd.read_csv(CSV_URL)
    df.columns = ['Timestamp', 'Date', 'Item', 'Amount'][:len(df.columns)]
    
    # ശൂന്യമായ വരികൾ ഒഴിവാക്കുന്നു
    df = df.dropna(subset=['Amount'])
    
    total = pd.to_numeric(df['Amount'], errors='coerce').sum()
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
