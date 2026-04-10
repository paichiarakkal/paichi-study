import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv"
# ഫോം സബ്മിറ്റ് ചെയ്യാനുള്ള ലിങ്ക്
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdy-v96B6XU3WvOCUKRJ3BLnyP7/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഡാറ്റ ഇൻപുട്ട് സെക്ഷൻ
with st.expander("➕ പുതിയ ചെലവ് ചേർക്കുക", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        item = col1.text_input("Item Name (സാധനം)")
        price = col2.number_input("Amount (തുക)", min_value=0)
        today = datetime.now().strftime("%Y-%m-%d")
        
        submit = st.form_submit_button("Save to Google Sheet")
        
        if submit:
            if item and price:
                # ഫോമിലെ എൻട്രി ഐഡികൾ (ഇതാണ് പൈത്തൺ ഉപയോഗിക്കുന്നത്)
                # സാധാരണയായി 'entry.ID' രൂപത്തിലായിരിക്കും ഇത്. 
                # നിന്റെ ഫോമിന് അനുസരിച്ചുള്ള ഏകദേശ ഐഡികൾ താഴെ നൽകുന്നു.
                form_data = {
                    "entry.1843187210": today,  # Date
                    "entry.1017830857": item,   # Item
                    "entry.1887019672": price   # Amount
                }
                try:
                    requests.post(FORM_URL, data=form_data)
                    st.success(f"സേവ് ചെയ്തു: {item} - ₹{price}")
                    st.balloons()
                except:
                    st.error("സേവ് ചെയ്യാൻ പറ്റിയില്ല, കണക്ഷൻ നോക്കുക.")

st.write("---")

# ചാർട്ടും ലിസ്റ്റും കാണിക്കാൻ
try:
    df = pd.read_csv(CSV_URL)
    total = pd.to_numeric(df.iloc[:, -1], errors='coerce').sum()
    st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📋 ഹിസ്റ്ററി")
        st.dataframe(df.tail(10), use_container_width=True) # അവസാന 10 എണ്ണം
    with c2:
        st.subheader("📊 വിഭജനം")
        fig = px.pie(df, values=df.columns[-1], names=df.columns[1], hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
except:
    st.info("ഡാറ്റ ലോഡ് ചെയ്യുന്നു...")

st.sidebar.write("Design by Faisal")
