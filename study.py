import streamlit as st
import pandas as pd
import requests
import random
import re
import urllib.parse
import threading
from datetime import datetime
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from streamlit_calendar import calendar
from fpdf import FPDF

# --- CONFIGS & API KEYS ---
TWILIO_SID, TWILIO_TOKEN = "YOUR_TWILIO_ACCOUNT_SID", "YOUR_TWILIO_AUTH_TOKEN"  
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY": genai.configure(api_key=GEMINI_API_KEY)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE, WA_API_KEY = "971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

# --- HELPER FUNCTIONS ---
def send_whatsapp_auto(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except: pass

def get_sheet_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def parse_mixed_dates(date_series):
    parsed = []
    for val in date_series:
        dt = pd.to_datetime(str(val).strip(), errors='coerce')
        if not pd.isna(dt) and dt.year == 2026 and dt.month < 4: dt = datetime(2026, dt.day, dt.month)
        parsed.append(dt if not pd.isna(dt) else pd.to_datetime(str(val).strip(), dayfirst=True, errors='coerce'))
    return pd.Series(parsed)

# --- AI & VOICE LOGIC ---
def scan_bill_with_gemini(uploaded_file):
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY": return None, None, "Others"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Analyze receipt image and extract exactly in this format:\nAmount: [number only]\nDescription: [short text]\nCategory: [Food, Shop, Fish, Travel, Rent, Others]"
        res = model.generate_content([prompt, Image.open(uploaded_file)]).text
        amt = re.search(r"Amount:\s*([\d\.]+)", res)
        desc = re.search(r"Description:\s*(.*)", res)
        cat = re.search(r"Category:\s*(.*)", res)
        return (amt.group(1) if amt else "", desc.group(1).strip() if desc else "Scanned Bill", cat.group(1).strip() if cat else "Others")
    except: return None, None, "Others"

def process_voice(text):
    if not text: return "Others", "", ""
    raw = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw)
    cat = "Food" if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ"]) else "Shop" if any(x in raw for x in ["shop", "കട"]) else "Fish" if "മീൻ" in raw else "Travel" if any(x in raw for x in ["travel", "യാത്ര"]) else "Others"
    return cat, nums[0] if nums else "", re.sub(r'\d+', '', raw).strip()

# --- STREAMLIT UI ---
st.set_page_config(page_title="PAICHI EXPENSES v2.6", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""

st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1A0521, #4B0082, #0D0214); color: #fff; }
    .balance-banner { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 20px; }
    .purple-box { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 20px; border: 2px solid rgba(255,215,0,0.3); text-align: center; margin-bottom: 15px; }
    .category-box { background: rgba(255,255,255,0.08); padding: 12px; border-radius: 12px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 10px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    .stDataFrame { background: white; color: black; border-radius: 10px; }
</style>""", unsafe_allow_html=True)

if not st.session_state.auth:
    st.title("🔐 PAICHI EXPENSES LOGIN")
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    df_main = get_sheet_data()
    
    t_in = df_main['Credit'].sum() if not df_main.empty else 0.0
    t_out = df_main['Debit'].sum() if not df_main.empty else 0.0
    balance = t_in - t_out
    
    st.markdown(f'<div class="balance-banner"><span style="size:18px;color:#E0B0FF;">Available Balance</span><br><span style="font-size:38px;color:#FFD700;">₹{balance:,.2f}</span></div>', unsafe_allow_html=True)
    
    menu = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker"] if curr_user == "shabana" else ["🏠 Dashboard", "💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
        
        if not df_main.empty:
            def get_cat(x):
                x = str(x)
                return x.split(':')[0].replace(']', '').strip().capitalize() if ':' in x else "Others"
            df_main['Cat'] = df_main['Item'].apply(get_cat)
            cats = df_main.groupby('Cat')['Debit'].sum().to_dict()
            cols = st.columns(3)
            for idx, (c_n, c_a) in enumerate(cats.items()):
                if c_a > 0:
                    with cols[idx % 3]: st.markdown(f'<div class="category-box"><span style="color:#aaa;">{c_n}</span><br><span>₹{c_a:,.2f}</span></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Add New Transaction 💰")
        t1, t2 = st.tabs(["🎙️ Voice Entry", "🧾 AI Bill Scanner"])
        init_amt, init_desc, init_cat = "", "", "Others"
        
        with t1:
            v_raw = speech_to_text(language='ml', key='v_8')
            if v_raw: init_cat, init_amt, init_desc = process_voice(v_raw)
        with t2:
            up_file = st.file_uploader("Upload Bill", type=["jpg", "jpeg", "png"])
            if up_file and st.button("✨ SCAN WITH AI"):
                with st.spinner("AI Reading..."):
                    init_amt, init_desc, init_cat = scan_bill_with_gemini(up_file)
                    st.success("Scanned! ✅")

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=init_desc)
            am_str = st.text_input("Amount", value=str(init_amt))
            cats = ["Food", "Shop", "Fish", "Travel", "Rent", "Others"]
            cat = st.selectbox("Category", cats, index=cats.index(init_cat) if init_cat in cats else 5)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", "entry.1460982454": am if ty=="Debit" else 0, "entry.1221658767": 0 if ty=="Debit" else am}
                    requests.post(FORM_API, data=payload, timeout=10)
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}")
                    st.success("Saved! ✅")
                    st.rerun()
                except: st.error("Invalid Amount!")

    elif page == "📅 Calendar":
        st.title("📊 P&L Calendar View")
        if not df_main.empty:
            df_main['Date'] = parse_mixed_dates(df_main['Date'])
            df_c = df_main.dropna(subset=['Date'])
            day_sum = df_c.groupby(df_c['Date'].dt.strftime('%Y-%m-%d')).agg({'Debit':'sum', 'Credit':'sum'}).reset_index()
            
            events = []
            for _, r in day_sum.iterrows():
                if r['Credit'] > 0: events.append({"title": f" +₹{r['Credit']:,.0f}", "start": r['Date'], "backgroundColor": "#198754", "textColor": "white"})
                if r['Debit'] > 0: events.append({"title": f" -₹{r['Debit']:,.0f}", "start": r['Date'], "backgroundColor": "#dc3545", "textColor": "white"})
            
            cal_data = calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}}, key="pnl_cal")
            if cal_data.get("eventClick"):
                c_date = cal_data["eventClick"]["event"]["start"].split("T")[0]
                st.subheader(f"📋 Details for {c_date}")
                day_df = df_c[df_c['Date'].dt.strftime('%Y-%m-%d') == c_date].copy()
                if not day_df.empty:
                    day_df['Date'] = day_df['Date'].dt.strftime('%d/%m/%Y')
                    st.download_button("📥 Download Day Data", day_df[['Date','Item','Debit','Credit']].to_csv(index=False), f"Trans_{c_date}.csv", "text/csv")
                    st.toast("📥 ഫയൽ റെഡിയാണ്!", icon="✅")
                    st.dataframe(day_df[['Date','Item','Debit','Credit']], use_container_width=True)

    elif page in ["📊 Report", "🔍 History"]:
        if not df_main.empty:
            df_main['Date'] = parse_mixed_dates(df_main['Date'])
            df_f = df_main[(df_main['Date'].dt.year == 2026) & (df_main['Date'].dt.month >= 4)].copy()
            df_f['Month'] = df_f['Date'].dt.strftime('%B %Y')
            months = df_f.sort_values(by='Date', ascending=False)['Month'].dropna().unique()
            
            if len(months) == 0: st.warning("No data found from April 2026 onwards!")
            else:
                m_sel = st.selectbox("Select Month", months, key="m_sel")
                m_df = df_f[df_f['Month'] == m_sel].copy()
                
                if page == "📊 Report":
                    st.title("Monthly Expense Analysis")
                    dr, cr = m_df['Debit'].sum(), m_df['Credit'].sum()
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f'<div class="purple-box"><h4 style="color:#00FF00;">Credit</h4><h3>₹{cr:,.2f}</h3></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="purple-box"><h4 style="color:#FF3131;">Expense</h4><h3>₹{dr:,.2f}</h3></div>', unsafe_allow_html=True)
                    c3.markdown(f'<div class="purple-box"><h4 style="color:#FFD700;">Savings</h4><h3>₹{cr-dr:,.2f}</h3></div>', unsafe_allow_html=True)
                    
                    if dr > 0:
                        m_df['Cat'] = m_df['Item'].apply(lambda x: str(x).split(':')[0] if ':' in x else 'Others')
                        st.plotly_chart(px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Cat', hole=0.4), use_container_width=True)
                    
                    st.download_button("📥 Download CSV Report", m_df.drop(columns=['Month']).to_csv(index=False), f"Report_{m_sel}.csv", "text/csv")
                    st.toast("📥 റിപ്പോർട്ട് റെഡിയാണ്!", icon="📊")
                else:
                    st.title("Transaction History")
                    st.download_button("📥 Download CSV History", m_df.drop(columns=['Month']).to_csv(index=False), f"History_{m_sel}.csv", "text/csv")
                    st.toast("📥 CSV ഫയൽ റെഡിയാണ്!", icon="✅")
                
                m_df['Date'] = m_df['Date'].dt.strftime('%d/%m/%Y')
                st.dataframe(m_df.drop(columns=['Month']).iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_form"):
            n, a, t = st.text_input("Name"), st.number_input("Amount", min_value=0.0), st.selectbox("Category", ["vagiyade", "koduthade"])
            if st.form_submit_button("SAVE"):
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t} - {n}", "entry.1460982454": 0 if "vagiyade" in t else a, "entry.1221658767": a if "vagiyade" in t else 0}
                requests.post(FORM_API, data=payload, timeout=10)
                st.success("Saved! ✅")
