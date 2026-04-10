import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# 1. നിന്റെ പുതിയ ശരിയായ ലിങ്കുകൾ (അപ്‌ഡേറ്റ് ചെയ്തത്)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 3px solid #FFD700; margin-top: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | ആപ്പിൽ നിന്ന് തന്നെ വിവരങ്ങൾ ചേർക്കാം | ടോട്ടൽ തുക താഴെ കാണാം 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📊 Monthly Report", "⏰ Reminders"])

# ഷീറ്റിൽ നിന്ന് ഡാറ്റ എടുക്കുന്ന ഭാഗം
def get_data():
    try:
        data = pd.read_csv(CSV_URL)
        if not data.empty:
            # കോളങ്ങൾ ക്രമീകരിക്കുന്നു
            data.columns = [f'Col{i}' for i in range(len(data.columns))]
            data.rename(columns={data.columns[2]: 'Item', data.columns[-1]: 'Amount'}, inplace=True)
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
            return data
    except:
        return pd.DataFrame()

df = get_data()

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.write("സ്വാഗതം ഫൈസൽ! താഴെയുള്ള മെനുവിൽ നിന്ന് Expenses തിരഞ്ഞെടുക്കുക.")

elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Add New Expense")
        # ഗൂഗിൾ ഫോമിന് പകരം നമ്മൾ തന്നെ ഉണ്ടാക്കിയ ഇൻപുട്ട് ബോക്സുകൾ
        with st.form("add_expense_form", clear_on_submit=True):
            item_name = st.text_input("സാധനം (Item Name)")
            item_amount = st.number_input("തുക (Amount)", min_value=0)
            
            if st.form_submit_button("SAVE TO SHEET"):
                if item_name and item_amount:
                    # നിന്റെ പുതിയ ഫോമിലെ കറക്റ്റ് ID-കൾ
                    payload = {
                        "entry.812300063": datetime.now().strftime("%Y-%m-%d"),
                        "entry.685338308": item_name,
                        "entry.464670068": str(item_amount)
                    }
                    try:
                        r = requests.post(FORM_URL, data=payload)
                        if r.status_code == 200:
                            st.success(f"സേവ് ചെയ്തു: {item_name}")
                            st.rerun()
                        else:
                            st.error("സേവ് ചെയ്യാൻ പറ്റിയില്ല!")
                    except:
                        st.error("കണക്ഷൻ എറർ!")

    with col2:
        st.subheader("📋 Expense History")
        if st.button('🔄 Refresh Data'):
            st.rerun()
            
        if not df.empty:
            # ടോട്ടൽ തുക
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            # ലിസ്റ്റ് കാണിക്കുന്നു
            st.table(df[['Item', 'Amount']].tail(10).iloc[::-1])
        else:
            st.info("ഡാറ്റയൊന്നുമില്ല. ഇടത് വശത്ത് വിവരങ്ങൾ ചേർക്കുക.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

else:
    st.title(menu)
    st.write("ഈ സെക്ഷൻ റെഡിയായി വരുന്നു...")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
