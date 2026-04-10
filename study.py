import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI HUB", layout="wide")

# 2. അസ്സൽ AI ഡിസൈൻ (Dark mode with Gold & Neon Glow)
st.markdown("""
    <style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp {
        background: radial-gradient(circle at center, #1e1e2f 0%, #000000 100%);
        color: #ffffff;
    }
    
    /* സൈഡ്ബാർ */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 15, 0.9) !important;
        border-right: 1px solid #BF953F;
    }

    /* ഗ്ലാസ് കാർഡ് ഇഫക്റ്റ് */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 30px;
        border: 1px solid rgba(191, 149, 63, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }

    /* ടോട്ടൽ തുക ബോക്സ് (Gold Glow) */
    .total-box {
        background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%);
        color: #000 !important;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        font-size: 38px;
        font-weight: 900;
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.4);
        margin: 20px 0;
        text-transform: uppercase;
    }

    /* പ്രീമിയം ബട്ടണുകൾ */
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: black !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 18px !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.4s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(191, 149, 63, 0.6);
    }

    /* ടിക്കർ ലൈൻ */
    .ticker-container {
        background: #BF953F;
        color: black;
        padding: 10px;
        font-weight: bold;
        border-radius: 50px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 0 15px rgba(191, 149, 63, 0.3);
    }

    /* ഹെഡിംഗുകൾ */
    h1, h2, h3 {
        color: #FCF6BA !important;
        text-shadow: 0 0 10px rgba(191, 149, 63, 0.2);
    }

    /* ഇൻപുട്ട് ഫീൽഡുകൾ */
    input {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(191, 149, 63, 0.5) !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ടിക്കർ
st.markdown('<div class="ticker-container">🚀 PAICHI AI HUB V4.0 | NEXT-GEN FINANCIAL TRACKING 🚀</div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except:
        return pd.DataFrame()

# സൈഡ്‌ബാർ മെനു
st.sidebar.markdown("<h1 style='text-align: center;'>💎 PAICHI</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("Navigate:", 
    ["🏠 Home", "💰 Add Expense", "📊 Smart Analytics", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    st.title(f"Welcome back, Faisal!")
    st.markdown("""
    <div class="glass-card">
    <h3>System Status: Online 🟢</h3>
    <p>നിന്റെ വ്യക്തിഗത AI ഹബ്ബ് ഇപ്പോൾ സജ്ജമാണ്. ഡാറ്റ നൽകാൻ <b>Add Expense</b> ടാബിൽ പോകുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 💰 ADD EXPENSE ---
elif menu == "💰 Add Expense":
    st.title("💵 Intelligent Entry")
    st.write("🎤 വോയ്‌സ് നൽകാൻ താഴെ അമർത്തുക:")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("ai_form", clear_on_submit=True):
        item = st.text_input("Item Description", value=v_in if v_in else "", placeholder="ഉദാ: ചായ, ഫുഡ്‌...")
        amt = st.number_input("Amount (₹)", min_value=0, value=None)
        
        if st.form_submit_button("SYNC TO CLOUD"):
            if item and amt:
                payload = {
                    "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                    "entry.1896057694": item, 
                    "entry.1570426033": str(amt)
                }
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.balloons()
                    st.success(f"Data Synced: {item} - ₹{amt}")
                except:
                    st.error("Sync Failed!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 SMART ANALYTICS ---
elif menu == "📊 Smart Analytics":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    
    if not st.session_state["unlocked"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Enter Access Code", type="password")
        if st.button("AUTHENTICATE"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("Access Denied!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("📊 Financial Intelligence")
        if st.sidebar.button("🔒 Lock Database"):
            st.session_state["unlocked"] = False
            st.rerun()
            
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">TOTAL SPENT: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, 
                             color_discrete_sequence=px.colors.sequential.Gold)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Activity Log")
                st.dataframe(df.tail(15), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# --- മറ്റുള്ളവ ---
elif menu in ["🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"]:
    st.title(menu)
    st.markdown('<div class="glass-card">ഈ ഭാഗം ഇപ്പോൾ അപ്‌ഡേറ്റ് ചെയ്തുകൊണ്ടിരിക്കുകയാണ്.</div>', unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.write("System: PAICHI AI v4.0")
