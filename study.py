import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ (നിന്റെ പുതിയ ലിങ്കുകൾ തന്നെ)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI PREMIUM", layout="wide")

# 2. അസ്സൽ AI ഡിസൈൻ സെറ്റിംഗ്സ് (Dark, Gold & Glass Effect)
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a1a, #000000);
        color: #e0e0e0;
    }
    
    /* സൈഡ്‌ബാർ */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 2px solid #BF953F;
    }

    /* ഗ്ലാസ് മോർഫിസം ബോക്സ് */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* ടോട്ടൽ തുക കാണിക്കുന്ന ബോക്സ് */
    .total-box {
        background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%);
        color: #000 !important;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        font-size: 35px;
        font-weight: 900;
        box-shadow: 0 10px 20px rgba(191, 149, 63, 0.3);
        margin: 20px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* ബട്ടൺ സ്റ്റൈൽ */
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: bold !important;
        transition: 0.3s all;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(191, 149, 63, 0.5);
    }

    /* ടിക്കർ ലൈൻ */
    .ticker-wrap {
        background: #BF953F;
        color: #000;
        padding: 8px;
        font-weight: bold;
        border-radius: 50px;
        margin-bottom: 30px;
        text-align: center;
    }

    /* ടെക്സ്റ്റ് കളറുകൾ */
    h1, h2, h3, p, label {
        color: #FCF6BA !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* ഇൻപുട്ട് ഫീൽഡുകൾ */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #BF953F !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ടിക്കർ
st.markdown('<div class="ticker-wrap">✨ PAICHI AI PREMIUM HUB | INTELLIGENT EXPENSE TRACKING ✨</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except:
        return pd.DataFrame()

# സൈഡ്‌ബാർ
st.sidebar.markdown("<h2 style='text-align:center;'>💎 PAICHI</h2>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("Navigation", 
    ["🏠 Dashboard", "💰 Add Expense", "📊 Reports", "🎓 Academy", "⏰ Alerts"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome back, Faisal!")
    st.markdown("""
    <div class="glass-card">
    <h3>Hello! 👋</h3>
    <p>നിന്റെ ചിലവുകൾ ട്രാക്ക് ചെയ്യാനും റിപ്പോർട്ടുകൾ കാണാനും ഈ AI ഡാഷ്‌ബോർഡ് സഹായിക്കും. 
    തുടങ്ങാൻ സൈഡ്‌ബാറിൽ നിന്ന് <b>Add Expense</b> തിരഞ്ഞെടുക്കുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 💰 ADD EXPENSE (Premium Look) ---
elif menu == "💰 Add Expense":
    st.title("💎 Smart Entry")
    
    st.write("🎤 വോയ്‌സ് വഴി ഡാറ്റ ചേർക്കാൻ താഴെ അമർത്തുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("premium_form", clear_on_submit=True):
        item = st.text_input("Item Name", value=v_in if v_in else "", placeholder="ഉദാ: പെട്രോൾ")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        
        submit = st.form_submit_button("SECURE SAVE")
        if submit:
            if item and amt:
                payload = {
                    "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.1896057694": item, 
                    "entry.1570426033": str(amt)
                }
                requests.post(FORM_URL_API, data=payload)
                st.balloons()
                st.success(f"Successfully added {item} to Cloud!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 REPORTS ---
elif menu == "📊 Reports":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    
    if not st.session_state["unlocked"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Enter Access Key", type="password")
        if st.button("AUTHENTICATE"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("Access Denied!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📊 AI Analytics")
        if st.sidebar.button("🔒 Lock"):
            st.session_state["unlocked"] = False
            st.rerun()
            
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.4, 
                             color_discrete_sequence=px.colors.sequential.Gold_r)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Transactions")
                st.dataframe(df.tail(10), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No data found in cloud.")

# --- 🎓 ACADEMY & ALERTS ---
elif menu in ["🎓 Academy", "⏰ Alerts"]:
    st.title(menu)
    st.write("This section is being synchronized...")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI Hub v4.0")
