import streamlit as st
import pandas as pd

# 1. ആപ്പിന്റെ അടിസ്ഥാന സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #D4AF37 !important; }
    .stApp { background: linear-gradient(135deg, #C0C0C0 30%, #D4AF37 90%) !important; }
    h1, h2, h3, p, span, label, .stMetric { color: #1a1a1a !important; }
    .stButton>button {
        background-color: #D4AF37 !important;
        color: black !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. പാസ്‌വേഡുകൾ
PASSWORDS = {
    "HOME_EXPENSES": "wife123",
    "SSLC": "sslc123",
    "PLUS_TWO": "plus123"
}

# 3. സൈഡ്ബാർ മെനു
st.sidebar.title("PAICHI MENU")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Home Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Study Resources"])

# --- സെക്ഷനുകൾ താഴെ ---

if option == "Home":
    st.markdown("<h1 style='text-align: center;'>🏠 PAICHI Family Hub</h1>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("സ്വാഗതം ഫൈസൽ!")
    st.write("നിന്റെ കുടുംബത്തിന് വേണ്ടിയുള്ള ഡിജിറ്റൽ ഹബ്ബ്.")

elif option == "Home Expenses":
    st.header("💰 Home Expenses Tracker")
    pwd = st.text_input("Enter Password", type="password", key="exp_pwd")
    if pwd == PASSWORDS["HOME_EXPENSES"]:
        st.success("Access Granted!")
        st.info("ഇവിടെ ഹോം എക്സ്പെൻസസ് ഡീറ്റെയിൽസ് കാണാം.")
        # ഗൂഗിൾ ഷീറ്റ് ലിങ്ക് ഇവിടെ വരും
    elif pwd != "":
        st.error("Incorrect Password!")

elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd_s = st.text_input("Enter SSLC Password", type="password", key="sslc_key")
    
    # പാസ്‌വേഡ് ശരിയാണെങ്കിൽ ലിങ്കുകൾ നേരിട്ട് വരും
    if pwd_s == PASSWORDS["SSLC"]:
        st.success("Welcome to SSLC Portal!")
        st.balloons()
        
        st.markdown("### 📚 Study Materials")
        st.write("1. [SSLC Model Questions](https://www.scert.kerala.gov.in)")
        st.write("2. [Previous Year Papers](https://www.keralapareekshabhavan.in)")
        st.write("3. [Online Classes (Victers)](https://www.youtube.com/@ItsVicters)")
        
    elif pwd_s != "":
        st.error("Incorrect Password!")

elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd_p = st.text_input("Enter Plus Two Password", type="password", key="p2_key")
    
    if pwd_p == PASSWORDS["PLUS_TWO"]:
        st.success("Welcome to Plus Two Portal!")
        st.snow()
        
        st.markdown("### 📖 Higher Secondary Resources")
        st.write("1. [Plus Two Textbooks](https://samagra.kite.kerala.gov.in)")
        st.write("2. [Focus Area Notes](https://www.hsslive.in)")
        st.write("3. [Question Bank](https://www.dhsekerala.gov.in)")
        
    elif pwd_p != "":
        st.error("Incorrect Password!")

elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg")

elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Textbooks", "https://samagra.kite.kerala.gov.in/#/textbook/view")

st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
