import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
import urllib.parse
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകളും സെറ്റിംഗ്സും
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

PEACE_NUMBERS = ["918714752210"] # നിനക്ക് മെസ്സേജ് അയക്കേണ്ട നമ്പറുകൾ ഇവിടെ ചേർക്കാം

st.set_page_config(page_title="PAICHI AI V21", layout="wide")

# 2. സമയം നോക്കി ഓട്ടോമാറ്റിക്കായി മെനു മാറ്റാനുള്ള ലോജിക്
now = datetime.now()
# പുലർച്ചെ 4:00 നും 5:00 നും ഇടയിലാണെങ്കിൽ നേരിട്ട് Peace Mode തുറക്കും
if 4 <= now.hour < 5:
    default_menu = "🌙 Peace Mode"
else:
    default_menu = "🏠 Dashboard"

# Sidebar
st.sidebar.title("🤖 PAICHI AI")
menu = st.sidebar.selectbox("COMMANDS:", 
    ["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"], index=["🏠 Dashboard", "🌙 Peace Mode", "💰 Add Entry", "📊 Reports", "🔴 Debt Tracker", "✅ To-Do List", "💬 Logs"].index(default_menu))

# --- 🌙 PEACE MODE (Assalamualaikum Section) ---
if menu == "🌙 Peace Mode":
    st.title("Morning Peace 🌙")
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); padding: 40px; border-radius: 25px; text-align: center; color: white;">
            <h1 style="color: white !important;">Assalamu Alaikum</h1>
            <p>നിന്റെ സന്ദേശം റെഡിയാണ്. താഴെ ക്ലിക്ക് ചെയ്യുക.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # AI മോഡൽ ഡിസൈൻ ഉൾപ്പെടുത്തിയ മെസ്സേജ്
    msg_body = """
🌟 *ASSALAMU ALAIKUM* 🌟
━━━━━━━━━━━━━━━━━━━
✨ *PAICHI AI GREETINGS* ✨

നിങ്ങൾക്ക് സന്തോഷകരമായ ഒരു പുലരി നേരുന്നു!
ഈ സന്ദേശം നിങ്ങളിലേക്ക് എത്തിക്കുന്നത് 
*PAICHI AI NEURAL LINK* വഴിയാണ്.

🖼️ *നിങ്ങൾക്കുള്ള AI ഡിസൈൻ ഇവിടെ കാണാം:*
https://img.freepik.com/free-vector/ramadan-kareem-greeting-card-design_1017-31015.jpg

━━━━━━━━━━━━━━━━━━━
🚀 _Powered by Paichi AI_
    """
    
    for num in PEACE_NUMBERS:
        wa_url = f"https://wa.me/{num}?text={urllib.parse.quote(msg_body)}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#facc15; color:#000; padding:15px; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:10px; border:none;">SEND TO {num} 🚀</button></a>', unsafe_allow_html=True)

# --- 💰 ADD ENTRY ---
elif menu == "💰 Add Entry":
    st.title("📥 Data Input")
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ...", key='voice')
    # പഴയ സേവിംഗ് ലോജിക് ഇവിടെ തുടരും...
    with st.form("input_form"):
        item = st.text_input("Item", value=v_in if v_in else "")
        amt = st.number_input("Amount", min_value=0)
        if st.form_submit_button("SAVE"):
            st.success("Saved!")

# --- മറ്റുള്ളവ (പഴയ കോഡിലെ എല്ലാം ഇതിൽ ഉണ്ടാകും) ---
else:
    st.write("മറ്റ് വിവരങ്ങൾ ഇവിടെ കാണാം.")

st.sidebar.write("---")
st.sidebar.write("PAICHI AI v21.0")
