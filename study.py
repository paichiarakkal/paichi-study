# ============================================
# PAICHI EXPENSES v5.0 - Ultimate AI Agent
# ============================================

import streamlit as st
import pandas as pd
import requests
import random
import re
import urllib.parse
import threading
from datetime import datetime
from io import BytesIO
import json

import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from streamlit_calendar import calendar
from fpdf import FPDF
from groq import Groq # AI-ക്ക് വേണ്ടി

# --- CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"

# Secrets
WA_PHONE = st.secrets.get("WA_PHONE", "")
WA_API_KEY = st.secrets.get("WA_API_KEY", "")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
USER_PINS = {
    "faisal": st.secrets.get("PIN_FAISAL", ""),
    "shabana": st.secrets.get("PIN_SHABANA", ""),
    "admin": st.secrets.get("PIN_ADMIN", "")
}

# --- PAGE SETUP & CSS ---
st.set_page_config(page_title="PAICHI AI Agent", layout="wide")
if st.session_state.get("page") == "🏠 Dashboard":
    st_autorefresh(interval=60000, key="auto_refresh")

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0,0,0,0.70), rgba(0,0,0,0.70)), url("{BG_IMAGE_URL}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.85) !important; }}
    .balance-banner {{ background: rgba(0,0,0,0.65); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 25px; }}
    .purple-box {{ background: rgba(0,0,0,0.65); padding: 20px; border-radius: 25px; border: 2px solid rgba(255,215,0,0.3); text-align: center; margin-bottom: 20px; }}
    .category-box {{ background: rgba(0,0,0,0.65); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }}
    .alert-banner {{ background-color: #ff4d4d; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }}
    .login-card {{ background: rgba(0,0,0,0.7); padding: 25px; border-radius: 20px; border: 1px solid #FFD700; max-width: 450px; margin: auto; margin-top: 30px; }}
    h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
    .stDataFrame {{ background: white; border-radius: 10px; color: black; }}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INIT ---
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = ""
if "custom_alert_text" not in st.session_state:
    st.session_state.custom_alert_text = "Shop kuri book"
if "low_limit" not in st.session_state:
    st.session_state.low_limit = 6000

# ============================================
# 🤖 AI AGENT TOOLS & FUNCTIONS
# ============================================
# 1. AI-ക്ക് നൽകാൻ പോകുന്ന ടൂളുകൾ ഡിഫൈൻ ചെയ്യുന്നു
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_new_entry",
            "description": "ഒരു പുതിയ ചെലവോ (Debit) വരുമാനമോ (Credit) Google Sheet-ൽ ചേർക്കുക.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "ചെലവിന്റെ പേര് (ഉദാ: Biriyani, Petrol)"},
                    "amount": {"type": "number", "description": "തുക (ഉദാ: 150, 5000)"},
                    "type": {"type": "string", "enum": ["Debit", "Credit"], "description": "ചെലവാണെങ്കിൽ Debit, വരുമാനമാണെങ്കിൽ Credit"}
                },
                "required": ["item", "amount", "type"]
            }
        }
    }
]

# 2. ടൂൾ പ്രവർത്തിപ്പിക്കാനുള്ള യഥാർത്ഥ ഫംഗ്ഷൻ
def execute_add_entry(item, amount, entry_type):
    try:
        payload = {
            "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
            "entry.2013476337": f"[{st.session_state.user.capitalize()}] Others: {item}",
            "entry.1460982454": amount if entry_type == "Debit" else 0,
            "entry.1221658767": 0 if entry_type == "Debit" else amount,
        }
        requests.post(FORM_API, data=payload, timeout=10)
        
        wa_msg = f"✅ *AI Agent Entry*\n📝 Item: {item}\n💰 Amt: {amount}\n👤 User: {st.session_state.user}"
        send_whatsapp_auto(wa_msg)
        st.cache_data.clear()
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"

# --- HELPERS ---
def send_whatsapp_auto(msg):
    if not (WA_PHONE and WA_API_KEY): return
    def _send():
        try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
        except: pass
    threading.Thread(target=_send, daemon=True).start()

def parse_mixed_dates(date_series):
    return pd.Series([pd.to_datetime(str(val).strip(), dayfirst=True, errors="coerce") for val in date_series])

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1, 999)}")
        df.columns = df.columns.str.strip()
        df["Date"] = parse_mixed_dates(df["Date"])
        df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce").fillna(0)
        df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Data load error: {e}")
        return pd.DataFrame()

def create_pdf(df):
    try:
        pdf = FPDF(); pdf.add_page()
        pdf.set_font("Arial", "B", 14); pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align="C"); pdf.ln(10)
        widths = {"Date": 30, "Item": 85, "Debit": 35, "Credit": 35}
        pdf.set_font("Arial", "B", 10)
        for col in widths: pdf.cell(widths[col], 10, txt=col, border=1, align="C")
        pdf.ln(); pdf.set_font("Arial", "", 9)
        for _, row in df.iterrows():
            if pdf.get_y() > 260: pdf.add_page()
            y_start = pdf.get_y(); pdf.cell(30, 10, txt=str(row["Date"]), border=0); x_after_date = pdf.get_x()
            item_text = str(row["Item"]).encode("ascii", "ignore").decode("ascii")
            pdf.multi_cell(85, 5, txt=item_text, border=0); h = max(10, pdf.get_y() - y_start)
            pdf.set_xy(x_after_date + 85, y_start); pdf.cell(35, h, txt=str(row["Debit"]), border=0, align="R"); pdf.cell(35, h, txt=str(row["Credit"]), border=0, align="R")
            pdf.set_xy(10, y_start)
            for w in widths.values(): pdf.cell(w, h, txt="", border=1)
            pdf.set_y(y_start + h)
        return BytesIO(bytes(pdf.output()))
    except: return None

def extract_cat(x):
    item_text = str(x).lower()
    rules = {"Food": ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ", "ബിരിയാണി", "mess"], "Shop": ["shop", "കട", "സാധനങ്ങൾ"], "Fish": ["fish", "മീൻ", "ഇറച്ചി", "ചിക്കൻ"], "Travel": ["travel", "യാത്ര", "പെട്രോൾ"], "Rent": ["rent", "വാടക", "റൂം"]}
    for cat, keywords in rules.items():
        if any(w in item_text for w in keywords): return cat
    return "Others"

# ============================================
# LOGIN
# ============================================
if not st.session_state.auth:
    st.markdown('<div class="login-card"><div class="login-title" style="text-align:center; color:#FFD700; font-size:22px; font-weight:bold; margin-bottom:15px;">🔐 PAICHI AI AGENT</div>', unsafe_allow_html=True)
    u = st.selectbox("👤 Select User", ["faisal", "shabana", "admin"]).lower()
    pin = st.text_input("🔑 Enter 4-Digit PIN", type="password", max_chars=4)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("UNLOCK APP 🔓"):
        if USER_PINS.get(u) and USER_PINS.get(u) == pin:
            st.session_state.auth = True; st.session_state.user = u; st.rerun()
        else: st.error("❌ Incorrect PIN!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================
# MAIN APP
# ============================================
df = load_data()
t_in = df["Credit"].sum() if not df.empty else 0.0
t_out = df["Debit"].sum() if not df.empty else 0.0
bal = t_in - t_out

if st.session_state.user != "shabana":
    with st.sidebar.expander("⚙️ Settings"):
        st.session_state.custom_alert_text = st.text_area("Custom Alert", value=st.session_state.custom_alert_text)
        st.session_state.low_limit = st.number_input("Low Balance Limit", value=st.session_state.low_limit)

if bal < st.session_state.low_limit:
    st.markdown(f'<div class="alert-banner">⚠️ ബാലൻസ് കുറവാണ് ({st.session_state.custom_alert_text})</div>', unsafe_allow_html=True)

st.markdown(f'<div class="balance-banner"><span style="font-size:20px; color:#E0B0FF;">Available Balance</span><br><span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)

menu = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History"]
if st.session_state.user != "shabana": menu.insert(0, "🏠 Dashboard")
page = st.sidebar.radio("Menu", menu)
st.session_state.page = page
if st.sidebar.button("Logout"):
    st.session_state.clear(); st.rerun()

# --- PAGES ---
if page == "🏠 Dashboard" and not df.empty:
    st.title("Financial Overview")
    st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00;">Total Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Total Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
    st.subheader("🗂️ Categories")
    df_dash = df.copy(); df_dash["Cat"] = df_dash["Item"].apply(extract_cat)
    cats = df_dash[~df_dash["Item"].str.contains("total", case=False, na=False)].groupby("Cat")["Debit"].sum().to_dict()
    cols = st.columns(3); idx = 0
    for c_name, c_amt in cats.items():
        if c_amt > 0:
            with cols[idx % 3]: st.markdown(f'<div class="category-box"><span style="color:#aaa;">Total {c_name}</span><br><span style="font-size:24px; color:#FFF;">₹{c_amt:,.2f}</span></div>', unsafe_allow_html=True)
            idx += 1

elif page == "💰 Add Entry":
    st.title("Smart Voice Entry 🎙️")
    v_raw = speech_to_text(language="ml", key="voice_v9")
    if v_raw: st.session_state["voice_data"] = v_raw
    v_raw = st.session_state.get("voice_data", "")
    v_desc, v_amt = "", ""
    if v_raw:
        raw = v_raw.lower().replace(".", "").replace(",", ""); nums = re.findall(r"\d+", raw)
        v_amt = nums[0] if nums else ""; v_desc = re.sub(r"\d+", "", raw).strip()

    with st.form("entry_form", clear_on_submit=True):
        it = st.text_input("Description", value=v_desc); am_str = st.text_input("Amount", value=str(v_amt))
        cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
        ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        if st.form_submit_button("SAVE"):
            try:
                am = float(am_str.strip().replace(",", ""))
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.capitalize()}] {cat}: {it}", "entry.1460982454": am if ty=="Debit" else 0, "entry.1221658767": 0 if ty=="Debit" else am}
                threading.Thread(target=lambda: requests.post(FORM_API, data=payload, timeout=10)).start()
                send_whatsapp_auto(f"✅ Entry: {it} ₹{am}")
                st.session_state["voice_data"] = ""; st.session_state["flash"] = "Saved! ✅"; st.cache_data.clear(); st.rerun()
            except: st.error("Valid amount required!")

elif page == "📅 Calendar" and not df.empty:
    st.title("P&L Calendar 📅")
    df_cal = df.dropna(subset=["Date"])
    if not df_cal.empty:
        summary = df_cal.groupby(df_cal["Date"].dt.strftime("%Y-%m-%d")).agg({"Debit": "sum", "Credit": "sum"}).reset_index()
        events = []
        for _, row in summary.iterrows():
            if row["Credit"] > 0: events.append({"title": f" +₹{row['Credit']:,.0f}", "start": row["Date"], "backgroundColor": "#198754"})
            if row["Debit"] > 0: events.append({"title": f" -₹{row['Debit']:,.0f}", "start": row["Date"], "backgroundColor": "#dc3545"})
        calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth"}, key="pnl_cal")

elif page in ("📊 Report", "🔍 History"):
    if df.empty: st.warning("No data available!")
    else:
        df_rep = df[(df["Date"].dt.year == 2026) & (df["Date"].dt.month >= 4)].copy()
        df_rep["Month"] = df_rep["Date"].dt.strftime("%B %Y")
        months = df_rep.dropna(subset=["Month"]).sort_values("Date", ascending=False)["Month"].unique()
        if len(months) > 0:
            sel_m = st.selectbox("Select Month", months)
            m_df = df_rep[df_rep["Month"] == sel_m]
            st.dataframe(m_df[['Date', 'Item', 'Debit', 'Credit']], use_container_width=True)

if "flash" in st.session_state:
    st.success(st.session_state.flash); del st.session_state.flash

# ============================================
# 🚀 AI AGENT & ASSISTANT (Sidebar)
# ============================================
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Agent & Assistant")

if not GROQ_API_KEY:
    st.sidebar.error("Groq API Key ലഭ്യമല്ല!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.sidebar.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.sidebar.chat_input("Ask or tell me to add an expense..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.sidebar.chat_message("user"):
        st.markdown(prompt)

    with st.sidebar.spinner("AI ആലോചിക്കുന്നു..."):
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            # സ്വന്തം കോഡ് വായിക്കാൻ ശ്രമിക്കുന്നു
            try:
                with open("app.py", "r", encoding="utf-8") as f: my_code = f.read()
            except: my_code = "Code not available."

            df_summary = df[['Date', 'Item', 'Debit', 'Credit']].tail(20).to_string() if not df.empty else "No data"
            
            system_instruction = f"""
            നീ ഒരു സ്മാർട്ട് ഫിനാൻസ് AI ഏജന്റും, സഹായിയുമാണ്. 
            നിലവിലെ ബാലൻസ്: {bal} Rs.
            Data: {df_summary}
            
            നിനക്ക് പൊതുവായ അറിവുള്ള ചോദ്യങ്ങൾക്കും മലയാളത്തിൽ വിശദമായി മറുപടി നൽകാം.
            യൂസർ എന്തെങ്കിലും ചെലവ് ചേർക്കാൻ പറഞ്ഞാൽ (ഉദാ: 'ബിരിയാണി 150'), നീ നിർബന്ധമായും add_new_entry എന്ന ടൂൾ ഉപയോഗിക്കണം.
            
            ഇതാ നിന്റെ സ്വന്തം സോഴ്സ് കോഡ് (app.py):
            ```python
            {my_code[:5000]} # കോഡ് വളരെ വലുതാണെങ്കിൽ ആദ്യത്തെ 5000 അക്ഷരങ്ങൾ മാത്രം
            ```
            യൂസർ കോഡിനെക്കുറിച്ച് ചോദിച്ചാൽ ഈ കോഡ് വായിച്ച് മറുപടി നൽകുക.
            """
            
            messages_for_api = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]

            response = client.chat.completions.create(
                model="llama3-70b-8192", # Groq-ൽ ടൂൾസ് വർക്ക് ചെയ്യുന്ന മികച്ച മോഡൽ
                messages=messages_for_api,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            
            # AI ടൂൾ ഉപയോഗിക്കാൻ തീരുമാനിച്ചാൽ
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "add_new_entry":
                        args = json.loads(tool_call.function.arguments)
                        result = execute_add_entry(args["item"], args["amount"], args["type"])
                        if result == "Success":
                            ai_reply = f"✅ ചേട്ടാ, {args['item']}-ന് വേണ്ടി {args['amount']} Rs ഞാൻ ഷീറ്റിൽ എൻട്രി ഇട്ടിട്ടുണ്ട്! (Action Completed)"
                        else: ai_reply = f"❌ എൻട്രി ഇടാൻ പറ്റിയില്ല: {result}"
            else:
                # സാധാരണ ചോദ്യങ്ങൾക്കുള്ള മറുപടി
                ai_reply = response_message.content

            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            with st.sidebar.chat_message("assistant"):
                st.markdown(ai_reply)
                
            if response_message.tool_calls and result == "Success":
                st.rerun()

        except Exception as e:
            st.sidebar.error(f"AI Error: {str(e)}")