import streamlit as st
import pandas as pd

# 1. ആപ്പിന്റെ അടിസ്ഥാന സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

st.title("🎓 PAICHI Family Education & Expense Portal")

# 2. പാസ്‌വേഡുകൾ
EXPENSE_PASSWORD = "wife123"

# 3. ലിങ്കുകൾ (നിന്റെ ഡാറ്റാബേസുമായി കണക്ട് ചെയ്തിട്ടുണ്ട്)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"
SHEET_ID = "1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM"
SHEET_URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SHEET_VIEW_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0"

# 4. സൈഡ്ബാർ മെനു
option = st.sidebar.selectbox("Choose Section", ["Home", "Wife's Expenses"])

# --- സെക്ഷനുകൾ ---

if option == "Home":
    st.header("സ്വാഗതം ഫൈസൽ!")
    st.write("കുടുംബത്തിന് വേണ്ടിയുള്ള നിന്റെ സ്വന്തം പൈത്തൺ ആപ്പ്.")

elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    
    # പാസ്‌വേഡ് സെക്ഷൻ (നീ ചോദിച്ചതുപോലെ)
    pwd = st.text_input("Enter Password", type="password")
    confirm_pwd = st.text_input("Confirm Password", type="password")
    
    if pwd != "" and confirm_pwd != "":
        if pwd == confirm_pwd:
            if pwd == EXPENSE_PASSWORD:
                st.success("Access Granted!")
                
                # ആകെ തുക കാണിക്കുന്നു
                try:
                    df = pd.read_csv(SHEET_URL_CSV)
                    # ഷീറ്റിലെ 'Amount' കോളം നമ്പറുകളാണെന്ന് ഉറപ്പുവരുത്തി കൂട്ടുന്നു
                    total_expense = pd.to_numeric(df['Amount'], errors='coerce').sum()
                    st.metric(label="ഈ മാസത്തെ ആകെ ചിലവ്", value=f"₹{total_expense}")
                except:
                    st.info("കണക്കുകൾ ശേഖരിക്കുന്നു. ആദ്യത്തെ എൻട്രി നൽകിയാൽ ഇവിടെ ടോട്ടൽ വരും.")

                st.divider()
                st.write("പുതിയ ചിലവുകൾ താഴെ കാണുന്ന ബട്ടൺ അമർത്തി രേഖപ്പെടുത്തുക.")
                st.link_button("📝 പുതിയ ചിലവ് ചേർക്കുക (Open Form)", GOOGLE_FORM_URL)
                
                st.subheader("📊 പഴയ ലിസ്റ്റ് കാണാൻ")
                st.link_button("👁️ View Full Google Sheet", SHEET_VIEW_URL)
            else:
                st.error("Incorrect Password!")
        else:
            st.warning("Passwords do not match!")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
