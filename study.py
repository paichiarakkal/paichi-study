import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ആപ്പിന്റെ സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

st.title("🎓 PAICHI Family Education & Expense Portal")

# പാസ്‌വേഡുകൾ (നിനക്ക് ഇഷ്ടമുള്ളത് മാറ്റാം)
SSLC_PASSWORD = "sslc123"
PLUS2_PASSWORD = "plus123"
EXPENSE_PASSWORD = "wife123"

# ഗൂഗിൾ ഷീറ്റ് ലിങ്ക്
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Dml8r92UeygAKpnR5QNMkzcM4q3UEb2IwirHJ9otYSM/edit?usp=sharing"

# സൈഡ്ബാർ മെനു
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "SSLC Student", "Plus Two Student", "Wife's Expenses", "Photo Gallery", "Maths Lab (Loops)", "Study Resources"])

# 1. ഹോം പേജ്
if option == "Home":
    st.header("സ്വാഗതം ഫൈസൽ!")
    st.write("ഈ ആപ്പ് ഇപ്പോൾ നിന്റെ ഗൂഗിൾ ഷീറ്റുമായി കണക്ട് ചെയ്തിരിക്കുന്നു.")
    st.image("https://img.freepik.com/free-vector/graduation-cap-with-diploma-scroll-realistic-style_1284-18155.jpg", width=300)

# 2. വൈഫിന്റെ എക്സ്പെൻസ് സെക്ഷൻ
elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    pwd = st.text_input("Enter Password", type="password")
    
    if pwd == EXPENSE_PASSWORD:
        st.success("Access Granted!")
        
        # ഗൂഗിൾ ഷീറ്റുമായി കണക്ട് ചെയ്യുന്നു
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # പഴയ ഡാറ്റ വായിക്കുന്നു
        try:
            df = conn.read(spreadsheet=SHEET_URL)
        except:
            df = pd.DataFrame(columns=["Date", "Item", "Amount"])

        with st.form("expense_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1: date = st.date_input("Date")
            with col2: item = st.text_input("Item (സാധനം)")
            with col3: amount = st.number_input("Amount (തുക)", min_value=0)
            
            if st.form_submit_button("Save to Cloud"):
                if item and amount > 0:
                    new_data = pd.DataFrame([{"Date": str(date), "Item": item, "Amount": amount}])
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, data=updated_df)
                    st.success("വിജയകരമായി സേവ് ചെയ്തു!")
                    st.rerun()
                else:
                    st.error("വിവരങ്ങൾ കൃത്യമായി നൽകുക.")

        # ഷീറ്റിലുള്ള ഡാറ്റ കാണിക്കുന്നു
        if not df.empty:
            st.divider()
            st.subheader("📊 ഈ മാസത്തെ മുഴുവൻ കണക്ക്")
            st.table(df)
            st.metric("Total Expense", f"₹{df['Amount'].sum()}")

    elif pwd != "":
        st.error("Wrong Password!")

# 3. SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Mark Entry")
    pwd_s = st.text_input("Enter SSLC Password", type="password")
    if pwd_s == SSLC_PASSWORD:
        name = st.text_input("Student Name")
        maths = st.number_input("Maths", 0, 100)
        if st.button("Generate"):
            st.success(f"ഹലോ {name}, മാർക്ക് സേവ് ചെയ്തു.")
            st.balloons()

# 4. പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Grade Tracker")
    pwd_p = st.text_input("Enter Plus Two Password", type="password")
    if pwd_p == PLUS2_PASSWORD:
        st.write("ഗ്രേഡുകൾ ഇവിടെ എന്റർ ചെയ്യാം.")
        st.snow()

# 5. ഫോട്ടോ ഗാലറി
elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg", caption="Family Time ❤️")

# 6. മാത്സ് ലാബ്
elif option == "Maths Lab (Loops)":
    st.header("🔢 Multiplication Table")
    num = st.number_input("Number", value=5)
    for i in range(1, 11):
        st.write(f"{num} x {i} = {num*i}")

# 7. സ്റ്റഡി റിസോഴ്‌സസ്
elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Books", "https://samagra.kite.kerala.gov.in/#/textbook/view")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
