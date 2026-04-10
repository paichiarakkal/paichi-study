import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# നിന്റെ ഷീറ്റ് ലിങ്ക്
# ശ്രദ്ധിക്കുക: ഷീറ്റ് 'Editor' ആക്സസ് നൽകിയിട്ടുണ്ടെന്ന് ഉറപ്പാക്കുക
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BfS6I2-2L9Y9xYVq5q8W7W7W7W7W7W7W7W7W7W7W7W7W7/edit#gid=663160667"

# ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; border: 3px solid #FFD700; margin-bottom: 20px; }
    h1, h2, h3, label { color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💵 Family Expense Tracker")

# ഷീറ്റുമായി കണക്ട് ചെയ്യുന്നു
conn = st.connection("gsheets", type=GSheetsConnection)

# ഡാറ്റ വായിക്കുന്നു
try:
    df = conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3])
    df.columns = ['Timestamp', 'Date', 'Item', 'Amount']
except:
    df = pd.DataFrame(columns=['Timestamp', 'Date', 'Item', 'Amount'])

# പുതിയ ഡാറ്റ ചേർക്കാനുള്ള ഫോം
with st.expander("➕ പുതിയ ചെലവ് ചേർക്കുക", expanded=True):
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        item_val = col1.text_input("Item Name (സാധനം)")
        price_val = col2.number_input("Amount (തുക)", min_value=0)
        
        if st.form_submit_button("Save Directly to Sheet"):
            if item_val and price_val:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Item": item_val,
                    "Amount": price_val
                }])
                # ഷീറ്റിലേക്ക് ഡാറ്റ ചേർക്കുന്നു
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success(f"{item_val} സേവ് ചെയ്തു!")
                st.balloons()
                st.rerun()

st.write("---")

# ഡിസ്പ്ലേ
if not df.empty:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    total = df['Amount'].sum()
    st.markdown(f'<div class="total-box">ആകെ ചെലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📋 ഹിസ്റ്ററി")
        st.dataframe(df.tail(10), use_container_width=True)
    with c2:
        st.subheader("📊 വിഭജനം")
        fig = px.pie(df, values='Amount', names='Item', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ഷീറ്റിൽ ഡാറ്റ ലോഡ് ചെയ്യുന്നു...")
