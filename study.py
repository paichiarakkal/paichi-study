import streamlit as st
import pandas as pd
import requests
import os
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family & Study Hub", layout="wide")

# നിന്റെ ഗൂഗിൾ ഷീറ്റ് ലിങ്ക് (Expenses കാണിക്കാൻ)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nu09TIn8p6s0NJblSaH-Ji2KWDowQTLfYasPWZhO1yg/export?format=csv" 

# ഫയൽ സെറ്റിംഗ്സ് (മാർക്ക് ലിസ്റ്റ് സേവ് ചെയ്യാൻ)
MARK_FILE = 'marks_data.csv'

# ഗോൾഡൻ തീം & സ്റ്റൈൽ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #000 !important; }
    .news-ticker { background-color: #000; color: #FFD700; padding: 12px; border-radius: 10px; border: 2px solid #FFD700; font-size: 18px; margin-bottom: 20px; font-weight: bold; }
    .stTable { background-color: white !important; border-radius: 10px; color: black !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; border: 2px solid #FFD700; margin-top: 10px; }
    h1, h2, h3 { color: black !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def get_news():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Kerala,Dubai&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        titles = "  |  ".join([item['title'] for item in res['news']])
        return translate(titles, "ml", "en")
    except: return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു..."

# 1. വാർത്തകൾ
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 {get_news()}</marquee></div>', unsafe_allow_html=True)

# 2. സൈഡ്ബാർ
menu = st.sidebar.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["Home", "💰 Home Expenses", "📚 SSLC Result", "🎓 Plus Two Result", "🤖 AI Advisor"])

if menu == "Home":
    st.title("🏠 Paichi Family & Study Hub")
    st.subheader(f"സ്വാഗതം ഫൈസൽ!")
    st.write("---")
    st.info("നിന്റെ വീട്ടിലെ ചെലവുകളും കുട്ടികളുടെ പഠന വിവരങ്ങളും ഈ ഒരു ആപ്പിൽ ഇനി ലഭ്യമാണ്.")

elif menu == "💰 Home Expenses":
    st.header("💵 Home Expenses Tracker")
    try:
        df = pd.read_csv(SHEET_URL)
        st.table(df)
        if 'Amount' in df.columns:
            total_sum = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total_sum:,.2f}</div>', unsafe_allow_html=True)
    except:
        st.error("ഗൂഗിൾ ഷീറ്റ് ലിങ്ക് പരിശോധിക്കുക.")

elif menu in ["📚 SSLC Result", "🎓 Plus Two Result"]:
    category = "SSLC" if "SSLC" in menu else "Plus Two"
    st.header(f"📊 {category} Mark List")
    
    # പുതിയ മാർക്ക് ചേർക്കാൻ
    with st.expander(f"{category} മാർക്ക് ആഡ് ചെയ്യുക"):
        with st.form(f"mark_form_{category}", clear_on_submit=True):
            name = st.text_input("വിദ്യാർത്ഥിയുടെ പേര്")
            mark = st.number_input("നേടിയ മാർക്ക്", min_value=0)
            submit = st.form_submit_button("Save Mark")
            if submit and name:
                new_m = pd.DataFrame([[name, category, mark]], columns=['Name', 'Class', 'Mark'])
                if not os.path.isfile(MARK_FILE): new_m.to_csv(MARK_FILE, index=False)
                else: new_m.to_csv(MARK_FILE, mode='a', header=False, index=False)
                st.success(f"{name}-ന്റെ മാർക്ക് സേവ് ചെയ്തു!")

    # ലിസ്റ്റ് കാണിക്കാൻ
    if os.path.isfile(MARK_FILE):
        all_marks = pd.read_csv(MARK_FILE)
        filtered = all_marks[all_marks['Class'] == category]
        st.table(filtered)
    else:
        st.info("മാർക്കുകൾ ഒന്നും ലഭ്യമല്ല.")

elif menu == "🤖 AI Advisor":
    st.header("🤖 AI Advisor")
    st.write("പഠനത്തെക്കുറിച്ചോ ചെലവുകളെക്കുറിച്ചോ ചോദിക്കൂ.")
    user_query = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യൂ...")
    if user_query:
        st.markdown(f"**AI Advisor:** ഫൈസൽ, നിനക്ക് വേണ്ട മറുപടി ഞാൻ ഉടനെ നൽകാം!")

st.sidebar.write("---")
st.sidebar.write("Designed by Faisal")
