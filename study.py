import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np

# 1. AI ലൈബ്രറി ലോഡ് ചെയ്യുന്നു
@st.cache_resource
def load_ai_reader():
    import easyocr
    return easyocr.Reader(['en'])

# 2. നിന്റെ ലിങ്കുകൾ
# ഷീറ്റ് 1 (Expenses): gid=1126266048
# ഷീറ്റ് 2 (News): gid=0 (സാധാരണ ആദ്യ ഷീറ്റ് 0 ആയിരിക്കും, അല്ലെങ്കിൽ നിന്റെ ഷീറ്റിന്റെ gid ലിങ്കിൽ നിന്ന് നോക്കി മാറ്റുക)
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
NEWS_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=0&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Family Hub", layout="wide")

# 3. പ്രീമിയം ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; border: 2px solid #FFD700; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 20s linear infinite; font-size: 18px; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; margin-top: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# വാർത്ത ഷീറ്റിൽ നിന്ന് ലോഡ് ചെയ്യുന്നു
def load_news():
    try:
        news_df = pd.read_csv(NEWS_URL)
        return news_df.columns[0] # ആദ്യത്തെ സെല്ലിലെ വരി എടുക്കുന്നു
    except:
        return "📢 പൈച്ചി ഫാമിലി അസിസ്റ്റന്റ് ലോഡ് ആയിരിക്കുന്നു..."

current_news = load_news()

# ഡൈനാമിക് ന്യൂസ് ടിക്കർ
st.markdown(f'<div class="ticker-wrap"><div class="ticker">📢 {current_news} 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📸 AI Bill Scanner", "📊 Monthly Report", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# ഡാറ്റ ലോഡ് ചെയ്യുന്ന ഫംഗ്ഷൻ
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            df.columns = [f'Col{i}' for i in range(len(df.columns))]
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            df = df[df['Amount'] > 0]
            return df
    except:
        return pd.DataFrame()

# --- മെനു വിഭാങ്ങൾ ---

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.write(f"സ്വാഗതം ഫൈസൽ! നിന്റെ സ്മാർട്ട് ന്യൂസ് ടിക്കർ ഇപ്പോൾ ഷീറ്റുമായി കണക്ട് ചെയ്തിട്ടുണ്ട്.")

elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("➕ Add New Entry")
        with st.form("entry_form", clear_on_submit=True):
            item_name = st.text_input("സാധനം (Item Name)")
            item_amount = st.number_input("തുക (Amount)", min_value=0, value=None, placeholder="0")
            if st.form_submit_button("SAVE TO SHEET"):
                if item_name and item_amount:
                    payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item_name, "entry.1570426033": str(item_amount)}
                    requests.post(FORM_URL, data=payload)
                    st.success("സേവ് ചെയ്തു!")
                    st.rerun()
    with col2:
        st.subheader("📋 History")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])

elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Smart Scanner")
    st.write("ബില്ലിന്റെ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക, AI തുക തനിയെ കണ്ടെത്തും.")
    img_file = st.file_uploader("Choose Bill Image", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300)
        if st.button("🔍 START AI SCAN"):
            try:
                reader = load_ai_reader()
                with st.spinner("AI ബില്ല് വായിക്കുന്നു..."):
                    result = reader.readtext(np.array(img))
                    prices = []
                    for (bbox, text, prob) in result:
                        clean = text.replace(',', '').replace(' ', '').replace('Rs', '').replace('Total', '').replace('total', '')
                        try: prices.append(float(clean))
                        except: continue
                    if prices:
                        detected_amt = max(prices)
                        st.success(f"AI കണ്ടെത്തിയ തുക: ₹ {detected_amt}")
                        with st.form("ai_save"):
                            item = st.text_input("Item Name", value="AI Scanned Bill")
                            amt = st.number_input("Amount", value=float(detected_amt))
                            if st.form_submit_button("SAVE TO SHEET"):
                                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                                requests.post(FORM_URL, data=payload)
                                st.success("സേവ് ചെയ്തു!")
                    else: st.warning("തുക കണ്ടെത്താനായില്ല.")
            except Exception as e: st.error(f"AI Error: {e}")

else:
    st.title(menu)
    st.write("ഈ സെക്ഷൻ ഉടൻ റെഡിയാകും...")

st.sidebar.write("---")
st.sidebar.write("Design & AI by Faisal")
