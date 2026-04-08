import streamlit as st
import pandas as pd

# 1. ആപ്പിന്റെ അടിസ്ഥാന സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

st.title("🎓 PAICHI Family Education & Expense Portal")

# 2. പാസ്‌വേഡുകൾ
SSLC_PASSWORD = "sslc123"
PLUS2_PASSWORD = "plus123"
EXPENSE_PASSWORD = "wife123"

# 3. ലിങ്കുകൾ (നിനക്ക് വേണ്ടി ഞാൻ ഇത് സെറ്റ് ചെയ്തിട്ടുണ്ട്)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"
SHEET_URL_CSV = "https://docs.google.com/spreadsheets/d/1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM/export?format=csv"
SHEET_VIEW_URL = "https://docs.google.com/spreadsheets/d/1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM/edit#gid=0"

# 4. സൈഡ്ബാർ മെനു
st.sidebar.title("📌 Main Menu")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Wife's Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Study Resources"])

# --- സെക്ഷനുകൾ താഴെ ---

# ഹോം പേജ്
if option == "Home":
    st.header("സ്വാഗതം ഫൈസൽ!")
    st.write("കുടുംബത്തിന് വേണ്ടിയുള്ള നിന്റെ സ്വന്തം ആപ്പ് ഇപ്പോൾ തയ്യാറാണ്.")
    st.image("https://img.freepik.com/free-vector/graduation-cap-with-diploma-scroll-realistic-style_1284-18155.jpg", width=300)

# വൈഫിന്റെ എക്സ്പെൻസ് സെക്ഷൻ (വിത്ത് ടോട്ടൽ)
elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    pwd = st.text_input("Enter Password", type="password")
    
    if pwd == EXPENSE_PASSWORD:
        st.success("Access Granted!")
        
        # ടോട്ടൽ കണക്കാക്കുന്നു
        try:
            df = pd.read_csv(SHEET_URL_CSV)
            # 'Amount' കോളത്തിലെ ഡാറ്റ നമ്പറുകളാണെന്ന് ഉറപ്പുവരുത്തി കൂട്ടുന്നു
            total_expense = pd.to_numeric(df['Amount'], errors='coerce').sum()
            
            # ടോട്ടൽ തുക വലിയ അക്ഷരത്തിൽ കാണിക്കുന്നു
            st.metric(label="ഈ മാസത്തെ ആകെ ചിലവ്", value=f"₹{total_expense}")
        except:
            st.info("കണക്കുകൾ ശേഖരിക്കുന്നു. പുതിയ ഡാറ്റ നൽകിയ ശേഷം ഇവിടെ കാണാം.")

        st.divider()
        st.write("പുതിയ ചിലവുകൾ താഴെ കാണുന്ന ബട്ടൺ അമർത്തി രേഖപ്പെടുത്തുക.")
        st.link_button("📝 പുതിയ ചിലവ് ചേർക്കുക (Open Form)", GOOGLE_FORM_URL)
        
        st.subheader("📊 മുഴുവൻ ലിസ്റ്റ് കാണാൻ")
        st.link_button("👁️ View Full Google Sheet", SHEET_VIEW_URL)

    elif pwd != "":
        st.error("Wrong Password!")

# SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd_s = st.text_input("SSLC Password", type="password")
    if pwd_s == SSLC_PASSWORD:
        st.write("പഠന വിവരങ്ങൾ ഇവിടെ ലഭ്യമാണ്.")
        st.balloons()

# പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd_p = st.text_input("Plus Two Password", type="password")
    if pwd_p == PLUS2_PASSWORD:
        st.write("നോട്ടുകൾ ഇവിടെ ലഭിക്കും.")
        st.snow()

# ഫോട്ടോ ഗാലറി
elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg")

# സ്റ്റഡി റിസോഴ്‌സസ്
elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Textbooks", "https://samagra.kite.kerala.gov.in/#/textbook/view")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
