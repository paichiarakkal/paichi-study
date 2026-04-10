import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np

# AI ലൈബ്രറി ലോഡ് ചെയ്യുന്ന ഭാഗം - എറർ ഒഴിവാക്കാൻ try/except ചേർത്തു
try:
    import easyocr
    @st.cache_resource
    def load_ai():
        return easyocr.Reader(['en'])
except Exception as e:
    st.sidebar.error("AI സിസ്റ്റം റെഡിയായിട്ടില്ല.")

# നിന്റെ ശരിയായ ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ സെറ്റിംഗ്സ് (നീ അയച്ച ഫോട്ടോയിലെ പോലെ)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #F9D976, #F39C12); color: #000; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 20px; text-align: center; font-size: 38px; font-weight: bold; border: 4px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; font-family: 'Arial'; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; border-radius: 10px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു - ഇത് ലളിതമാക്കി
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.radio("Select Option:", ["💰 Expense History", "➕ Add Expense", "📸 AI Bill Scan"])

if menu == "💰 Expense History":
    st.title("💰 Expense History")
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            df = df[df['Amount'] > 0]
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            # ഹിസ്റ്ററി ടേബിൾ
            display_df = df.iloc[:, [2, -1]].tail(15).iloc[::-1]
            display_df.columns = ['Item', 'Amount']
            st.table(display_df)
    except:
        st.info("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. Refresh ചെയ്യുക.")

elif menu == "➕ Add Expense":
    st.title("➕ Add New Entry")
    with st.form("manual_form", clear_on_submit=True):
        item_name = st.text_input("സാധനം (Item Name)")
        item_amount = st.number_input("തുക (Amount)", min_value=0, value=None, placeholder="0")
        
        if st.form_submit_button("SAVE DATA"):
            if item_name and item_amount:
                payload = {
                    "entry.1069832729": datetime.now().strftime("%Y-%m-%d"),
                    "entry.1896057694": item_name,
                    "entry.1570426033": str(item_amount)
                }
                requests.post(FORM_URL, data=payload)
                st.success(f"{item_name} സേവ് ചെയ്തു!")
                st.rerun()

elif menu == "📸 AI Bill Scan":
    st.title("📸 AI Smart Scanner")
    st.write("ബില്ലിന്റെ ഫോട്ടോ നൽകുക.")
    img_file = st.file_uploader("Upload Bill Image", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300)
        
        if st.button("🔍 START SCANNING"):
            try:
                reader = load_ai()
                with st.spinner("AI ബില്ല് പരിശോധിക്കുന്നു..."):
                    result = reader.readtext(np.array(img))
                    prices = []
                    for res in result:
                        txt = res[1].replace(',', '').replace(' ', '')
                        try: prices.append(float(txt))
                        except: continue
                    
                    if prices:
                        st.success(f"തുക കണ്ടെത്തി: ₹ {max(prices)}")
                        # ബാക്കി സേവിംഗ്സ് ഓപ്ഷൻ ഇവിടെ വരും
                    else:
                        st.warning("തുക കിട്ടിയില്ല, നേരിട്ട് അടിക്കുക.")
            except:
                st.error("AI ലോഡ് ആകാൻ കുറച്ചു സമയം കൂടി നൽകൂ.")

st.sidebar.write("---")
if st.sidebar.button("🔄 Refresh App"):
    st.rerun()
