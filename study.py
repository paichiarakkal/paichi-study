import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from PIL import Image
import numpy as np

# AI ലൈബ്രറി ലോഡ് ചെയ്യുന്നു
try:
    import easyocr
    # ഇത് ആദ്യമായി റൺ ചെയ്യുമ്പോൾ AI മോഡൽ ഡൗൺലോഡ് ചെയ്യാൻ അല്പം സമയമെടുക്കും
    @st.cache_resource
    def load_reader():
        return easyocr.Reader(['en'])
    reader = load_reader()
except Exception as e:
    st.error(f"AI ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല: {e}")

# നിന്റെ ഗൂഗിൾ ലിങ്കുകൾ
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?gid=1126266048&single=true&output=csv&x={random.randint(1,10000)}"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI Hub", layout="wide")

# പ്രീമിയം ഗോൾഡൻ ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 4px solid #FFD700; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# സൈഡ്‌ബാർ
st.sidebar.title("⚪ PAICHI AI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses", "📸 AI Bill Scanner", "📊 Report", "⏰ Reminders"])

if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("നിന്റെ പേഴ്സണൽ AI അസിസ്റ്റന്റ് ഇപ്പോൾ റെഡിയാണ്. ബില്ലുകൾ സ്കാൻ ചെയ്യാൻ 'AI Bill Scanner' തിരഞ്ഞെടുക്കുക.")

elif menu == "📸 AI Bill Scanner":
    st.title("📸 AI Smart Scan")
    st.write("ബില്ലിന്റെ ഫോട്ടോ എടുക്കുകയോ അപ്‌ലോഡ് ചെയ്യുകയോ ചെയ്യുക. AI തുക തനിയെ കണ്ടെത്തും.")
    
    img_file = st.file_uploader("Upload or Take Photo", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="നിങ്ങൾ നൽകിയ ബില്ല്", width=300)
        
        if st.button("🔍 SCAN WITH AI"):
            with st.spinner("AI ബില്ല് വായിക്കുന്നു..."):
                result = reader.readtext(np.array(img))
                all_text = [res[1] for res in result]
                
                # നമ്പറുകൾ മാത്രം കണ്ടുപിടിക്കുന്നു
                prices = []
                for text in all_text:
                    clean = text.replace(',', '').replace(' ', '')
                    try:
                        prices.append(float(clean))
                    except:
                        continue
                
                if prices:
                    detected_amt = max(prices) # സാധാരണ ഏറ്റവും വലിയ നമ്പറാണ് ടോട്ടൽ
                    st.success(f"AI കണ്ടെത്തിയ തുക: ₹ {detected_amt}")
                    
                    # ഫോമിലേക്ക് അയക്കാൻ
                    with st.form("ai_save"):
                        final_item = st.text_input("Item Name", value="AI Scanned Bill")
                        final_price = st.number_input("Amount", value=float(detected_amt))
                        if st.form_submit_button("SAVE TO SHEET"):
                            payload = {
                                "entry.1069832729": datetime.now().strftime("%Y-%m-%d"),
                                "entry.1896057694": final_item,
                                "entry.1570426033": str(final_price)
                            }
                            requests.post(FORM_URL, data=payload)
                            st.balloons()
                            st.success("വിജയകരമായി സേവ് ചെയ്തു!")
                else:
                    st.error("ക്ഷമിക്കണം, തുക കണ്ടെത്താൻ കഴിഞ്ഞില്ല. നേരിട്ട് ടൈപ്പ് ചെയ്യുക.")

elif menu == "💰 Expenses":
    st.title("💰 Expense History")
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            # തുകയുള്ള വരികൾ മാത്രം (0 ഒഴിവാക്കാൻ)
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            df = df[df['Amount'] > 0]
            
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            st.table(df.iloc[:, [2, -1]].tail(10).iloc[::-1])
    except:
        st.info("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. Refresh ചെയ്യുക.")

st.sidebar.write("---")
st.sidebar.write("AI Powered by Faisal")
