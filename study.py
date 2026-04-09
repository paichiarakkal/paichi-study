import streamlit as st
import pandas as pd

# നിന്റെ ഷീറ്റ് ലിങ്ക്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTupW3xiZrAzp632NVBO3SpfRKcloT_GtUfOYetoWP1ZedonX8xKWZuvluEuOel54ZLewlxXfqahVsl/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# പുതിയ കളർ സെറ്റിംഗ്‌സ് (Silver Sidebar & Gold Main)
st.markdown("""
    <style>
    /* മെയിൻ പേജ് ഗോൾഡ് കളർ */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); 
        color: #000; 
    }
    
    /* സൈഡ്‌ബാർ സിൽവർ കളർ */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; 
    }
    
    /* ടോട്ടൽ ബോക്സ് ഡിസൈൻ */
    .total-box { 
        background-color: #000; 
        color: #FFD700; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        font-size: 28px; 
        font-weight: bold; 
        border: 3px solid #FFD700; 
        margin-top: 20px; 
    }
    
    /* ടേബിൾ സ്റ്റൈൽ */
    .stDataFrame { 
        background-color: white !important; 
        border-radius: 10px; 
        padding: 10px; 
    }
    
    h1, h2, label { 
        color: black !important; 
        font-weight: bold; 
    }
    
    /* സൈഡ്‌ബാറിലെ അക്ഷരങ്ങൾ കറുപ്പ് നിറത്തിൽ വരാൻ */
    .st-emotion-cache-10trblm, .st-emotion-cache-6q9sum {
        color: black !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI Menu")
menu = st.sidebar.radio("ഇവിടെ നിന്ന് തിരഞ്ഞെടുക്കൂ:", ["🏠 Home", "💰 Home Expenses"])

if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    st.success("സ്വാഗതം ഫൈസൽ!")
    st.info("നിന്റെ ചെലവുകൾ കാണാൻ സൈഡ്‌ബാറിൽ നിന്ന് 'Home Expenses' തിരഞ്ഞെടുക്കുക.")

elif menu == "💰 Home Expenses":
    st.title("💵 Expense Tracker")
    try:
        df = pd.read_csv(CSV_URL)
        st.subheader("📊 നിലവിലുള്ള വിവരങ്ങൾ")
        st.dataframe(df, use_container_width=True)
        
        if 'Amount' in df.columns:
            total = pd.to_numeric(df['Amount'], errors='coerce').sum()
            st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
