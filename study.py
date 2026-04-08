import streamlit as st
import pandas as pd
import random

# ആപ്പിന്റെ സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

st.title("🎓 PAICHI Family Education & Expense Portal")

# പാസ്‌വേഡുകൾ
SSLC_PASSWORD = "sslc123"
PLUS2_PASSWORD = "plus123"
EXPENSE_PASSWORD = "wife123"

# സൈഡ്ബാർ മെനു
st.sidebar.title("📌 Main Menu")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "Wife's Expenses", "SSLC Student", "Plus Two Student", "Photo Gallery", "Maths Lab (Loops)", "Study Resources"])

# എക്സ്പെൻസ് ഡാറ്റ സൂക്ഷിക്കാൻ (Session State)
if 'expense_data' not in st.session_state:
    st.session_state.expense_data = pd.DataFrame(columns=["Date", "Item", "Amount"])

# 1. ഹോം പേജ്
if option == "Home":
    st.header("സ്വാഗതം ഫൈസൽ!")
    st.write("നിന്റെ കുടുംബത്തിന് ആവശ്യമായ എല്ലാ കാര്യങ്ങളും ഇപ്പോൾ ഈ ഒരു ആപ്പിൽ ലഭ്യമാണ്.")
    st.image("https://img.freepik.com/free-vector/graduation-cap-with-diploma-scroll-realistic-style_1284-18155.jpg", width=300)

# 2. വൈഫിന്റെ എക്സ്പെൻസ് സെക്ഷൻ
elif option == "Wife's Expenses":
    st.header("💰 Wife's Monthly Expense Tracker")
    pwd = st.text_input("Enter Password", type="password")
    
    if pwd == EXPENSE_PASSWORD:
        st.success("Access Granted!")
        
        with st.form("expense_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1: date = st.date_input("Date")
            with col2: item = st.text_input("Item (സാധനം)")
            with col3: amount = st.number_input("Amount (തുക)", min_value=0)
            
            if st.form_submit_button("Add to List"):
                if item and amount > 0:
                    new_row = pd.DataFrame([{"Date": str(date), "Item": item, "Amount": amount}])
                    st.session_state.expense_data = pd.concat([st.session_state.expense_data, new_row], ignore_index=True)
                    st.success("ലിസ്റ്റിലേക്ക് ചേർത്തു!")
                else:
                    st.error("വിവരങ്ങൾ കൃത്യമായി നൽകുക.")

        # ലിസ്റ്റ് കാണിക്കുന്നു
        if not st.session_state.expense_data.empty:
            st.divider()
            st.subheader("📊 ഈ മാസത്തെ മുഴുവൻ കണക്ക്")
            st.table(st.session_state.expense_data)
            
            total = st.session_state.expense_data["Amount"].sum()
            st.metric("Total Expense", f"₹{total}")
            
            # ഡാറ്റ സേവ് ചെയ്യാൻ ഡൗൺലോഡ് ബട്ടൺ
            csv = st.session_state.expense_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Expenses (CSV)",
                data=csv,
                file_name='family_expenses.csv',
                mime='text/csv',
            )
            st.info("ശ്രദ്ധിക്കുക: ആപ്പ് റിഫ്രഷ് ചെയ്യുന്നതിന് മുൻപ് ഈ ബട്ടൺ അമർത്തി ഡാറ്റ സേവ് ചെയ്യുക.")
    elif pwd != "":
        st.error("Wrong Password!")

# 3. SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Student Zone")
    pwd = st.text_input("SSLC Password", type="password")
    if pwd == SSLC_PASSWORD:
        st.success("Welcome Student!")
        name = st.text_input("Name")
        score = st.slider("Estimate your Score", 0, 100)
        if st.button("Save Progress"):
            st.write(f"{name}-ന്റെ സ്കോർ {score} ആയി രേഖപ്പെടുത്തി.")
            st.balloons()
    elif pwd != "":
        st.error("Wrong Password!")

# 4. പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Student Zone")
    pwd = st.text_input("Plus Two Password", type="password")
    if pwd == PLUS2_PASSWORD:
        st.success("Welcome Plus Two Student!")
        st.write("നിന്റെ പാഠപുസ്തകങ്ങളും നോട്ട്സും ഇവിടെ ക്രമീകരിക്കാം.")
        st.snow()
    elif pwd != "":
        st.error("Wrong Password!")

# 5. ഫോട്ടോ ഗാലറി
elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg", caption="Family Time ❤️")

# 6. മാത്സ് ലാബ് (Loops)
elif option == "Maths Lab (Loops)":
    st.header("🔢 Multiplication Table Generator")
    num = st.number_input("Enter Number", value=5)
    if st.button("Generate Table"):
        for i in range(1, 11):
            st.write(f"{num} x {i} = **{num * i}**")

# 7. സ്റ്റഡി റിസോഴ്‌സസ്
elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.link_button("Download Books (SSLC & +2)", "https://samagra.kite.kerala.gov.in/#/textbook/view")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: Faisal")
