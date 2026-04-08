import streamlit as st
import pandas as pd

# 1. ആപ്പിന്റെ അടിസ്ഥാന സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# --- CUSTOM CSS (Gold & Silver Theme) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #D4AF37 !important; }
    [data-testid="stSidebar"] * { color: black !important; font-weight: bold; }
    .stApp { background: linear-gradient(135deg, #C0C0C0 30%, #D4AF37 90%) !important; }
    h1, h2, h3, p, span, label, .stMetric { color: #1a1a1a !important; }
    .stButton>button {
        background-color: #D4AF37 !important;
        color: black !important;
        border-radius: 12px !important;
        border: 2px solid #C0C0C0 !important;
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

# 3. ലിങ്കുകൾ
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"
SHEET_ID = "1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM"
SHEET_URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 4. സൈഡ്ബാർ മെനു
st.sidebar.title("PAICHI MENU")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Home Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Study Resources"])

# --- സെക്ഷനുകൾ താഴെ ---

if option == "Home":
    st.markdown("<h1 style='text-align: center;'>🏠 PAICHI Family Hub</h1>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("സ്വാഗതം ഫൈസൽ!")
    st.write("കുടുംബത്തിന്റെ ആവശ്യങ്ങൾക്കായി നിർമ്മിച്ച ഡിജിറ്റൽ ഹബ്ബ്.")

elif option == "Home Expenses":
    st.header("💰 Home Expenses Tracker")
    pwd = st.text_input("Enter Password", type="password", key="exp_pwd")
    if pwd == PASSWORDS["HOME_EXPENSES"]:
        st.success("Access Granted!")
        try:
            df = pd.read_csv(SHEET_URL_CSV)
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.metric(label="ഈ മാസത്തെ ആകെ ചിലവ്", value=f"₹{total}")
            st.write("### 📊 Recent Entries")
            st.dataframe(df.tail(10)) # ലിസ്റ്റ് കൂടി കാണാൻ ഇത് സഹായിക്കും
        except:
            st.info("കണക്കുകൾ ശേഖരിക്കുന്നു...")
    elif pwd != "":
        st.error("Incorrect Password!")

elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd_s = st.text_input("Enter SSLC Password", type="password", key="sslc_key")
    if pwd_s == PASSWORDS["SSLC"]:
        st.success("Welcome to SSLC Portal!")
        st.balloons()
        st.markdown("""
        ### 📚 Study Materials
        * [SSLC Model Questions](https://www.scert.kerala.gov.in)
        * [Previous Year Papers](https://www.keralapareekshabhavan.in)
        * [Online Classes (Victers)](https://www.youtube.com/@ItsVicters)
        """)
    elif pwd_s != "":
        st.error("Incorrect Password!")

elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd_p = st.text_input("Enter Plus Two Password", type="password", key="p2_key")
    if pwd_p == PASSWORDS["PLUS_TWO"]:
        st.success("Welcome to Plus Two Portal!")
        st.snow()
        st.markdown("""
        ### 📖 Higher Secondary Resources
        * [Plus Two Textbooks](https://samagra.kite.kerala.gov.in)
        * [Focus Area Notes](https://www.hsslive.in)
        * [Question Bank](https://www.dhsekerala.gov.in)
        """)
    elif pwd_p != "":
        st.error("Incorrect Password!")

elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg", use_column_width=True)
        st.image("https://img.freepik.com/free-photo/happy-family-outdoors-park_23-2148873752.jpg", use_column_width=True)
    with col_img2:
        st.image("https://img.freepik.com/free-photo/kids-studying-together-home_23-2148873760.jpg", use_column_width=True)
        st.image("https://img.freepik.com/free-photo/family-smiling-camera-outdoors_23-2148873740.jpg", use_column_width=True)

elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Textbooks", "https://samagra.kite.kerala.gov.in/#/textbook/view")

st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
