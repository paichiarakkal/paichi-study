import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from streamlit_mic_recorder import speech_to_text

# 1. ലിങ്കുകൾ
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2UqKgCAEEv42IC6vwe0D2g_pW7-XR2Qiv7_FwAZYFDTDLd7pOwKQ5yvClbwy88AZmD6Ar2AiFQ8Xu/pub?output=csv"
FORM_URL_API = "https://docs.google.com/forms/d/e/1FAIpQLScHkSw0nkgNQSeRGocM85t4bZCkWHQS6EUSDf-5dIts1gWZXw/formResponse"

st.set_page_config(page_title="PAICHI AI PRO", layout="wide", initial_sidebar_state="collapsed")

# --- 🌗 UI DESIGN (MOBILE OPTIMIZED) ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%); }
    
    /* 📱 വരിവരിയായി ഐക്കണുകൾ വരാൻ */
    [data-testid="column"] {
        width: 33.33% !important;
        flex: 1 1 33.33% !important;
        min-width: 30% !important;
    }

    .stButton > button {
        background: white !important;
        color: #eab308 !important;
        border: 2px solid #eab308 !important;
        border-radius: 50% !important; 
        height: 70px !important;
        width: 70px !important;
        margin: 5px auto !important;
        font-size: 24px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .total-box { 
        background: linear-gradient(135deg, #facc15 0%, #eab308 100%); 
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 വോയ്‌സ് ക്ലീനിംഗ് ഫങ്ക്ഷൻ ---
def clean_voice_input(text):
    # മലയാളം അക്കങ്ങളെ ഇംഗ്ലീഷ് നമ്പറുകളാക്കുന്നു
    num_map = {'ഒന്ന്': '1', 'രണ്ട്': '2', 'മൂന്ന്': '3', 'നാല്': '4', 'അഞ്ച്': '5', 
               'ആറ്': '6', 'ഏഴ്': '7', 'എട്ട്': '8', 'ഒൻപത്': '9', 'പത്ത്': '10', 'ഇരുപത്': '20', 'അമ്പത്': '50', 'നൂറ്': '100'}
    
    words = text.split()
    item_parts = []
    final_amt = None
    
    for word in words:
        if word.isdigit():
            final_amt = int(word)
        elif word in num_map:
            final_amt = int(num_map[word])
        else:
            item_parts.append(word)
            
    return " ".join(item_parts), final_amt

if 'page' not in st.session_state: st.session_state.page = "🏠 HOME"
def nav(p):
    st.session_state.page = p
    st.rerun()

# --- 🏠 HOME SCREEN ---
if st.session_state.page == "🏠 HOME":
    st.markdown("<h2 style='text-align: center; color: #0f172a;'>PAICHI AI</h2>", unsafe_allow_html=True)
    
    # മൊത്തം തുക കാണിക്കാൻ
    try:
        df = pd.read_csv(f"{CSV_URL}&ref={random.randint(1,999)}")
        total = pd.to_numeric(df.iloc[:, -1], errors='coerce').sum()
    except: total = 0
    st.markdown(f'<div class="total-box"><h2 style="margin:0;">₹ {total:,.2f}</h2></div>', unsafe_allow_html=True)

    # ഐക്കൺ ഗ്രിഡ്
    c1, c2, c3 = st.columns(3)
    with c1: st.button("💰", on_click=nav, args=("ADD",))
    with c2: st.button("📊", on_click=nav, args=("DATA",))
    with c3: st.button("🔴", on_click=nav, args=("DEBT",))
    
    st.write("")
    
    c4, c5, c6 = st.columns(3)
    with c4: st.button("✅", on_click=nav, args=("TODO",))
    with c5: st.button("💬", on_click=nav, args=("LOGS",))
    with c6: st.button("🔄", on_click=st.rerun)

# --- 💰 ADD ENTRY PAGE ---
elif st.session_state.page == "ADD":
    if st.button("🔙"): nav("🏠 HOME")
    st.markdown("### 📥 Smart Input")
    
    v_in = speech_to_text(language='ml', start_prompt="സംസാരിക്കൂ... (ഉദാ: ചായ 10)", key='voice')
    
    auto_item, auto_amt = "", None
    if v_in:
        auto_item, auto_amt = clean_voice_input(v_in)
    
    with st.form("input_form", clear_on_submit=True):
        item = st.text_input("ഐറ്റം പേര്", value=auto_item)
        amt = st.number_input("തുക (₹)", min_value=0, value=auto_amt if auto_amt else 0)
        if st.form_submit_button("SAVE TO CLOUD"):
            if item and amt:
                requests.post(FORM_URL_API, data={"entry.1069832729": datetime.now().strftime("%Y-%m-%d"), "entry.1896057694": item, "entry.1570426033": str(amt)})
                st.success("Synced! ✅")

# ബാക്കി പേജുകൾ (DATA, DEBT, etc.) ചുരുക്കത്തിൽ
else:
    if st.button("🔙 BACK"): nav("🏠 HOME")
    st.write(f"{st.session_state.page} Page Under Construction")
