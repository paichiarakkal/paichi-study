import streamlit as st
import pandas as pd

# നിന്റെ പുതിയ ലിങ്കുകൾ ഇവിടെ സെറ്റ് ചെയ്തിട്ടുണ്ട്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv"
FORM_URL = "https://forms.gle/R3wVocUKRJ3BLnyP7"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ (Silver Sidebar & Gold Main Page)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | കൃത്യസമയത്ത് വിവരങ്ങൾ അപ്ഡേറ്റ് ചെയ്യുക. 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", ["🏠 Home", "💰 Home Expenses", "📊 Monthly Report", "⏰ Reminders"])

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.success("സ്വാഗതം ഫൈസൽ! എല്ലാം വിജയകരമായി ലിങ്ക് ചെയ്തു.")
    st.link_button("➕ പുതിയ ചെലവുകൾ ചേർക്കുക", FORM_URL)

elif menu == "💰 Home Expenses":
    st.title("💵 Expense Tracker")
    
    if st.button('🔄 Refresh Data'):
        st.cache_data.clear()
        st.rerun()

    try:
        # ഷീറ്റിൽ നിന്ന് ഡാറ്റ വായിക്കുന്നു
        df = pd.read_csv(CSV_URL)
        
        if df.empty:
            st.info("ഷീറ്റിൽ നിലവിൽ വിവരങ്ങൾ ഒന്നുമില്ല. ഫോം വഴി ഒന്ന് ആഡ് ചെയ്യൂ.")
        else:
            st.dataframe(df, use_container_width=True)
            # തുകയുടെ കോളം (Amount) കണക്കാക്കുന്നു
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ഷീറ്റ് പബ്ലിഷ് ചെയ്തിട്ടുണ്ടെന്ന് ഉറപ്പുവരുത്തുക.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
