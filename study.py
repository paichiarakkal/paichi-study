import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import random

# 1. നിന്റെ പുതിയ ഷീറ്റും ഫോം ലിങ്കും (പുതിയതിൽ നിന്നുള്ളത്)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,1000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# നിന്റെ ഒറിജിനൽ ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 3px solid #FFD700; margin-top: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000; color: #FFD700; border: 2px solid #FFD700; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | ആപ്പിൽ നിന്ന് തന്നെ വിവരങ്ങൾ ചേർക്കാം | ടോട്ടൽ തുക താഴെ കാണാം 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📊 Monthly Report", "⏰ Reminders"])

# ഡാറ്റ ലോഡ് ചെയ്യുന്നു (എല്ലാ മെനുവിലും ടോട്ടൽ അറിയാൻ വേണ്ടി)
try:
    df = pd.read_csv(CSV_URL)
    if not df.empty:
        df.columns = ['Timestamp', 'Date', 'Item', 'Amount'][:len(df.columns)]
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=['Timestamp', 'Date', 'Item', 'Amount'])

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.write(f"സ്വാഗതം ഫൈസൽ! നിലവിൽ ആകെ ചിലവ്: ₹ {df['Amount'].sum() if not df.empty else 0}")
    st.write("താഴെയുള്ള മെനുവിൽ നിന്ന് Expenses തിരഞ്ഞെടുക്കുക.")

elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Add New Expense")
        # ഗൂഗിൾ ഫോം ഫോട്ടോ ഒഴിവാക്കി, നേരിട്ട് ഇൻപുട്ട് ബോക്സുകൾ നൽകി
        with st.form("my_form", clear_on_submit=True):
            item_val = st.text_input("സാധനം (Item Name)")
            price_val = st.number_input("തുക (Amount)", min_value=0)
            
            if st.form_submit_button("SAVE TO SHEET"):
                if item_val and price_val:
                    # പുതിയ ഫോമിലെ ഐഡികൾ
                    payload = {
                        "entry.206977218": datetime.now().strftime("%Y-%m-%d"),
                        "entry.1989669677": item_val,
                        "entry.483984534": str(price_val)
                    }
                    try:
                        requests.post(FORM_URL, data=payload)
                        st.success(f"സേവ് ചെയ്തു: {item_val}")
                        st.rerun()
                    except:
                        st.error("Error!")

    with col2:
        st.subheader("📊 Summary & Graph")
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            # വിഭജനം കാണിക്കുന്ന ഗ്രാഫ്
            fig = px.pie(df, values='Amount', names='Item', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    st.subheader("📋 Expense History")
    if not df.empty:
        # പുതിയ എൻട്രികൾ മുകളിൽ കാണാൻ തിരിച്ചിടുന്നു
        st.table(df[['Item', 'Amount']].tail(10).iloc[::-1])

elif menu == "📊 Monthly Report":
    st.title("📊 Monthly Report")
    if not df.empty:
        st.bar_chart(df.set_index('Item')['Amount'])
    else:
        st.info("റിപ്പോർട്ട് കാണിക്കാൻ ഡാറ്റയില്ല.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
