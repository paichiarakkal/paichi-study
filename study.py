import streamlit as st
import pandas as pd
import os
import requests
from mtranslate import translate

# 1. നിന്റെ ഗൂഗിൾ ഷീറ്റ് ലിങ്ക് (CSV ഫോർമാറ്റിൽ)
# ഷീറ്റിൽ 'Anyone with the link' എന്ന് സെറ്റ് ചെയ്തതുകൊണ്ട് ഇത് വർക്ക് ആകും.
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nu09TIn8p6s0NJblSaH-Ji2KWDowQTLfYasPWZhO1yg/export?format=csv" 
MARK_FILE = 'marks_data.csv'

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഗോൾഡൻ തീം സ്റ്റൈൽ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #000 !important; }
    .news-ticker { background-color: #000; color: #FFD700; padding: 12px; border-radius: 10px; border: 2px solid #FFD700; font-size: 18px; font-weight: bold; }
    .total-box { background-color: #000; color: #FFD700; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; border: 2px solid #FFD700; }
    .stTable { background-color: white !important; border-radius: 10px; color: black !important; }
    h1, h2 { color: black !important; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# വാർത്തകൾ
def get_news():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Kerala,Dubai&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        titles = "  |  ".join([item['title'] for item in res['news']])
        return translate(titles, "ml", "en")
    except: return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു..."

st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 {get_news()}</marquee></div>', unsafe_allow_html=True)

# മെനു
menu = st.sidebar.radio("Go To:", ["🏠 Home", "💰 Home Expenses", "📚 SSLC & Plus Two"])

if menu == "🏠 Home":
    st.title("🏠 Paichi Family Hub")
    st.success("സ്വാഗതം ഫൈസൽ!")
    st.info("ഗൂഗിൾ ഫോം വഴി നൽകുന്ന വിവരങ്ങൾ 'Home Expenses' എന്നതിൽ കാണാം.")
    st.markdown(f"[ലിങ്ക്: ഇവിടെ ക്ലിക്ക് ചെയ്ത് പുതിയ ചെലവുകൾ ചേർക്കാം](https://forms.gle/smPfVnZepcELmAgH6)")

elif menu == "💰 Home Expenses":
    st.header("💵 Expense Tracker (Live)")
    try:
        df = pd.read_csv(SHEET_URL)
        st.table(df) 
        
        # ടോട്ടൽ കണക്കാക്കുന്നു 
        # നീ ഷീറ്റിൽ 'Items', 'Amount' എന്നാണ് പേര് നൽകിയിരിക്കുന്നത് (45223.jpg)
        if 'Amount' in df.columns:
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    except:
        st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ഷീറ്റ് ലിങ്ക് ചെക്ക് ചെയ്യൂ.")

elif menu == "📚 SSLC & Plus Two":
    st.header("📊 Mark List (App Storage)")
    with st.expander("പുതിയ മാർക്ക് ചേർക്കുക"):
        with st.form("mark_form", clear_on_submit=True):
            name = st.text_input("പേര്")
            cat = st.selectbox("ക്ലാസ്സ്", ["SSLC", "Plus Two"])
            mark = st.number_input("മാർക്ക്", min_value=0)
            if st.form_submit_button("Save"):
                new_data = pd.DataFrame([[name, cat, mark]], columns=['Name', 'Class', 'Mark'])
                if not os.path.isfile(MARK_FILE): new_data.to_csv(MARK_FILE, index=False)
                else: new_data.to_csv(MARK_FILE, mode='a', header=False, index=False)
                st.success("സേവ് ചെയ്തു!")
    if os.path.isfile(MARK_FILE):
        st.table(pd.read_csv(MARK_FILE))

st.sidebar.write("---")
st.sidebar.write("Designed by Faisal")
