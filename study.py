import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# 1. നിന്റെ പുതിയ ലിങ്കുകൾ (CSV & API)
# ഷീറ്റ് ലിങ്ക്
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
# ഫോം API ലിങ്ക്
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI Family Hub", layout="wide")

# 2. ഡിസൈൻ സെറ്റിംഗ്സ് (Silver & Gold)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #C0C0C0, #E8E8E8, #A9A9A9) !important; }
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #000; color: #FFD700; padding: 10px 0; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .total-box { background-color: #000; color: #FFD700; padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; border: 4px solid #FFD700; }
    h1, h2, h3, label, p { color: black !important; font-weight: bold !important; }
    .stButton>button { background-color: #000 !important; color: #FFD700 !important; font-weight: bold; width: 100%; border: 2px solid #FFD700; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 പൈച്ചി ഫാമിലി ഹബ്ബ് ലൈവ് ട്രാക്കർ | വോയ്‌സ് വഴിയോ നേരിട്ടോ വിവരങ്ങൾ സുരക്ഷിതമായി ചേർക്കാം 📢</div></div>', unsafe_allow_html=True)

def load_data():
    try:
        url = f"{CSV_URL}&x={random.randint(1, 1000)}"
        df = pd.read_csv(url)
        if not df.empty:
            df['Amount'] = pd.to_numeric(df.iloc[:, -1], errors='coerce').fillna(0)
            return df
    except:
        return pd.DataFrame()

# 3. സൈഡ്‌ബാർ മെനു (നീ ചോദിച്ച എല്ലാ സെക്ഷനും ഇതിലുണ്ട്)
st.sidebar.title("⚪ PAICHI MENU")
menu = st.sidebar.selectbox("തിരഞ്ഞെടുക്കുക:", 
    ["🏠 Home", "💰 Expenses (Add Entry)", "📊 Smart Analytics", "🎓 SSLC Marks", "🎓 Plus Two Marks", "⏰ Reminders"])

# --- 🏠 HOME ---
if menu == "🏠 Home":
    st.title("🏠 Welcome Faisal!")
    st.write("പൈച്ചി ഫാമിലി ഹബ്ബിലേക്ക് സ്വാഗതം. ഡാറ്റ ചേർക്കാൻ Expenses പേജിൽ പോകുക.")

# --- 💰 EXPENSES (ക്ലീൻ എന്റർ പേജ് - ഇവിടെ ഷീറ്റോ ഫോമോ കാണില്ല) ---
elif menu == "💰 Expenses (Add Entry)":
    st.title("💵 Add New Entry")
    st.write("🎤 മൈക്കിൽ ക്ലിക്ക് ചെയ്ത് സംസാരിക്കൂ (അല്ലെങ്കിൽ താഴെ ടൈപ്പ് ചെയ്യുക):")
    
    # വോയ്‌സ് ഇൻപുട്ട്
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    
    st.markdown('<br>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background-color: rgba(255,255,255,0.2); padding: 30px; border-radius: 20px; border: 2px solid #000;">', unsafe_allow_html=True)
        with st.form("quick_add_form", clear_on_submit=True):
            item = st.text_input("സാധനത്തിന്റെ പേര് (Item Name)", value=v_in if v_in else "")
            amt = st.number_input("തുക (Amount)", min_value=0, value=None, placeholder="0")
            
            if st.form_submit_button("SAVE TO CLOUD"):
                if item and amt:
                    # നിന്റെ പുതിയ ഗൂഗിൾ ഫോം എൻട്രി ഐഡികൾ
                    payload = {
                        "entry.1069832729": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.1896057694": item, 
                        "entry.1570426033": str(amt)
                    }
                    try:
                        requests.post(FORM_URL_API, data=payload)
                        st.success(f"വിജയകരമായി സേവ് ചെയ്തു: {item}")
                    except:
                        st.error("ലിങ്ക് ശരിയല്ല, ഒന്ന് പരിശോധിക്കൂ!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 📊 SMART ANALYTICS (പാസ്‌വേഡ് അടിച്ചാൽ മാത്രം കണക്കുകൾ കാണാം) ---
elif menu == "📊 Smart Analytics":
    if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
    
    if not st.session_state["unlocked"]:
        st.title("🔐 Secure Section")
        pwd = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
        if st.button("UNLOCK"):
            if pwd == "1234":
                st.session_state["unlocked"] = True
                st.rerun()
            else: st.error("തെറ്റായ പാസ്‌വേഡ്!")
    else:
        st.title("📊 Financial Report")
        if st.sidebar.button("🔒 Lock"):
            st.session_state["unlocked"] = False
            st.rerun()
            
        df = load_data()
        if not df.empty:
            total = df['Amount'].sum()
            st.markdown(f'<div class="total-box">ഈ മാസത്തെ ആകെ ചിലവ്: ₹ {total:,.2f}</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("ചിലവ് വിശകലനം")
                fig = px.pie(df, values='Amount', names=df.columns[1] if len(df.columns) > 1 else None)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("കഴിഞ്ഞ 10 ചിലവുകൾ")
                st.table(df.tail(10))
        else:
            st.info("ഡാറ്റയൊന്നുമില്ല.")

# --- 🎓 SSLC & PLUS TWO MARKS ---
elif menu in ["🎓 SSLC Marks", "🎓 Plus Two Marks"]:
    st.title(menu)
    st.info("ഈ സെക്ഷനിൽ നിന്റെ മാർക്ക് ലിസ്റ്റുകൾ ഉടൻ അപ്‌ഡേറ്റ് ചെയ്യും.")

# --- ⏰ REMINDERS ---
elif menu == "⏰ Reminders":
    st.title("⏰ Reminders")
    st.warning("⚡ കറന്റ് ബില്ല് അടയ്ക്കാൻ സമയമായോ എന്ന് പരിശോധിക്കുക!")

st.sidebar.write("---")
st.sidebar.write("Design by Faisal | PAICHI AI")
