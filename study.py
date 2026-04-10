import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ ക്ലൗഡ് ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI PRO", layout="wide")

# 2. Deep Dark AI Design
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid #BF953F; }
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(191, 149, 63, 0.3);
        margin-bottom: 20px;
    }
    .total-box {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #BF953F !important;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        border: 2px solid #BF953F;
        box-shadow: 0 0 30px rgba(191, 149, 63, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #BF953F, #AA771C) !important;
        color: black !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
    }
    h1, h2, h3 { color: #FCF6BA !important; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&cb={random.randint(1, 99999)}"
        df = pd.read_csv(url)
        if not df.empty:
            # എപ്പോഴും അവസാനത്തെ കോളം തുകയായി എടുക്കുന്നു
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except: return pd.DataFrame()

# Sidebar Setup
st.sidebar.markdown("<h1 style='text-align: center;'>👾</h1>", unsafe_allow_html=True)
menu = st.sidebar.selectbox("COMMANDS:", ["🏠 Dashboard", "💰 Add Entry", "📊 Intelligence", "💬 WhatsApp Tracking"])

# --- 🏠 DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Welcome Faisal.")
    st.markdown('<div class="glass-card"><h3>AI Core Active 🟢</h3><p>സിസ്റ്റം ഇപ്പോൾ സ്മൂത്ത് ആയി വർക്ക് ചെയ്യുന്നു. പുതിയ ഡിസൈൻ ആസ്വദിക്കൂ!</p></div>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Neural Input")
    v_in = speech_to_text(language='ml', start_prompt="Listening...", key='voice')
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("Entry Name", value=v_in if v_in else "")
        amt = st.number_input("Value (₹)", min_value=0, value=None)
        if st.form_submit_button("EXECUTE SYNC"):
            if item and amt:
                payload = {"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)}
                try:
                    requests.post(FORM_URL_API, data=payload)
                    st.success("SYNC SUCCESSFUL")
                except: st.error("SYNC FAILED")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 INTELLIGENCE (ERROR RESOLVED) ---
elif menu == "📊 Intelligence":
    st.title("📊 Intelligence Report")
    df = load_data()
    if not df.empty:
        total = df['Amount'].sum()
        st.markdown(f'<div class="total-box">TOTAL: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
        
        # ചാർട്ടിലെ എറർ വരാതിരിക്കാൻ കളർ സെറ്റിംഗ്സ് ലളിതമാക്കി
        fig = px.pie(df, values='Amount', names=df.columns[1], hole=0.5, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("ക്ലൗഡിൽ വിവരങ്ങളൊന്നും കണ്ടില്ല.")

# --- 💬 WHATSAPP TRACKING (NEW) ---
elif menu == "💬 WhatsApp Tracking":
    st.title("💬 WhatsApp Logs")
    st.markdown('<div class="glass-card"><h3>WhatsApp Activity</h3><p>നിന്റെ ഗൂഗിൾ ഷീറ്റിൽ "WhatsApp" എന്ന് ടൈപ്പ് ചെയ്ത് നൽകുന്ന എൻട്രികൾ ഇവിടെ കാണാം.</p></div>', unsafe_allow_html=True)
    df = load_data()
    if not df.empty:
        # WhatsApp എന്ന് പേരുള്ള വിവരങ്ങൾ മാത്രം ഫിൽട്ടർ ചെയ്യുന്നു
        wa_data = df[df.iloc[:, 1].str.contains('whatsapp', case=False, na=False)]
        if not wa_data.empty:
            st.dataframe(wa_data, use_container_width=True)
            wa_total = wa_data['Amount'].sum()
            st.info(f"WhatsApp വഴിയുള്ള ആകെ ചിലവ്: ₹ {wa_total}")
        else:
            st.info("WhatsApp വിവരങ്ങളൊന്നും ഇപ്പോൾ ലഭ്യമല്ല. 'Add Entry' ടാബിൽ 'WhatsApp' എന്ന് ചേർത്ത് നോക്കൂ.")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v7.0 | Deep Dark")
