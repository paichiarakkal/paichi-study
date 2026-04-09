import streamlit as st
import pandas as pd

# നിന്റെ കറക്റ്റ് ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv"
FORM_URL = "https://forms.gle/R3wVocUKRJ3BLnyP7"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 3px solid #FFD700; margin-top: 20px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | ആപ്പിൽ നിന്ന് തന്നെ വിവരങ്ങൾ ചേർക്കാം | ടോട്ടൽ തുക താഴെ കാണാം 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📊 Monthly Report", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.write("സ്വാഗതം ഫൈസൽ! താഴെയുള്ള മെനുവിൽ നിന്ന് Expenses തിരഞ്ഞെടുക്കുക.")

elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Add New Expense")
        st.write("താഴെ കാണുന്ന ഫോമിൽ വിവരങ്ങൾ നൽകി സബ്മിറ്റ് ചെയ്യുക:")
        # ഗൂഗിൾ ഫോം ആപ്പിനുള്ളിൽ തന്നെ കാണിക്കുന്നു
        st.components.v1.iframe(FORM_URL, height=500)
    
    with col2:
        st.subheader("📋 Expense History")
        if st.button('🔄 Refresh Data'):
            st.cache_data.clear()
            st.rerun()
            
        try:
            df = pd.read_csv(CSV_URL)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # തുക കൃത്യമായി കണക്കാക്കാൻ (Amount കോളം അല്ലെങ്കിൽ അവസാന കോളം)
                total = pd.to_numeric(df.iloc[:, -1], errors='coerce').sum()
                st.markdown(f'<div class="total-box">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            else:
                st.info("ഡാറ്റയൊന്നുമില്ല. ഇടതുവശത്തെ ഫോമിൽ വിവരങ്ങൾ ചേർക്കുക.")
        except:
            st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

else:
    st.title(menu)
    st.write("ഈ സെക്ഷൻ റെഡിയായി വരുന്നു...")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
