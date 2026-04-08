import streamlit as st
import pandas as pd

# 1. App Settings
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

st.title("🎓 PAICHI Family Hub")

# 2. Defaults (Nee itilaanu adhyam password set cheyyendathu)
if 'my_pwd' not in st.session_state:
    st.session_state['my_pwd'] = "wife123" # Default Password

# 3. Links
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfr32sd7l4p0QkWnocnhKf_jbwYsKrHT06CjZnVWD4y1a1afw/viewform"
SHEET_ID = "1Dml8r92UeygAKpnR5 (ittittu...) " # Ninte Sheet ID
SHEET_URL_CSV = f"https://docs.google.com/spreadsheets/d/1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM/export?format=csv"

# 4. Sidebar
option = st.sidebar.selectbox("Choose Section", ["Home", "Wife's Expenses", "Settings"])

# --- Home ---
if option == "Home":
    st.header("Welcome Faisal!")
    st.write("Wife's Expenses section-il poyi password adikkuka.")

# --- Wife's Expenses ---
elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    
    # Password adikkunna bagam (Aarkkum kaanan pattilla)
    pwd = st.text_input("Enter Password", type="password", help="Enter your secret password")
    confirm_pwd = st.text_input("Confirm Password", type="password", help="Re-type password to confirm")
    
    if pwd != "" and confirm_pwd != "":
        if pwd == confirm_pwd:
            if pwd == st.session_state['my_pwd']:
                st.success("Access Granted!")
                
                # Total Calculation
                try:
                    df = pd.read_csv(SHEET_URL_CSV)
                    total_expense = pd.to_numeric(df['Amount'], errors='coerce').sum()
                    st.metric(label="ഈ മാസത്തെ ആകെ ചിലവ്", value=f"₹{total_expense}")
                except:
                    st.info("No data found in sheet.")

                st.divider()
                st.link_button("📝 പുതിയ ചിലവ് ചേർക്കുക", GOOGLE_FORM_URL)
            else:
                st.error("Incorrect Password!")
        else:
            st.warning("Passwords do not match!")

# --- Settings (Password Maattan) ---
elif option == "Settings":
    st.header("⚙️ Change Password")
    old_p = st.text_input("Current Password", type="password")
    if old_p == st.session_state['my_pwd']:
        new_p = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            st.session_state['my_pwd'] = new_p
            st.success("Password Updated Successfully!")
