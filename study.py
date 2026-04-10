import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നീ തന്ന പുതിയ ലിങ്കുകൾ ഞാൻ ഇവിടെ സെറ്റ് ചെയ്തിട്ടുണ്ട്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI HUB", layout="wide")

# 2. പ്രീമിയം AI ഡിസൈൻ
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #1e1e2f 0%, #000000 100%); color: #ffffff; }
    [data-testid="stSidebar"] { background: rgba(15, 15, 15, 0.9) !important; border-right: 1px solid #BF953F; }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); border-radius: 25px; padding: 30px; border: 1px solid rgba(191, 149, 63, 0.3); margin-bottom: 25px; }
    .total-box { background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%); color: #000 !important; padding: 35px; border-radius: 20px; text-align: center; font-size: 35px; font-weight: 900; box-shadow: 0 0 30px rgba(191, 149, 63, 0.4); margin: 20px 0; }
    .stButton>button { background: linear-gradient(90deg, #BF953F, #AA771C) !important; color: black !important; border-radius: 15px !important; font-weight: bold !important; height: 55px; }
    h1, h2, h3 { color: #FCF6BA !important; }
    .ticker-container { background: #BF953F; color: black; padding: 10px; font-weight: bold; border-radius: 50px; text-align: center; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="ticker-container">🚀 PAICHI AI HUB V4.0 | CONNECTED TO CLOUD 🚀</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

st.sidebar.markdown("<h1 style='text-align: center;'>💎 PAICHI</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("Navigate:", ["🏠 Home", "💰 Add Expense", "📊 Smart Analytics", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    st.title(f"Welcome back, Faisal!")
    st.markdown('<div class="glass-card"><h3>System Ready 🟢</h3><p>ചിലവുകൾ രേഖപ്പെടുത്താൻ <b>Add Expense</b> പേജിൽ പോകുക. നിന്റെ ഡാറ്റ ഇപ്പോൾ പുതിയ ഷീറ്റുമായി കണക്ട് ചെയ്തിട്ടുണ്ട്.</p></div>', unsafe_allow_html=True)

# --- 💰 ADD EXPENSE ---
elif menu == "💰 Add Expense":
    st.title("💵 Intelligent Entry")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("ai_form", clear_on_submit=True):
        item = st.text_input("Item Description", value=v_in if v_in else "")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        if st.form_submit_button("SYNC TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success(f"Synced: {item}")
                except: st.error("Sync Error!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 SMART ANALYTICS (ERROR FIXED) ---
elif menu == "📊 Smart Analytics":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    if not st.session_state["unlocked"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Enter Access Code", type="password")
        if st.button("AUTHENTICATE"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("Wrong Code!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📊 Financial Intelligence")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                # ERROR ശരിയാക്കിയ ഭാഗം താഴെ:
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, 
                             color_discrete_sequence=["#BF953F", "#FCF6BA", "#B38728"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.dataframe(df.tail(10), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.warning("No data found.")

else:
    st.title(menu)
    st.info("Coming Soon...")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v4.0")
