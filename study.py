import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ ലിങ്കുകൾ (ഇത് മാറ്റരുത്)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI DEEP AI", layout="wide")

# 2. Deep Dark AI Design (Pure Black, Gold & Silver)
st.markdown("""
    <style>
    /* കട്ട കറുപ്പ് ബാക്ക്ഗ്രൗണ്ട് */
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 50%, #111111 0%, #000000 100%);
        color: #ffffff;
    }
    
    /* സൈഡ്‌ബാർ - Neon Silver Border */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #C0C0C0;
    }

    /* AI Glass Card - Dark Glow */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(191, 149, 63, 0.3);
        box-shadow: 0 0 20px rgba(191, 149, 63, 0.1);
        margin-bottom: 20px;
    }

    /* Total Spent Box - High Contrast Gold */
    .total-box {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #BF953F !important; /* Gold Color */
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 48px;
        font-weight: 900;
        border: 3px solid #BF953F;
        box-shadow: 0 0 40px rgba(191, 149, 63, 0.4);
        margin: 20px 0;
        text-shadow: 0 0 15px rgba(252, 246, 186, 0.6);
    }

    /* AI Buttons - Silver to Gold Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #C0C0C0, #BF953F) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        transition: 0.5s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.7);
    }

    /* Ticker */
    .ticker {
        background: #BF953F;
        color: #000;
        padding: 10px;
        font-weight: 900;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }

    h1, h2, h3 {
        color: #FCF6BA !important;
    }

    /* Input Fields */
    input {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid #C0C0C0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="ticker">🚀 PAICHI AI CORE: DEEP DARK MODE ACTIVE | SYSTEM SECURE 🚀</div>', unsafe_allow_html=True)

# ഡാറ്റ ലോഡ് ചെയ്യുന്ന ഫങ്ക്ഷൻ (Auto Refresh ശരിയാക്കിയത്)
def load_data():
    try:
        # random number ചേർക്കുന്നത് വഴി ഗൂഗിൾ ഷീറ്റിൽ നിന്ന് എപ്പോഴും പുതിയ ഡാറ്റ വരും
        url = f"{CSV_URL}&cache_bust={random.randint(1, 99999)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except:
        return pd.DataFrame()

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center;'>👾</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMAND:", ["🏠 Dashboard", "💰 Add Entry", "📊 Intelligence", "🎓 Academy", "⏰ Sync"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Neural Access: Faisal")
    st.markdown("""
    <div class="glass-card">
    <h3 style="color: #BF953F !important;">AI Status: Optimal 🟢</h3>
    <p>നിന്റെ എല്ലാ വിവരങ്ങളും സുരക്ഷിതമാണ്. WhatsApp-ൽ ടോട്ടൽ വരാൻ ഡാറ്റ നൽകി കഴിഞ്ഞ് 1 മിനിറ്റ് കാത്തിരിക്കുക.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Input")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Item Name", value=v_in if v_in else "")
        amt = st.number_input("Value (₹)", min_value=0, value=None)
        if st.form_submit_button("EXECUTE SYNC"):
            if item and amt:
                # നിന്റെ ഗൂഗിൾ ഫോം ഐഡികൾ
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("SYNC COMPLETE. PLEASE WAIT FOR CLOUD REFRESH.")
                except: st.error("CONNECTION FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE ---
elif menu == "📊 Intelligence":
    if "is_auth" not in st.session_state: st.session_state["is_auth"] = False
    if not st.session_state["is_auth"]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        pwd = st.text_input("Enter Master Key", type="password")
        if st.button("DECRYPT"):
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
            # ടോട്ടൽ ബോക്സ് ഇവിടെ കാണിക്കും
            st.markdown(f'<div class="total-box">TOTAL: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.6, 
                             color_discrete_sequence=["#BF953F", "#C0C0C0", "#808080", "#E5E4E2"])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.write("Recent Activity Data")
                st.dataframe(df.tail(15), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("ക്ലൗഡിൽ ഡാറ്റയൊന്നും കണ്ടില്ല. ഒന്ന് കൂടി ശ്രമിക്കൂ.")

else:
    st.title(menu)
    st.info("Module loading...")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v5.0 | Deep Dark")
