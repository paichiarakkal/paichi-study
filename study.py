import streamlit as st
import pandas as pd

# 1. Nee thanna puthiya CSV link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFVz3KIhk0Q8oYKnnU1Q5lx7VibrckNRVnA7AOm_n2aerxhXhRSgh4yKGAak9vtU04mTEyp7epp_hA/pub?gid=0&single=true&output=csv"
FORM_URL = "https://forms.gle/smPfVnZepcELmAgH6"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# Custom Design (Silver Sidebar & Gold Main)
st.markdown("""
    <style>
    /* Main Page Gold */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    
    /* Sidebar Silver */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    
    /* Vartha Odunna Vari (News Ticker) */
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 30s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; }
    .st-emotion-cache-10trblm { color: black !important; font-weight: bold !important; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Varthakal (News Ticker)
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 PAICHI Family Hub-ilekku Swagatham! | Current Bill, Vadaka ennivaya krithya samayathu adaykkan sradhikkuka. | Ninte ellam chelhavukalum ivide live aayi kaanam. 📢</div></div>', unsafe_allow_html=True)

# 3. Sidebar Menu
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("Thiranjedukkuka:", 
    ["🏠 Home", "💰 Home Expenses", "🎓 SSLC Marks", "🎓 Plus Two Marks", "📊 Monthly Report", "📈 Charts & Graphs", "🔍 Search & Filter", "⏰ Reminders"])

# --- Features ---

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.success(f"Swagatham Faisal!")
    st.link_button("➕ Puthiya chelhavukal cherkkan (Google Form)", FORM_URL)
    st.info("Sidebar-il ninnu ninakku avashyamulla karyangal thiranjedukkam.")

elif menu == "💰 Home Expenses":
    st.title("💵 Home Expenses")
    st.link_button("➕ Add New Entry", FORM_URL)
    
    if st.button('🔄 Refresh Data'):
        st.cache_data.clear()
        st.rerun()

    try:
        # Sheet-il ninnu data vayikkunnu
        df = pd.read_csv(CSV_URL)
        st.dataframe(df, use_container_width=True)
        
        # Total Amount kanikkunnu
        if not df.empty:
            # 'Amount' enna column thirayunnu
            amount_col = [col for col in df.columns if 'amount' in col.lower()]
            if amount_col:
                total = pd.to_numeric(df[amount_col[0]], errors='coerce').sum()
                st.markdown(f'<div class="total-box">Aake Chelhavu: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    except:
        st.error("Sheet-il data onnum kaanunnilla. Form submit cheytho ennu parishodhikkuka.")

elif menu == "🎓 SSLC Marks" or menu == "🎓 Plus Two Marks":
    st.title(f"{menu}")
    st.write("Mark-ukal ivide rekhappeduthlam (Work in Progress).")

elif menu == "📊 Monthly Report":
    st.title("📊 Monthly Report")
    st.write("Ee masathe chelhavukalude poornaroopam ivide varum.")

elif menu == "📈 Charts & Graphs":
    st.title("📈 Expense Charts")
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty:
            st.bar_chart(df.iloc[:, -1]) 
    except:
        st.write("Data labhyamalla.")

elif menu == "🔍 Search & Filter":
    st.title("🔍 Search")
    query = st.text_input("Thirayendath enthanu?")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ Current Bill adaykkan samayamayi!")
    st.warning("🏠 Veettu vadaka nalkaan marakkuruthu!")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
