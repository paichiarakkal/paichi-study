import streamlit as st
import pandas as pd

# 1. ആപ്പിന്റെ അടിസ്ഥാന സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# --- CUSTOM CSS FOR THEME (Gold & Silver Mix) ---
st.markdown("""
    <style>
    /* സൈഡ്‌ബാർ ഗോൾഡ് (Gold) കളർ */
    [data-testid="stSidebar"] {
        background-color: #D4AF37 !important;
    }
    [data-testid="stSidebar"] * {
        color: black !important;
        font-weight: bold;
    }
    
    /* മെയിൻ ബോഡി സിൽവർ + ഗോൾഡ് മിക്സ് (Silver & Gold Mix) */
    .stApp {
        background: linear-gradient(135deg, #C0C0C0 30%, #D4AF37 90%);
    }
    
    /* ടൈറ്റിൽ ആൻഡ് ടെക്സ്റ്റ് കളർ */
    h1, h2, h3, p, span {
        color: #1a1a1a !important;
    }

    /* ബട്ടണുകളുടെ ഡിസൈൻ */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: black !important;
        border-radius: 12px;
        border: 2px solid #C0C0C0;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. പാസ്‌വേഡുകൾ
SSLC_PASSWORD = "sslc123"
PLUS2_PASSWORD = "plus123"
EXPENSE_PASSWORD = "wife123"

# 3. ലിങ്കുകൾ
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"
SHEET_ID = "1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM"
SHEET_URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SHEET_VIEW_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0"

# 4. സൈഡ്ബാർ മെനു (Home Expenses എന്ന് മാറ്റിയിട്ടുണ്ട്)
st.sidebar.title("🔱 PAICHI MENU")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Home Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Study Resources"])

# --- സെക്ഷനുകൾ താഴെ ---

# 1. ഹോം പേജ്
if option == "Home":
    st.markdown("<h1 style='text-align: center;'>🏠 PAICHI Family Hub</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("സ്വാഗതം ഫൈസൽ!")
        st.write("നിന്റെ കുടുംബത്തിന്റെ എല്ലാ ആവശ്യങ്ങൾക്കുമായി ഈ ഡിജിറ്റൽ ഹബ്ബ് ഉപയോഗിക്കാം.")
        st.info("💡 **ഇന്നത്തെ ചിന്ത:** കൃത്യമായ പ്ലാനിംഗ് വിജയത്തിലേക്കുള്ള ആദ്യ ചുവടുവെപ്പാണ്.")
    with col2:
        st.image("https://img.freepik.com/free-vector/home-concept-illustration_114360-1007.jpg")

# 2. ഹോം എക്സ്പെൻസസ് (Home Expenses Tracker)
elif option == "Home Expenses":
    st.header("💰 Home Expenses Tracker")
    pwd = st.text_input("Enter Password", type="password", key="exp_pwd")
    
    if pwd == EXPENSE_PASSWORD:
        st.success("Access Granted!")
        
        # ടോട്ടൽ തുക തനിയെ കൂട്ടി കാണിക്കുന്നു
        try:
            df = pd.read_csv(SHEET_URL_CSV)
            total_expense = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.metric(label="ഈ മാസത്തെ ആകെ ചിലവ്", value=f"₹{total_expense}")
        except:
            st.info("കണക്കുകൾ ശേഖരിക്കുന്നു. പുതിയ മറുപടികൾ നൽകിയ ശേഷം ഇവിടെ കാണാം.")

        st.divider()
        st.write("പുതിയ വിവരങ്ങൾ ചേർക്കാൻ താഴെ കാണുന്ന ബട്ടൺ ഉപയോഗിക്കുക:")
        st.link_button("📝 പുതിയ ചിലവ് ചേർക്കുക (Open Form)", GOOGLE_FORM_URL)
        
        st.subheader("📊 പഴയ റെക്കോർഡുകൾ")
        st.link_button("👁️ View Full Google Sheet", SHEET_VIEW_URL)
    elif pwd != "":
        st.error("Incorrect Password!")

# 3. SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd_s = st.text_input("SSLC Password", type="password", key="sslc_pwd")
    if pwd_s == SSLC_PASSWORD:
        st.success("Welcome to SSLC Portal")
        st.balloons()
    elif pwd_s != "":
        st.error("Incorrect Password!")

# 4. പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd_p = st.text_input("Plus Two Password", type="password", key="p2_pwd")
    if pwd_p == PLUS2_PASSWORD:
        st.success("Welcome to Plus Two Portal")
        st.snow()
    elif pwd_p != "":
        st.error("Incorrect Password!")

# 5. ഫോട്ടോ ഗാലറി (ഇപ്പോൾ ഫോട്ടോകൾ വരും)
elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.write("മനോഹരമായ നിമിഷങ്ങൾ ഇവിടെ കാണാം.")
    
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg", use_column_width=True)
        st.image("https://img.freepik.com/free-photo/happy-family-outdoors-park_23-2148873752.jpg", use_column_width=True)
    with col_img2:
        st.image("https://img.freepik.com/free-photo/kids-studying-together-home_23-2148873760.jpg", use_column_width=True)
        st.image("https://img.freepik.com/free-photo/family-smiling-camera-outdoors_23-2148873740.jpg", use_column_width=True)

# 6. സ്റ്റഡി റിസോഴ്‌സസ്
elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Textbooks", "https://samagra.kite.kerala.gov.in/#/textbook/view")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
