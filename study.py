import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import random

# 1. ലിങ്കുകൾ (നിന്റെ പുതിയ ഷീറ്റും ഫോമും)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .total-box { 
        background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; 
        text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; 
        margin-bottom: 20px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    h1, h2, h3, label { color: black !important; font-weight: bold !important; }
    .stButton>button { 
        background-color: #000 !important; color: #FFD700 !important; 
        font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഡാറ്റ ഇൻപുട്ട് ഭാഗം
with st.form("my_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    item_val = col1.text_input("Item Name (സാധനം)")
    price_val = col2.number_input("Amount (തുക)", min_value=0)
    
    if st.form_submit_button("SAVE TO SHEET"):
        if item_val and price_val:
            # പുതിയ ഫോമിലെ കറക്റ്റ് ID-കൾ
            payload = {
                "entry.812300063": datetime.now().strftime("%Y-%m-%d"),
                "entry.685338308": item_val,
                "entry.464670068": str(price_val)
            }
            try:
                # ഡാറ്റ ഫോമിലേക്ക് അയക്കുന്നു
                response = requests.post(FORM_URL, data=payload)
                if response.status_code == 200:
                    st.success(f"സേവ് ചെയ്തു: {item_val}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("ഫോമിലേക്ക് ഡാറ്റ എത്തിയില്ല. ID മാറ്റം ഉണ്ടോ എന്ന് നോക്കണം.")
            except:
                st.error("Connection Error!")

st.write("---")

# ഡാറ്റ പ്രദർശനം
try:
    df = pd.read_csv(CSV_URL)
    if not df.empty:
        # കോളം ക്രമീകരണം
        df.columns = [f'C{i}' for i in range(len(df.columns))]
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        
        # ടോട്ടൽ തുക കാണിക്കുന്നു
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.subheader("📋 Recent History")
            # Item (Col2), Amount (Last Col)
            st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])
        with c2:
            st.subheader("📊 Distribution")
            fig = px.pie(df, values='Amount', names=df.columns[2], hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ഷീറ്റിൽ ഡാറ്റയൊന്നുമില്ല. ആദ്യത്തെ സാധനം ആഡ് ചെയ്യൂ!")
except:
    st.warning("ഷീറ്റിൽ നിന്ന് ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. അല്പസമയത്തിന് ശേഷം Refresh ചെയ്യുക.")

if st.button("🔄 Refresh Data"):
    st.rerun()
