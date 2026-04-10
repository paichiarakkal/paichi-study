import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ക്ലൗഡ് കണക്ഷൻ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI LIGHT AI", layout="wide")

# 2. Light Mode AI Design (Silver White & Gold)
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് - Soft Silver-White */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2c3e50;
    }
    
    /* സൈഡ്‌ബാർ - Clean Silver */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 2px solid #BF953F;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }

    /* AI Glass Card - Light Version */
    .glass-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 30px;
        border: 1px solid rgba(191, 149, 63, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }

    /* Total Box - Liquid Gold Glow */
    .total-box {
        background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%);
        color: #1a1a1a !important;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 40px;
        font-weight: 900;
        box-shadow: 0 15px 35px rgba(191, 149, 63, 0.3);
        border: 1px solid #ffffff;
    }

    /* AI Buttons - Gold & Silver Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: #ffffff !important;
        border-radius: 15px !important;
        padding: 15px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border: none !important;
        transition: 0.4s;
        box-shadow: 0 4px 15px rgba(191, 149, 63, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(191, 149, 63, 0.4);
    }

    /* Ticker / Status Bar */
    .status-bar {
        background: #2c3e50;
        color: #FCF6BA;
        padding: 10px;
        border-radius: 50px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
    }

    h1, h2, h3 {
        color: #1a1a1a !important;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Tables & Frames */
    .stDataFrame {
        background: white;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="status-bar">💡 PAICHI NEURAL CORE: LIGHT MODE ACTIVE 💡</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>👑 PAICHI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMAND CENTER:", ["🏠 Dashboard", "📥 Add Expense", "📊 Analytics", "🎓 Academy", "⏰ Sync"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome Faisal!")
    st.markdown("""
    <div class="glass-card">
    <h3>System Status: Stable ⚪</h3>
    <p>ലൈറ്റ് മോഡ് ഡിസൈനിൽ നിന്റെ AI ഹബ്ബ് ഇപ്പോൾ സജ്ജമാണ്. എല്ലാ വിവരങ്ങളും വോയ്‌സ് വഴിയോ ടൈപ്പ് ചെയ്തോ ചേർക്കാവുന്നതാണ്.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 📥 ADD EXPENSE ---
elif menu == "📥 Add Expense":
    st.title("📥 Neural Input")
    st.write("🎤 വോയ്‌സ് നൽകാൻ താഴെ ക്ലിക്ക് ചെയ്യുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Entry Name", value=v_in if v_in else "", placeholder="ഉദാ: പെട്രോൾ, ചായ...")
        amt = st.number_input("Value (₹)", min_value=0, value=None)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("SUCCESSFULLY SYNCED")
                except: st.error("SYNC FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 ANALYTICS ---
elif menu == "📊 Analytics":
    if "is_auth" not in st.session_state: st.session_state["is_auth"] = False
    if not st.session_state["is_auth"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Enter Access Key", type="password")
        if st.button("UNLOCK"):
            if pwd == "1234":
                st.session_state["is_auth"] = True
                st.rerun()
            else: st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📊 Intelligence Report")
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, 
                             color_discrete_sequence=["#BF953F", "#C0C0C0", "#B38728", "#808080"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Activity Data")
                st.dataframe(df.tail(15), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info("Coming soon...")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v5.0 | Light Edition")
