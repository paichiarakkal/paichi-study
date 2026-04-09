import streamlit as st
import pandas as pd
import requests
import os
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Study Hub", layout="wide")

# --- CUSTOM CSS (Color & Style) ---
st.markdown("""
    <style>
    /* ബാക്ക്ഗ്രൗണ്ട് നിറം */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); 
        color: #000; 
    }
    /* സൈഡ്ബാർ സ്റ്റൈൽ */
    [data-testid="stSidebar"] { 
        background-color: #000 !important; 
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #FFD700 !important;
    }
    /* വാർത്താ ബോക്സ് */
    .news-ticker {
        background-color: #000;
        color: #FFD700;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #FFD700;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 25px;
    }
    /* ടേബിൾ സ്റ്റൈൽ */
    .stDataFrame, .stTable {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- വാർത്തകൾ എടുക്കാനുള്ള ഫംഗ്ഷൻ ---
def get_malayalam_news():
    try:
        # ഗൾഫ് വാർത്തകളും കേരള വാർത്തകളും കലർന്ന ഒരു സെർച്ച്
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Kerala,Dubai,Gold,Market&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        titles = [item['title'] for item in res['news']]
        combined = "  |  ".join(titles)
        return translate(combined, "ml", "en")
    except:
        return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു... ദയവായി കാത്തിരിക്കൂ..."

# ഫയൽ സെറ്റിംഗ്സ്
EXP_FILE = 'study_expenses.csv'
MARK_FILE = 'study_marks.csv'

# --- 1. LIVE NEWS TICKER (TOP) ---
live_news = get_malayalam_news()
st.markdown(f"""
    <div class="news-ticker">
        <marquee scrollamount="6">
            📢 {live_news}
        </marquee>
    </div>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR ---
st.sidebar.title("🏠 STUDY MENU")
menu = st.sidebar.radio("വിഭാഗം തിരഞ്ഞെടുക്കുക:", ["Home", "💰 Home Expenses", "📚 Student Corner"])

# --- 3. MAIN CONTENT ---

if menu == "Home":
    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px #000;'>🏠 Paichi Study App</h1>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("സ്വാഗതം!")
    st.info("ഈ ആപ്പിൽ നിനക്ക് വീട്ടിലെ ചെലവുകളും കുട്ടികളുടെ പഠന വിവരങ്ങളും കൃത്യമായി രേഖപ്പെടുത്താം.")

elif menu == "💰 Home Expenses":
    st.markdown("<h1 style='color: white; text-shadow: 2px 2px #000;'>💰 Home Expenses</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("പുതിയത് ചേർക്കുക")
        with st.form("exp_form"):
            date = st.date_input("തിയതി")
            item = st.text_input("വിവരണം")
            amt = st.number_input("തുക", min_value=0)
            submitted = st.form_submit_button("സേവ് ചെയ്യുക")
            
            if submitted:
                new_row = pd.DataFrame([[date, item, amt]], columns=['Date', 'Item', 'Amount'])
                if not os.path.isfile(EXP_FILE): new_row.to_csv(EXP_FILE, index=False)
                else: new_row.to_csv(EXP_FILE, mode='a', header=False, index=False)
                st.success("ലിസ്റ്റ് അപ്‌ഡേറ്റ് ചെയ്തു!")

    with col2:
        st.subheader("ലിസ്റ്റ് (Expense Table)")
        if os.path.isfile(EXP_FILE):
            df = pd.read_csv(EXP_FILE)
            st.table(df) # ലിസ്റ്റ് പട്ടികയായി കാണിക്കുന്നു
            st.markdown(f"### **ആകെ ചെലവ്: ₹{df['Amount'].sum()}**")
        else:
            st.warning("ലിസ്റ്റ് കാലിയാണ്.")

elif menu == "📚 Student Corner":
    st.markdown("<h1 style='color: white; text-shadow: 2px 2px #000;'>📚 Student Corner</h1>", unsafe_allow_html=True)
    
    cat = st.selectbox("ക്ലാസ്സ്:", ["SSLC", "Plus One", "Plus Two"])
    
    with st.expander("മാർക്ക് എന്റർ ചെയ്യുക"):
        name = st.text_input("പേര്")
        m1 = st.number_input("മലയാളം", 0, 100)
        m2 = st.number_input("ഇംഗ്ലീഷ്", 0, 100)
        m3 = st.number_input("മാക്സ്/അക്കൗണ്ടൻസി", 0, 100)
        if st.button("Submit Result"):
            total = m1+m2+m3
            new_m = pd.DataFrame([[name, cat, m1, m2, m3, total]], columns=['Name', 'Class', 'M1', 'M2', 'M3', 'Total'])
            if not os.path.isfile(MARK_FILE): new_m.to_csv(MARK_FILE, index=False)
            else: new_m.to_csv(MARK_FILE, mode='a', header=False, index=False)
            st.success("മാർക്ക് ലിസ്റ്റ് സേവ് ചെയ്തു!")

    st.subheader(f"📊 {cat} Mark List")
    if os.path.isfile(MARK_FILE):
        df_m = pd.read_csv(MARK_FILE)
        filtered = df_m[df_m['Class'] == cat]
        st.table(filtered)
    else:
        st.info("മാർക്കുകൾ ഒന്നും ലഭ്യമല്ല.")

st.sidebar.write("---")
st.sidebar.write("Designed by Faisal")
