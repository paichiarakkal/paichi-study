import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# 1. നിന്റെ കറക്റ്റ് ലിങ്കുകൾ
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
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { 
        background-color: #000 !important; color: #FFD700 !important; 
        font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഡാറ്റ സേവ് ചെയ്യാനുള്ള ഭാഗം
with st.form("my_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    item_val = col1.text_input("Item Name (സാധനം)")
    price_val = col2.number_input("Amount (തുക)", min_value=0)
    
    if st.form_submit_button("SAVE TO SHEET"):
        if item_val and price_val:
            # നീ അയച്ച ലിങ്കിലെ ശരിക്കുള്ള ID-കൾ
            payload = {
                "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                "entry.1896057694": item_val,                             
                "entry.1570426033": str(price_val)                       
            }
            try:
                response = requests.post(FORM_URL, data=payload)
                if response.status_code == 200:
                    st.success(f"സേവ് ചെയ്തു: {item_val}")
                    st.rerun()
                else:
                    st.error("Error: ഡാറ്റ പോയില്ല!")
            except:
                st.error("Connection Error!")

st.write("---")

# ഡാറ്റ ഷീറ്റിൽ നിന്ന് എടുക്കുന്നു
try:
    # ഇവിടെ നമ്പറുകൾ വരാൻ pandas കൃത്യമായി ഉപയോഗിക്കുന്നു
    df = pd.read_csv(CSV_URL)
    
    if not df.empty:
        # കോളങ്ങൾക്ക് പേര് നൽകുന്നു
        df.columns = [f'Col{i}' for i in range(len(df.columns))]
        
        # പ്രധാന ഭാഗം: അവസാന കോളത്തെ നമ്പറാക്കി മാറ്റുന്നു (0 ഒഴിവാക്കാൻ)
        df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
        
        # തുക കൂട്ടുന്നു
        total_sum = df['Amount'].sum()
        
        # ടോട്ടൽ ബോക്സ്
        st.markdown(f'<div class="total-box">Total: ₹ {total_sum:,.2f}</div>', unsafe_allow_html=True)
        
        st.subheader("📋 Recent History")
        # Item (Col 2), Amount (അവസാന കോളം)
        display_df = df.iloc[:, [2, -1]].tail(10).iloc[::-1]
        display_df.columns = ['സാധനം', 'തുക']
        st.table(display_df)
    else:
        st.info("ഷീറ്റിൽ ഡാറ്റയൊന്നുമില്ല.")
except Exception as e:
    st.warning("ഡാറ്റ അപ്‌ഡേറ്റ് ആകുന്നു... 5 സെക്കൻഡ് കഴിഞ്ഞ് Refresh ബട്ടൺ അമർത്തുക.")

if st.button("🔄 Refresh List"):
    st.rerun()
