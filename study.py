import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# 1. നിന്റെ ശരിയായ ലിങ്കുകൾ (Updated with your IDs)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഒറിജിനൽ ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-top: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | ആപ്പിൽ നിന്ന് തന്നെ വിവരങ്ങൾ ചേർക്കാം | ടോട്ടൽ തുക താഴെ കാണാം 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📊 Monthly Report", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# ഡാറ്റ ലോഡ് ചെയ്യുന്ന ഫംഗ്ഷൻ
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            # തുക പൂജ്യത്തിന് മുകളിലുള്ളവ മാത്രം കാണിക്കുന്നു
            df = df[df['Amount'] > 0]
            return df
    except:
        return pd.DataFrame()

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.write("സ്വാഗതം ഫൈസൽ! താഴെയുള്ള മെനുവിൽ നിന്ന് Expenses തിരഞ്ഞെടുക്കുക.")

elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Add New Expense")
        with st.form("entry_form", clear_on_submit=True):
            item_name = st.text_input("സാധനം (Item Name)")
            # value=None നൽകിയത് കൊണ്ട് '0' തനിയെ മാറും
            item_amount = st.number_input("തുക (Amount)", min_value=0, value=None, placeholder="Amount അടിക്കുക")
            
            if st.form_submit_button("SAVE TO SHEET"):
                if item_name and item_amount:
                    # നിന്റെ ഗൂഗിൾ ഫോം ഐഡികൾ ഇവിടെ കൃത്യമായി ചേർത്തിട്ടുണ്ട്
                    payload = {
                        "entry.1069832729": datetime.now().strftime("%Y-%m-%d"),
                        "entry.1896057694": item_name,
                        "entry.1570426033": str(item_amount)
                    }
                    try:
                        requests.post(FORM_URL, data=payload)
                        st.success(f"സേവ് ചെയ്തു: {item_name}")
                        st.rerun()
                    except:
                        st.error("Error: കണക്ട് ചെയ്യാൻ പറ്റിയില്ല!")

    with col2:
        st.subheader("📋 Expense History")
        if st.button('🔄 Refresh List'):
            st.rerun()
            
        df = load_data()
        if df is not None and not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            display_df = df.iloc[:, [2, -1]].tail(10).iloc[::-1]
            display_df.columns = ['സാധനം', 'തുക']
            st.table(display_df)
        else:
            st.info("ഡാറ്റയൊന്നുമില്ല.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

else:
    st.title(menu)
    st.write("ഈ സെക്ഷൻ ഉടൻ റെഡിയാകും...")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
