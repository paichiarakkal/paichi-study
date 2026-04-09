import streamlit as st
import pandas as pd
import os

# 1. നിന്റെ ഗൂഗിൾ ഷീറ്റ് ലിങ്ക് (ഫോമുമായി കണക്ട് ചെയ്തത്)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nu09TIn8p6s0NJblSaH-Ji2KWDowQTLfYasPWZhO1yg/export?format=csv" 
MARK_FILE = 'marks_data.csv'

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഗോൾഡൻ തീം സ്റ്റൈൽ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .total-box { background-color: #000; color: #FFD700; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; border: 2px solid #FFD700; }
    .stTable { background-color: white !important; border-radius: 10px; color: black !important; }
    h1, h2 { color: black !important; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("Go To:", ["🏠 Home", "💰 Home Expenses", "📚 SSLC & Plus Two"])

if menu == "🏠 Home":
    st.title("🏠 Paichi Family Hub")
    st.info("ഗൂഗിൾ ഫോം വഴി വിവരങ്ങൾ നൽകിയാൽ അത് 'Home Expenses' സെക്ഷനിൽ കാണാം.")

elif menu == "💰 Home Expenses":
    st.header("💵 Expense Tracker (Live)")
    try:
        df = pd.read_csv(SHEET_URL)
        st.table(df) 
        
        # ടോട്ടൽ കണക്കാക്കുന്നു 
        # നീ ഫോമിൽ 'Items' എന്നും 'Amount' എന്നുമാണ് നൽകിയത്, അത് ഷീറ്റിലും അങ്ങനെ തന്നെയായിരിക്കും.
        if 'Amount' in df.columns:
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">Total Expense: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    except:
        st.error("ഗൂഗിൾ ഷീറ്റ് കണക്ട് ആയിട്ടില്ല. ഷീറ്റ് ലിങ്ക് പബ്ലിക് ആണെന്ന് ഉറപ്പുവരുത്തുക.")

elif menu == "📚 SSLC & Plus Two":
    st.header("📊 Mark List")
    with st.expander("പുതിയ മാർക്ക് ചേർക്കുക"):
        with st.form("mark_form", clear_on_submit=True):
            name = st.text_input("പേര്")
            cat = st.selectbox("ക്ലാസ്സ്", ["SSLC", "Plus Two"])
            mark = st.number_input("മാർക്ക്", min_value=0)
            if st.form_submit_button("Save"):
                new_data = pd.DataFrame([[name, cat, mark]], columns=['Name', 'Class', 'Mark'])
                if not os.path.isfile(MARK_FILE): new_data.to_csv(MARK_FILE, index=False)
                else: new_data.to_csv(MARK_FILE, mode='a', header=False, index=False)
                st.success("സേവ് ചെയ്തു!")
    if os.path.isfile(MARK_FILE):
        st.table(pd.read_csv(MARK_FILE))

st.sidebar.write("---")
st.sidebar.write("Designed by Faisal")
