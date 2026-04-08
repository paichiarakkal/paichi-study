import streamlit as st
import pandas as pd

# 1. ആപ്പിന്റെ അടിസ്ഥാന സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# 2. പാസ്‌വേഡുകൾ
SSLC_PASSWORD = "sslc123"
PLUS2_PASSWORD = "plus123"
EXPENSE_PASSWORD = "wife123"

# 3. ലിങ്കുകൾ
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"
SHEET_ID = "1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM"
SHEET_URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SHEET_VIEW_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0"

# 4. സൈഡ്ബാർ മെനു
st.sidebar.title("📌 Main Menu")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Wife's Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Study Resources"])

# --- സെക്ഷനുകൾ താഴെ ---

# 1. ഹോം പേജ് (പുതുക്കിയത്)
if option == "Home":
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🏠 PAICHI Family Hub</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("സ്വാഗതം ഫൈസൽ!")
        st.write("""
        ഈ ആപ്പ് നിന്റെ കുടുംബത്തിന്റെ ആവശ്യങ്ങൾക്കായി പ്രത്യേകം തയ്യാറാക്കിയതാണ്. 
        ഇവിടെ നിനക്ക് താഴെ പറയുന്ന കാര്യങ്ങൾ ചെയ്യാം:
        
        * 💰 **ചിലവുകൾ രേഖപ്പെടുത്താം:** ദിവസേനയുള്ള ചിലവുകൾ കൃത്യമായി ട്രാക്ക് ചെയ്യാം.
        * 📚 **പഠന സഹായി:** കുട്ടികൾക്ക് പഠനത്തിനാവശ്യമായ നോട്ടുകളും ലിങ്കുകളും ഇവിടെ ലഭിക്കും.
        * 📸 **ഓർമ്മകൾ:** കുടുംബത്തിലെ നല്ല നിമിഷങ്ങൾ ഫോട്ടോ ഗാലറിയിൽ സൂക്ഷിക്കാം.
        """)
        
        st.info("💡 **ഇന്നത്തെ ചിന്ത:** ലക്ഷ്യത്തിലേക്കുള്ള ചെറിയ ചുവടുവെപ്പുകളാണ് വലിയ വിജയങ്ങളിലേക്ക് നയിക്കുന്നത്. നന്നായി പഠിക്കുക, കൃത്യമായി പ്ലാൻ ചെയ്യുക!")

    with col2:
        st.image("https://img.freepik.com/free-vector/home-concept-illustration_114360-1007.jpg", use_column_width=True)

# 2. വൈഫിന്റെ എക്സ്പെൻസ് സെക്ഷൻ
elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    pwd = st.text_input("Enter Password", type="password", key="exp_pwd")
    
    if pwd == EXPENSE_PASSWORD:
        st.success("Access Granted!")
        try:
            df = pd.read_csv(SHEET_URL_CSV)
            total_expense = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.metric(label="ഈ മാസത്തെ ആകെ ചിലവ്", value=f"₹{total_expense}")
        except:
            st.info("കണക്കുകൾ ശേഖരിക്കുന്നു...")

        st.divider()
        st.link_button("📝 പുതിയ ചിലവ് ചേർക്കുക (Open Form)", GOOGLE_FORM_URL)
        st.link_button("👁️ View Full Google Sheet", SHEET_VIEW_URL)
    elif pwd != "":
        st.error("Incorrect Password!")

# 3. SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd_s = st.text_input("SSLC Password", type="password", key="sslc_pwd")
    if pwd_s == SSLC_PASSWORD:
        st.success("Welcome to SSLC Portal")
        st.write("പഠന വിവരങ്ങളും നോട്ടുകളും ഇവിടെ ലഭ്യമാണ്.")
        st.balloons()
    elif pwd_s != "":
        st.error("Incorrect Password!")

# 4. പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd_p = st.text_input("Plus Two Password", type="password", key="p2_pwd")
    if pwd_p == PLUS2_PASSWORD:
        st.success("Welcome to Plus Two Portal")
        st.write("സ്റ്റഡി മെറ്റീരിയലുകൾ ഇവിടെ നോക്കാം.")
        st.snow()
    elif pwd_p != "":
        st.error("Incorrect Password!")

# 5. ഫോട്ടോ ഗാലറി
elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg")

# 6. സ്റ്റഡി റിസോഴ്‌സസ്
elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Textbooks", "https://samagra.kite.kerala.gov.in/#/textbook/view")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
