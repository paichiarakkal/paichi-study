import streamlit as st
import pandas as pd

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTupW3xiZrAzp632NVBO3SpfRKcloT_GtUfOYetoWP1ZedonX8xKWZuvluEuOel54ZLewlxXfqahVsl/pub?gid=0&single=true&output=csv"
FORM_URL = "https://forms.gle/smPfVnZepcELmAgH6"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# കസ്റ്റം ഡിസൈൻ (Silver Sidebar & Gold Main)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 30s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    .st-emotion-cache-10trblm { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# വാർത്തകൾ ഓടുന്ന വരി
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബിലേക്ക് സ്വാഗതം! | കറന്റ് ബില്ല്, വാടക എന്നിവ കൃത്യസമയത്ത് അടയ്ക്കാൻ ശ്രദ്ധിക്കുക. 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Home Expenses", "🎓 SSLC Marks", "🎓 Plus Two Marks", "📊 Monthly Report", "📈 Charts & Graphs", "🔍 Search & Filter", "⏰ Reminders"])

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.success("സ്വാഗതം ഫൈസൽ!")
    st.link_button("➕ പുതിയ ചെലവുകൾ ചേർക്കുക (Google Form)", FORM_URL)

elif menu == "💰 Home Expenses":
    st.title("💵 Expense Tracker")
    if st.button('🔄 Refresh Data'):
        st.cache_data.clear()
        st.rerun()

    try:
        df = pd.read_csv(CSV_URL)
        st.dataframe(df, use_container_width=True)
        
        if not df.empty:
            # നിന്റെ ഷീറ്റിലെ Amount കോളം (ഫോട്ടോ 45241 പ്രകാരം 4-ാമത്തെ കോളം)
            # അത് വരാൻ കോളം പേര് നോക്കാതെ നേരിട്ട് തുക കൂട്ടാനുള്ള വഴി:
            amount_values = pd.to_numeric(df.iloc[:, 3], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {amount_values:,.2f}</div>', unsafe_allow_html=True)
    except:
        st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ഷെയർ സെറ്റിംഗ്സ് മാറ്റിയ ശേഷം റിഫ്രഷ് ചെയ്യുക.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായി!")
    st.warning("🏠 വീട്ടുവാടക നൽകാൻ മറക്കരുത്!")

else:
    st.title(menu)
    st.write("ഈ ഭാഗം പിന്നീട് അപ്‌ഡേറ്റ് ചെയ്യാം.")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
