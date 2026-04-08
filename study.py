import streamlit as st

# ആപ്പിന്റെ സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ടൈറ്റിൽ
st.title("🎓 PAICHI Family Education & Expense Portal")

# പാസ്‌വേഡുകൾ
SSLC_PASSWORD = "sslc123"
PLUS2_PASSWORD = "plus123"
EXPENSE_PASSWORD = "wife123"

# നിന്റെ ഗൂഗിൾ ഫോം ലിങ്ക്
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"

# നിന്റെ ഗൂഗിൾ ഷീറ്റ് ലിങ്ക് (കണക്കുകൾ കാണാൻ)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM/edit#gid=0"

# സൈഡ്ബാർ മെനു
st.sidebar.title("📌 Main Menu")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Wife's Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Study Resources"])

# 1. ഹോം പേജ്
if option == "Home":
    st.header("സ്വാഗതം ഫൈസൽ!")
    st.write("നിന്റെ കുടുംബത്തിന് വേണ്ടി പൈത്തൺ ഉപയോഗിച്ച് നിർമ്മിച്ച പ്രത്യേക ആപ്പ് ആണിത്.")
    st.image("https://img.freepik.com/free-vector/graduation-cap-with-diploma-scroll-realistic-style_1284-18155.jpg", width=300)

# 2. വൈഫിന്റെ എക്സ്പെൻസ് സെക്ഷൻ
elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    pwd = st.text_input("Enter Password", type="password")
    
    if pwd == EXPENSE_PASSWORD:
        st.success("Access Granted!")
        
        st.info("പുതിയ ചിലവുകൾ താഴെ കാണുന്ന ബട്ടൺ അമർത്തി രേഖപ്പെടുത്തുക.")
        
        # ഗൂഗിൾ ഫോം തുറക്കാനുള്ള ബട്ടൺ
        st.link_button("📝 പുതിയ ചിലവ് രേഖപ്പെടുത്തുക (Open Form)", GOOGLE_FORM_URL)
        
        st.divider()
        
        st.subheader("📊 മാസത്തെ കണക്കുകൾ പരിശോധിക്കാൻ")
        st.write("ഇതുവരെ നൽകിയ എല്ലാ വിവരങ്ങളും കാണാൻ താഴെ ക്ലിക്ക് ചെയ്യുക.")
        st.link_button("👁️ View Full Google Sheet", SHEET_URL)

    elif pwd != "":
        st.error("Wrong Password!")

# 3. SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd_s = st.text_input("SSLC Password", type="password")
    if pwd_s == SSLC_PASSWORD:
        st.write("പഠന കാര്യങ്ങളും നോട്ടുകളും ഇവിടെ നൽകാം.")
        st.balloons()

# 4. പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd_p = st.text_input("Plus Two Password", type="password")
    if pwd_p == PLUS2_PASSWORD:
        st.write("സ്റ്റഡി മെറ്റീരിയലുകൾ ഇവിടെ ലഭ്യമാണ്.")
        st.snow()

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
