import streamlit as st
import pandas as pd
import datetime

# 1. ലിങ്കുകൾ (ഇവിടെ നിന്റെ ലിങ്കുകൾ കറക്റ്റ് ആണെന്ന് ഉറപ്പാക്കുക)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTupW3xiZrAzp632NVBO3SpfRKcloT_GtUfOYetoWP1ZedonX8xKWZuvluEuOel54ZLewlxXfqahVsl/pub?gid=0&single=true&output=csv"
FORM_URL = "https://forms.gle/smPfVnZepcELmAgH6"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# കസ്റ്റം ഡിസൈൻ (Silver Sidebar & Gold Main)
st.markdown("""
    <style>
    /* മെയിൻ പേജ് ഗോൾഡ് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* സൈഡ്‌ബാർ സിൽവർ */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    
    /* വാർത്തകൾ ഓടുന്ന വരി (News Ticker) */
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; margin-bottom: 20px; border-radius: 5px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; }
    .st-emotion-cache-10trblm { color: black !important; font-weight: bold !important; }
    h1, h2, h3 { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. കേരള വാർത്തകൾ ഓടുന്ന വരി
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 കേരളത്തിലെ പ്രാദേശിക വാർത്തകൾ ഇവിടെ തത്സമയം കാണാം... പൈച്ചി ഫാമിലി ഹബ്ബിലേക്ക് സ്വാഗതം! | കറന്റ് ബില്ല്, വാടക എന്നിവ കൃത്യസമയത്ത് അടയ്ക്കാൻ ശ്രദ്ധിക്കുക. 📢</div></div>', unsafe_allow_html=True)

# 3. സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Home Expenses", "🎓 SSLC Marks", "🎓 Plus Two Marks", "📊 Monthly Report", "📈 Charts & Graphs", "🔍 Search & Filter", "⏰ Reminders", "🌙 Dark Mode Toggle"])

# --- ഫീച്ചറുകൾ ---

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.success("സ്വാഗതം ഫൈസൽ!")
    st.link_button("➕ പുതിയ ചെലവുകൾ ചേർക്കുക (Google Form)", FORM_URL)
    st.info("സൈഡ്‌ബാറിൽ നിന്നും നിനക്ക് ആവശ്യമുള്ള മെനു തിരഞ്ഞെടുക്കാം.")

elif menu == "💰 Home Expenses":
    st.title("💵 Home Expenses")
    st.link_button("➕ Add New Entry", FORM_URL)
    try:
        df = pd.read_csv(CSV_URL)
        st.dataframe(df, use_container_width=True)
        if 'Amount' in df.columns:
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    except:
        st.error("ഷീറ്റ് ലിങ്ക് പരിശോധിക്കുക.")

elif menu == "🎓 SSLC Marks" or menu == "🎓 Plus Two Marks":
    st.title(f"{menu}")
    st.write("മാർക്കുകൾ ഇവിടെ രേഖപ്പെടുത്താം.")
    name = st.text_input("വിദ്യാർത്ഥിയുടെ പേര്")
    marks = st.number_input("മാർക്ക്", min_value=0)
    if st.button("Save Marks"):
        st.success(f"{name}-ന്റെ മാർക്ക് സേവ് ചെയ്തു!")

elif menu == "📊 Monthly Report":
    st.title("📊 Monthly Expense Report")
    st.info("ഈ മാസത്തെ ആകെ ചെലവുകളുടെ റിപ്പോർട്ട് ഇവിടെ കാണാം.")

elif menu == "📈 Charts & Graphs":
    st.title("📈 Expense Visualizer")
    try:
        df = pd.read_csv(CSV_URL)
        if 'Items' in df.columns and 'Amount' in df.columns:
            st.bar_chart(df.set_index('Items')['Amount'])
    except:
        st.write("ഡാറ്റ ലഭ്യമല്ല.")

elif menu == "🔍 Search & Filter":
    st.title("🔍 Search Expenses")
    search = st.text_input("ഏത് സാധനമാണ് തിരയേണ്ടത്?")
    try:
        df = pd.read_csv(CSV_URL)
        if search:
            result = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
            st.dataframe(result)
    except:
        st.write("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ മറക്കരുത്!")
    st.warning("🏠 വീട്ടുവാടക നൽകേണ്ട സമയമായി!")

elif menu == "🌙 Dark Mode Toggle":
    st.title("🌙 Theme Settings")
    dark = st.checkbox("Dark Mode ഓൺ ചെയ്യുക")
    if dark:
        st.write("ഡാർക്ക് മോഡ് ആക്ടിവേറ്റ് ചെയ്യുന്നു...")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
