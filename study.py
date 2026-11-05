import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import re
import json
from groq import Groq
from streamlit_calendar import calendar
from twilio.rest import Client

# --- 1. CONFIG & SETTINGS ---
EXPENSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

# നിങ്ങളുടെ ബിസിനസ്സ് ആപ്പിന്റെ ലിങ്കുകൾ (ഇവിടെ മാറ്റികൊള്ളൂ)
STOCK_CSV_URL = "YOUR_STOCK_SHEET_CSV_LINK" 
STOCK_FORM_API = "YOUR_STOCK_FORM_API"

WA_PHONE = "971551347989"
USER_PINS = {
    "faisal": st.secrets.get("PIN_FAISAL", ""),
    "shabana": st.secrets.get("PIN_SHABANA", ""),
    "admin": st.secrets.get("PIN_ADMIN", "")
}
BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"

# --- 2. UI SETUP & CSS ---
st.set_page_config(page_title="PAICHI SUPER APP", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-color: #0E1117 !important; background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("{BG_IMAGE_URL}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background: rgba(0, 0, 0, 0.9) !important; }}
    .stButton>button {{ background-color: #FFD700 !important; color: #000 !important; border-radius: 10px; font-weight: bold; width: 100%; }}
    .balance-banner {{ background: rgba(0, 0, 0, 0.7); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 25px; }}
    .purple-box {{ background: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 25px; border: 2px solid rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }}
    .category-box {{ background: rgba(0, 0, 0, 0.7); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }}
    .alert-banner {{ background-color: #ff4d4d; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }}
    h1, h2, h3, p, label, span {{ color: white !important; font-weight: bold !important; }}
    div[data-baseweb="select"] > div, [data-testid="stTextInput"] input {{ background-color: #262730 !important; color: white !important; -webkit-text-fill-color: white !important; border: 1px solid #555 !important; }}
    [data-testid="stChatMessage"] {{ background-color: #202c33 !important; border-radius: 12px !important; padding: 12px 16px !important; }}
    [data-testid="stChatInput"] textarea {{ color: white !important; }}
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if 'custom_alert_text' not in st.session_state: st.session_state.custom_alert_text = "Shop kuri book"
if 'low_limit' not in st.session_state: st.session_state.low_limit = 6000

# --- 3. HELPER FUNCTIONS ---
def send_whatsapp_auto(msg):
    try:
        account_sid, auth_token = st.secrets.get("TWILIO_ACCOUNT_SID", ""), st.secrets.get("TWILIO_AUTH_TOKEN", "")
        if account_sid and auth_token:
            Client(account_sid, auth_token).messages.create(from_='whatsapp:+14155238886', body=msg, to=f'whatsapp:{WA_PHONE}')
    except: pass 

def parse_mixed_dates(date_series):
    parsed = []
    for val in date_series:
        dt = pd.to_datetime(str(val).strip(), errors='coerce')
        if pd.isna(dt): dt = pd.to_datetime(str(val).strip(), dayfirst=True, errors='coerce')
        parsed.append(dt)
    return pd.Series(parsed)

@st.cache_data(ttl=10)
def load_expense_data():
    try:
        df = pd.read_csv(f"{EXPENSE_CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=10)
def load_stock_data():
    try:
        df = pd.read_csv(f"{STOCK_CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        return df
    except: 
        # ഡെമോ ഡാറ്റ (Sheets കണക്ട് ചെയ്യാതെ ടെസ്റ്റ് ചെയ്യാൻ)
        return pd.DataFrame({'Date': ['2026-11-01', '2026-11-02'], 'Item': ['Sugar', 'Milk'], 'Quantity': [100, 50], 'Type': ['Stock In', 'Stock In']})

def generate_pdf(df, title, columns):
    try:
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, txt=title, ln=True, align='C'); pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        col_width = 190 / len(columns)
        for col in columns: pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
        pdf.ln(); pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            for col in columns:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(col_width, 10, txt=val, border=1)
            pdf.ln()
        return bytes(pdf.output())
    except: return None

# --- 4. GROQ AI SETUP ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

def add_new_entry(item, amount, category="Others", type="Debit", entry_date=None):
    try:
        if not entry_date: entry_date = datetime.now().strftime("%Y-%m-%d")
        payload = {"entry.1044099436": entry_date, "entry.2013476337": f"[{st.session_state.user.capitalize()}] {category}: {item}", "entry.1460982454": amount if type.lower() == "debit" else 0, "entry.1221658767": 0 if type.lower() == "debit" else amount}
        requests.post(FORM_API, data=payload, timeout=10)
        send_whatsapp_auto(f"✅ *AI Entry Added*\n📝 Item: {item}\n💰 Amt: ₹{amount}")
        return f"Success: {item} - ₹{amount}"
    except: return "Error"

def add_multiple_entries(entries_list):
    results = []
    try:
        for entry in entries_list:
            payload = {'entry.1044099436': entry.get('date', datetime.now().strftime('%Y-%m-%d')), 'entry.2013476337': f"[{st.session_state.user.capitalize()}] {entry.get('category', 'Others')}: {entry.get('item')}", 'entry.1460982454': entry.get('amount') if entry.get('type', 'Debit').lower() == 'debit' else 0, 'entry.1221658767': 0 if entry.get('type', 'Debit').lower() == 'debit' else entry.get('amount')}
            requests.post(FORM_API, data=payload, timeout=10)
            results.append(f"{entry.get('item')} - ₹{entry.get('amount')}")
        send_whatsapp_auto(f"✅ *AI Multi-Entries Added*\n" + "\n".join(results))
        return f"Success: Added {len(results)} items."
    except: return "Error"

tools = [
    {"type": "function", "function": {"name": "add_new_entry", "description": "Add a single expense/income.", "parameters": {"type": "object", "properties": {"item": {"type": "string"}, "amount": {"type": "number"}, "category": {"type": "string"}, "type": {"type": "string", "enum": ["Debit", "Credit"]}, "date": {"type": "string"}}, "required": ["item", "amount"]}}},
    {"type": "function", "function": {"name": "add_multiple_entries", "description": "Add multiple entries.", "parameters": {"type": "object", "properties": {"entries_list": {"type": "array", "items": {"type": "object", "properties": {"item": {"type": "string"}, "amount": {"type": "number"}, "category": {"type": "string"}, "type": {"type": "string"}, "date": {"type": "string"}}, "required": ["item", "amount"]}}}, "required": ["entries_list"]}}}
]

# --- 5. LOGIN SCREEN ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2:
        st.markdown('<div style="background: rgba(0, 0, 0, 0.8); padding: 30px; border-radius: 20px; margin-top: 30px;">', unsafe_allow_html=True)
        st.subheader("🔐 PAICHI SUPER APP")
        u = st.selectbox("👤 Select User", ["faisal", "shabana", "admin"]).lower()
        pin = st.text_input("🔑 Enter 4-Digit PIN", type="password", max_chars=4)
        if st.button("UNLOCK APP 🔓"):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ Incorrect PIN!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 🌟 ഇവിടെയാണ് പ്രധാന മാറ്റം: ആപ്പ് തിരഞ്ഞെടുക്കാം
    app_mode = st.sidebar.radio("🔄 Switch Application", ["💼 PAICHI BUSINESS (Management)", "🤖 PAICHI EXPENSES (AI Assistant)"])
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

    # ==========================================
    # 💼 PAICHI BUSINESS (Management App)
    # ==========================================
    if app_mode == "💼 PAICHI BUSINESS (Management)":
        st.sidebar.title(f"👋 Business Admin: {st.session_state.user.capitalize()}")
        menu = ["📊 Dashboard", "📦 Stock Management", "👨‍💼 Staff Salary"]
        page = st.sidebar.radio("Menu", menu)
        
        df_fin = load_expense_data()
        bal = (df_fin['Credit'].sum() - df_fin['Debit'].sum()) if not df_fin.empty else 0.0

        if page == "📊 Dashboard":
            st.markdown(f'<div class="banner"><span style="font-size:20px; color:#00BFFF;">Total Business Balance</span><br><span style="font-size:40px; color:#FFF;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
            st.subheader("📈 Recent Transactions")
            if not df_fin.empty:
                st.dataframe(df_fin.tail(10).iloc[::-1], use_container_width=True)

        elif page == "📦 Stock Management":
            st.title("📦 Stock & Inventory")
            df_stk = load_stock_data()
            tab1, tab2, tab3 = st.tabs(["📊 Current Stock", "➕ Add Entry", "📄 Item History"])
            
            with tab1:
                if not df_stk.empty:
                    s = df_stk.copy()
                    s['In'] = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock In' else 0, axis=1)
                    s['Out'] = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock Out' else 0, axis=1)
                    final_stk = s.groupby('Item')[['In', 'Out']].sum().reset_index()
                    final_stk['Available Stock'] = final_stk['In'] - final_stk['Out']
                    st.dataframe(final_stk[['Item', 'Available Stock']], use_container_width=True)
            with tab2:
                with st.form("stock_form", clear_on_submit=True):
                    item_name = st.text_input("Item Name")
                    qty = st.number_input("Quantity", min_value=1.0)
                    stock_type = st.radio("Type", ["Stock In", "Stock Out"], horizontal=True)
                    if st.form_submit_button("SAVE STOCK"):
                        st.success("Stock Updated! ✅ (Demo Mode)")

        elif page == "👨‍💼 Staff Salary":
            st.title("👨‍💼 Staff Salary Management")
            st.info("വരും ദിവസങ്ങളിൽ ഇതിലേക്ക് കൂടുതൽ ഫീച്ചറുകൾ വരും! (Demo Mode)")

    # ==========================================
    # 🤖 PAICHI EXPENSES (Personal AI App)
    # ==========================================
    elif app_mode == "🤖 PAICHI EXPENSES (AI Assistant)":
        df = load_expense_data()
        t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
        bal = t_in - t_out
        
        # Settings (Shabana ഒഴികെയുള്ളവർക്ക്)
        if st.session_state.user != "shabana":
            with st.sidebar.expander("⚙️ Personal Settings"):
                st.session_state.custom_alert_text = st.text_area("Alert Message", value=st.session_state.custom_alert_text)
                st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)
        
        if bal > 0 and bal < st.session_state.low_limit:
            st.markdown(f'<div class="alert-banner">⚠️ ബാലൻസ് കുറവാണ്: {st.session_state.custom_alert_text} (₹{bal:,.2f})!</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="balance-banner"><span style="font-size:20px; color:#E0B0FF;">Available Personal Balance</span><br><span style="font-size:40px; color:#FFD700;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        
        menu = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤖 AI Chat", "🧠 My AI Buddy"]
        if st.session_state.user != "shabana": menu.insert(0, "🏠 Dashboard")
        page = st.sidebar.radio("Menu", menu)

        if page == "🏠 Dashboard" and not df.empty:
            st.title("Personal Financial Overview")
            st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)

        elif page == "💰 Add Entry":
            st.title("Smart Voice Entry 🎙️")
            v_raw = speech_to_text(language='ml', key='voice_v9')
            v_cat, v_amt, v_desc, v_type = "Others", "", "", "Debit"
            
            if v_raw:
                raw = v_raw.lower().replace('.', '').replace(',', '')
                nums = re.findall(r'\d+', raw)
                v_amt = nums[0] if nums else ""
                v_desc = re.sub(r'\d+', '', raw).strip()
                if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ"]): v_cat = "Food"
                elif any(x in raw for x in ["shop", "കട"]): v_cat = "Shop"
                if any(x in raw for x in ["കിട്ടി", "വന്നു", "തന്നു"]): v_type = "Credit"

            with st.form("entry_form", clear_on_submit=True):
                it = st.text_input("Description", value=v_desc)
                am_str = st.text_input("Amount", value=str(v_amt))
                cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"], index=["Food", "Shop", "Fish", "Travel", "Rent", "Others"].index(v_cat))
                ty = st.radio("Type", ["Debit", "Credit"], horizontal=True, index=0 if v_type == "Debit" else 1)
                if st.form_submit_button("SAVE & NOTIFY"):
                    try:
                        am = float(am_str.strip().replace(',', ''))
                        payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.capitalize()}] {cat}: {it}", "entry.1460982454": am if ty=="Debit" else 0, "entry.1221658767": 0 if ty=="Debit" else am}
                        requests.post(FORM_API, data=payload, timeout=10)
                        send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 {it}\n💰 ₹{am}")
                        st.success("Saved! ✅"); st.rerun()
                    except: st.error("Error! Valid amount required.")

        elif page == "🤖 AI Chat":
            st.title("🤖 AI Agent & Assistant")
            st.write("നിങ്ങൾക്ക് ടൈപ്പ് ചെയ്യാം, അല്ലെങ്കിൽ 'ബിരിയാണി 150' എന്ന് പറഞ്ഞാൽ അത് ഷീറ്റിൽ എൻട്രി ഇടും.")
            
            if "messages" not in st.session_state: st.session_state.messages = []
            for message in st.session_state.messages:
                with st.chat_message(message["role"]): st.markdown(message["content"])

            v_raw = speech_to_text(language='ml', key='ai_voice_input')
            prompt = st.chat_input("Ask anything or add expense...", key="ai_chat_box")
            final_prompt = v_raw if v_raw else prompt

            if final_prompt:
                st.session_state.messages.append({"role": "user", "content": final_prompt})
                with st.chat_message("user"): st.markdown(final_prompt)

                with st.spinner("AI ആലോചിക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        system_instruction = f"നീ ഒരു ഫിനാൻസ് AI അസിസ്റ്റന്റാണ്. ഇന്നത്തെ തീയതി: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}. ബാലൻസ്: {bal} Rs. ചെലവ് ചേർക്കാൻ add_new_entry അല്ലെങ്കിൽ add_multiple_entries ടൂൾ ഉപയോഗിക്കുക."
                        messages_for_api = [{"role": "system", "content": system_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-2:]]

                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=messages_for_api,
                            tools=tools,
                            tool_choice="auto",
                            max_tokens=1024
                        )

                        response_message = response.choices[0].message
                        ai_reply = ""
                        entry_saved = False

                        if response_message.tool_calls:
                            for tool_call in response_message.tool_calls:
                                if tool_call.function.name == 'add_new_entry':
                                    args = json.loads(tool_call.function.arguments)
                                    add_new_entry(item=args.get("item"), amount=args.get("amount"), category=args.get("category", "Others"), type=args.get("type", "Debit"), entry_date=args.get("date"))
                                    ai_reply = f"✅ {args.get('item')}-ന് {args.get('amount')} Rs ഞാൻ എൻട്രി ഇട്ടു!"
                                    entry_saved = True
                                elif tool_call.function.name == 'add_multiple_entries':
                                    args = json.loads(tool_call.function.arguments)
                                    add_multiple_entries(entries_list=args.get('entries_list', []))
                                    ai_reply = '✅ പറഞ്ഞ എല്ലാ എൻട്രികളും വിജയകരമായി ചേർത്തു!'
                                    entry_saved = True
                        elif response_message.content:
                            ai_reply = response_message.content
                        else:
                            ai_reply = "ക്ഷമിക്കണം, എനിക്ക് മനസ്സിലായില്ല."

                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        with st.chat_message("assistant"): st.markdown(ai_reply)
                        if entry_saved: st.rerun()

                    except Exception as e:
                        st.error(f"AI Error: {str(e)}")

        elif page == "🧠 My AI Buddy":
            st.title("🧠 Your Personal AI Buddy")
            if "buddy_messages" not in st.session_state: st.session_state.buddy_messages = []
            for msg in st.session_state.buddy_messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
                
            user_input = st.chat_input("Ask me anything...", key="buddy_chat_box")
            if user_input:
                st.session_state.buddy_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"): st.markdown(user_input)
                with st.spinner("ആലോചിക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        messages = [{"role": "system", "content": "You are a helpful personal AI assistant for a Malayali. Answer in Malayalam."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.buddy_messages[-4:]]
                        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, max_tokens=1024)
                        ai_reply = response.choices[0].message.content
                        st.session_state.buddy_messages.append({"role": "assistant", "content": ai_reply})
                        with st.chat_message("assistant"): st.markdown(ai_reply)
                    except Exception as e: st.error(f"Error: {e}")