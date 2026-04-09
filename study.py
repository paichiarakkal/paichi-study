import streamlit as st
import pandas as pd

# 1. നീ പബ്ലിഷ് ചെയ്ത പുതിയ ലിങ്ക്
NEW_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTupW3xiZrAzp632NVBO3SpfRKcloT_GtUfOYetoWP1ZedonX8xKWZuvluEuOel54ZLewlxXfqahVsl/pub?output=csv"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഗോൾഡൻ തീം സ്റ്റൈൽ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #000 !important; }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; margin-top: 20px; }
    .stDataFrame { background-color: white !important; border-radius: 10px; padding: 10px; }
    h1, h2, label { color: black !important; font-weight: bold; }
    .css-17l2qt2 { color: #FFD700 !important; } /* സൈഡ്‌ബാറിലെ അക്ഷരങ്ങൾക്കായി */
    </style>
    """, unsafe_allow_html=True)

# 2. സൈഡ്‌ബാർ മെനു (ഇതാണ് നിന്റെ ആപ്പിൽ ഇപ്പോൾ കാണാത്തത്)
st.sidebar.title("PAICHI Menu")
menu = st.sidebar.radio("ഇവിടെ നിന്ന് തിരഞ്ഞെടുക്കൂ:", ["🏠 Home", "💰 Home Expenses", "📊 Marks"])

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.success("സ്വാഗതം ഫൈസൽ!")
    st.info("നിന്റെ ചെലവുകൾ കാണാൻ സൈഡ്‌ബാറിൽ നിന്ന് 'Home Expenses' തിരഞ്ഞെടുക്കുക.")

elif menu == "💰 Home Expenses":
    st.title("💵 Expense Tracker")
    try:
        # ഷീറ്റിൽ നിന്ന് ഡാറ്റ എടുക്കുന്നു
        df = pd.read_csv(NEW_SHEET_URL)
        
        st.subheader("📊 നിലവിലുള്ള വിവരങ്ങൾ")
        # പട്ടിക കാണിക്കുന്നു
        st.dataframe(df, use_container_width=True)
        
        # 'Amount' കോളത്തിലെ തുക കൂട്ടുന്നു
        if 'Amount' in df.columns:
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        else:
            st.warning("ഷീറ്റിൽ 'Amount' എന്ന കോളം കാണുന്നില്ല. ഹെഡർ പരിശോധിക്കുക.")

    except Exception as e:
        st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. പബ്ലിഷ് സെറ്റിംഗ്സ് ഒന്നുകൂടി നോക്കുക.")

elif menu == "📊 Marks":
    st.title("📚 Student Marks")
    st.write("ഈ ഭാഗം ഉടനെ അപ്‌ഡേറ്റ് ചെയ്യുന്നതാണ്.")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
