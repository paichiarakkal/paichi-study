import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ പുതിയ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI ITALIAN LUXURY", layout="wide")

# 2. Italian Marble & Gold/Silver AI Design
st.markdown("""
    <style>
    /* Italian Marble Background */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
                    url('https://www.transparenttextures.com/patterns/white-diamond.png');
        background-color: #f4f4f4;
        color: #1a1a1a;
    }
    
    /* Sidebar: Italian Deep Grey/Silver */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #000000 100%) !important;
        border-right: 3px solid #BF953F;
    }

    /* Glassmorphism Card with Silver Border */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 2px solid #C0C0C0;
        box-shadow: 10px 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Total Box: Italian Gold & Silver Mix */
    .total-box {
        background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 25%, #C0C0C0 50%, #FCF6BA 75%, #B38728 100%);
        color: #1a1a1a !important;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        font-size: 38px;
        font-weight: 900;
        box-shadow: 0 10px 25px rgba(184, 134, 11, 0.4);
        margin: 20px 0;
        border: 1px solid #ffffff;
    }

    /* Buttons: Metallic Gold */
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #BF953F) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
    }

    /* Ticker */
    .ticker-wrap {
        background: #1a1a1a;
        color: #D4AF37;
        padding: 10px;
        font-weight: bold;
        border-radius: 10px;
        text-align: center;
        border-bottom: 3px solid #BF953F;
    }

    h1, h2, h3 {
        color: #1a1a1a !important;
        font-family: 'Playfair Display', serif;
    }
    
    label { color: #1a1a1a !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="ticker-wrap">🏛️ PAICHI AI HUB | ITALIAN MARBLE EDITION | LUXURY TRACKING 🏛️</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h1 style='color: #D4AF37 !important; text-align: center;'>👑 PAICHI</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("Navigate:", ["🏠 Home", "💰 Add Expense", "📊 Smart Analytics", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    st.title("Welcome, Faisal")
    st.markdown("""
    <div class="glass-card">
    <h3 style="color: #B38728 !important;">Luxury AI Assistant</h3>
    <p>നിന്റെ ചിലവുകളും റിപ്പോർട്ടുകളും പ്രീമിയം ലുക്കിൽ കാണാൻ ഈ സിസ്റ്റം സഹായിക്കും. 
    <b>Add Expense</b> ടാബിലൂടെ വോയ്‌സ് വഴി ഡാറ്റ നൽകാം.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 💰 ADD EXPENSE ---
elif menu == "💰 Add Expense":
    st.title("💳 Premium Entry")
    st.write("🎤 വോയ്‌സ് റെക്കോർഡ് ചെയ്യാൻ താഴെ അമർത്തുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("luxury_form", clear_on_submit=True):
        item = st.text_input("Item Name", value=v_in if v_in else "", placeholder="ഉദാ: ഫുഡ്‌")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        if st.form_submit_button("SYNC TO CLOUD"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.balloons()
                    st.success(f"{item} - ₹{amt} ക്ലൗഡിലേക്ക് മാറ്റി!")
                except: st.error("Error!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 SMART ANALYTICS ---
elif menu == "📊 Smart Analytics":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    if not st.session_state["unlocked"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Security Key", type="password")
        if st.button("AUTHENTICATE"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("Wrong Key!")
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
                             color_discrete_sequence=["#BF953F", "#C0C0C0", "#B38728", "#E5E4E2"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.dataframe(df.tail(10), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title(menu)
    st.info("ഈ സെക്ഷൻ ഉടൻ അപ്‌ഡേറ്റ് ചെയ്യും...")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v4.0 | Luxury Edition")
