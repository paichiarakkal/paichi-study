import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import random

# 1. ലിങ്കുകൾ (നിന്റെ ഷീറ്റും ഫോമും)
# തുക ഉടനെ മാറാൻ ഒരു random നമ്പർ കൂടി ലിങ്കിൽ ചേർക്കുന്നു
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv&x={random.randint(1,1000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeF7QQUyWqBk_WZ127EMsvM33WtgpQPcJ6cQ5VDdulzLG7FhQ/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# 2. ഡിസൈൻ (ഗോൾഡൻ & ബ്ലാക്ക് തീം)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# 3. പുതിയ ചെലവ് ചേർക്കാനുള്ള ഫോം
with st.expander("➕ പുതിയ ചെലവ് ചേർക്കുക", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        item_input = col1.text_input("Item Name (സാധനം)")
        price_input = col2.number_input("Amount (തുക)", min_value=0)
        today = datetime.now().strftime("%Y-%m-%d")
        
        submit = st.form_submit_button("Save to Google Sheet")
        
        if submit:
            if item_input and price_input:
                # നിന്റെ ഫോമിന് കൃത്യമായി മാച്ച് ആകുന്ന ഐഡികൾ
                form_data = {
                    "entry.2064560731": today,
                    "entry.1014167909": item_input,
                    "entry.362153839": price_input
                }
                try:
                    requests.post(FORM_URL, data=form_data)
                    st.success(f"സേവ് ചെയ്തു: {item_input} - ₹{price_input}")
                    st.balloons()
                    st.rerun() # ലിസ്റ്റ് ഉടനെ പുതുക്കാൻ
                except:
                    st.error("സേവ് ചെയ്യാൻ പറ്റിയില്ല! ഇന്റർനെറ്റ് ഉണ്ടെന്ന് ഉറപ്പാക്കുക.")

st.write("---")

# 4. ഷീറ്റിലെ ഡാറ്റ കാണിക്കാനുള്ള ഭാഗം
try:
    df = pd.read_csv(CSV_URL)
    
    # ഷീറ്റിലെ കോളങ്ങൾക്ക് പേര് നൽകുന്നു (Errors വരാതിരിക്കാൻ)
    if not df.empty:
        # നിന്റെ ഷീറ്റിലെ കോളങ്ങളുടെ എണ്ണത്തിന് അനുസരിച്ച് പേര് മാറ്റുക
        df.columns = ['Timestamp', 'Date', 'Item', 'Amount'][:len(df.columns)]
        
        # ടോട്ടൽ തുക കാണിക്കാൻ
        total = pd.to_numeric(df['Amount'], errors='coerce').sum()
        st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        # ടേബിളും ഗ്രാഫും
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📋 ഹിസ്റ്ററി (അവസാന 10 എണ്ണം)")
            st.dataframe(df.tail(10), use_container_width=True)
        with c2:
            st.subheader("📊 വിഭജനം")
            fig = px.pie(df, values='Amount', names='Item', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ഷീറ്റിൽ ഡാറ്റയൊന്നും കണ്ടില്ല.")

except Exception as e:
    st.error(f"ഡാറ്റ ലോഡ് ചെയ്യുന്നതിൽ പ്രശ്നമുണ്ട്. ഗൂഗിൾ ഷീറ്റ് 'Publish to Web' ആണെന്ന് ഉറപ്പാക്കുക.")

st.sidebar.write(f"Design by Faisal | Last Update: {datetime.now().strftime('%H:%M:%S')}")
