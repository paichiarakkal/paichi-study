import streamlit as st
import pandas as pd

# 1. നീ പബ്ലിഷ് ചെയ്തപ്പോൾ കിട്ടിയ പുതിയ CSV ലിങ്ക്
NEW_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTupW3xiZrAzp632NVBO3SpfRKcloT_GtUfOYetoWP1ZedonX8xKWZuvluEuOel54ZLewlxXfqahVsl/pub?output=csv"

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# ഗോൾഡൻ തീം സ്റ്റൈൽ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; border: 3px solid #FFD700; margin-top: 20px; }
    .stDataFrame { background-color: white !important; border-radius: 10px; padding: 10px; }
    h1 { color: black !important; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏠 PAICHI Live Tracker")

try:
    # ഷീറ്റിൽ നിന്നും വിവരങ്ങൾ എടുക്കുന്നു
    df = pd.read_csv(NEW_SHEET_URL)
    
    st.subheader("📊 Expense List")
    
    # പട്ടിക കാണിക്കുന്നു
    st.dataframe(df, use_container_width=True)
    
    # 'Amount' കോളത്തിലെ തുകകൾ കൂട്ടുന്നു
    if 'Amount' in df.columns:
        # നമ്പറുകൾ ആണെന്ന് ഉറപ്പുവരുത്തുന്നു
        total = pd.to_numeric(df['Amount'], errors='coerce').sum()
        st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    else:
        st.warning("ഷീറ്റിൽ 'Amount' എന്ന കോളം കാണുന്നില്ല. ഹെഡർ പരിശോധിക്കുക.")

except Exception as e:
    st.error("ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ഷീറ്റ് പബ്ലിഷ് ചെയ്തിട്ടുണ്ടെന്ന് ഉറപ്പുവരുത്തുക.")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal")
