import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിങ്ങളുടെ പുതിയ ലിങ്കുകൾ
# ശ്രദ്ധിക്കുക: FORM_URL_API എന്നത് ഗൂഗിൾ ഫോമിന് ഡാറ്റ അയക്കാൻ ഉപയോഗിക്കുന്ന ലിങ്ക് ആണ്.
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRmFHWgvrzRobTTuiUO4pMbZ8QP1dAuBsn1hCaUf2ON7Bow1SeR2xHjYwupJZYYfMHW_Mm8pmtLUFA/pub?gid=663160667&single=true&output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLSfAsUoTDzCoAij8_2euuWhWJZRDe4TqEhx2TqWeBRNIqj2rjA/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# 2. ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 20px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 3px solid #FFD700; margin-top: 20px; }
    .glass-card { background: rgba(255, 255, 255, 0.4); border-radius: 15px; padding: 20px; border: 1px solid rgba(0,0,0,0.1); margin-bottom: 15px; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; border-radius: 10px !important; border: 2px solid #FFD700 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# വോയ്‌സ് പ്രോസസ്സിംഗ്
def process_voice(text):
    num_map = {'ഒന്ന്': '1', 'രണ്ട്': '2', 'മൂന്ന്': '3', 'നാല്': '4', 'അഞ്ച്': '5', 'പത്ത്': '10', 'ഇരുപത്': '20', 'അമ്പത്': '50', 'നൂറ്': '100'}
    words = text.split()
    item, amt = "", None
    for word in words:
        if word.isdigit(): amt = int(word)
        elif word in num_map: amt = int(num_map[word])
        else: item += word + " "
    return item.strip(), amt

def load_data():
    try:
        # ക്യാഷ് ഒഴിവാക്കാൻ റാൻഡം നമ്പർ ഉപയോഗിക്കുന്നു
        url = f"{CSV_URL}&ref={random.randint(1, 9999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് | പുതിയ ഫോം ലിങ്കുകൾ അപ്‌ഡേറ്റ് ചെയ്തു | വോയ്‌സ് കമാൻഡ് റെഡിയാണ് 📢</div></div>', unsafe_allow_html=True)

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add & View)", "📊 Reports", "✅ To-Do List", "⏰ Reminders"])

# --- 🏠 Home ---
if menu == "🏠 Home":
    st.title("🏠 PAICHI Family Hub")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">Total Spending: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
    st.write("സ്വാഗതം ഫൈസൽ! നിലവിലെ ചിലവ് വിവരങ്ങൾ മുകളിൽ കാണാം.")

# --- 💰 Expenses ---
elif menu == "💰 Expenses (Add & View)":
    st.title("💵 Expense Management")
    
    st.write("🎙️ വോയ്‌സ് വഴി ചേർക്കാൻ താഴെ ക്ലിക്ക് ചെയ്യൂ")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ (ഉദാ: ചായ 10)...", key='voice')
    auto_item, auto_amt = process_voice(v_in) if v_in else ("", None)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("➕ Add Entry")
        with st.form("input_form", clear_on_submit=True):
            item = st.text_input("ഐറ്റം പേര്", value=auto_item)
            amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
            
            # ശ്രദ്ധിക്കുക: നിങ്ങളുടെ ഗൂഗിൾ ഫോമിലെ entry ID-കൾ പഴയതാണെങ്കിൽ അത് ഇവിടെ മാറ്റേണ്ടി വരും
            if st.form_submit_button("SAVE TO CLOUD"):
                if item and amt:
                    payload = {
                        "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.1896057694": item, 
                        "entry.1570426033": str(amt)
                    }
                    try:
                        requests.post(FORM_URL_API, data=payload)
                        st.success(f"{item} - ₹{amt} സേവ് ചെയ്തു! ✅")
                    except:
                        st.error("ഗൂഗിൾ ഷീറ്റിലേക്ക് അയക്കാൻ കഴിഞ്ഞില്ല.")
    
    with col2:
        st.subheader("📋 Recent History")
        df = load_data()
        if not df.empty:
            st.dataframe(df.tail(10), use_container_width=True) # അവസാന 10 എണ്ണം കാണിക്കുന്നു
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box" style="font-size:20px; border-width: 1px;">Total: ₹ {total:,.2f}</div>', unsafe_allow_html=True)

# --- 📊 Reports ---
elif menu == "📊 Reports":
    st.title("📊 Monthly Analysis")
    df = load_data()
    if not df.empty:
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        # ബാർ ചാർട്ട് കൂടി ചേർക്കുന്നു
        st.subheader("Daily Spending Trend")
        df_daily = df.groupby(df.columns[0])['Amount'].sum().reset_index()
        fig2 = px.bar(df_daily, x=df_daily.columns[0], y='Amount', color_discrete_sequence=['#FFD700'])
        st.plotly_chart(fig2, use_container_width=True)

# --- ✅ To-Do List ---
elif menu == "✅ To-Do List":
    st.title("✅ Tasks")
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    t = st.text_input("ടാസ്ക് ചേർക്കുക:")
    if st.button("Add Task"):
        if t: st.session_state.tasks.append(t); st.rerun()
    for i, task in enumerate(st.session_state.tasks):
        st.markdown(f'<div class="glass-card">🔹 {task}</div>', unsafe_allow_html=True)

# --- ⏰ Reminders ---
elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

st.sidebar.write("---")
st.sidebar.write("PAICHI v15.7 | Design by Faisal")
