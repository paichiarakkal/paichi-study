import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
import calendar as py_calendar
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import re
import json
import time
import hashlib
import hmac
import base64
import sqlite3
import smtplib
import os
from email.message import EmailMessage
from groq import Groq
from streamlit_calendar import calendar
from twilio.rest import Client

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="PAICHI EXPENSES PRO", layout="wide")

# --- CONFIG & SETTINGS ---
WA_PHONE = st.secrets.get("DEFAULT_WA_PHONE", "")
BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
SECRET_KEY = st.secrets.get("SESSION_SECRET_KEY", "paichi_expenses_secure_key_2026")
SMTP_EMAIL = st.secrets.get("SMTP_EMAIL", "")
SMTP_APP_PASSWORD = st.secrets.get("SMTP_APP_PASSWORD", "")
RESEND_API_KEY = st.secrets.get("RESEND_API_KEY", "")
OTP_FROM_EMAIL = st.secrets.get("OTP_FROM_EMAIL", "onboarding@resend.dev")
BREVO_API_KEY = st.secrets.get("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = st.secrets.get("BREVO_SENDER_EMAIL", "")
DEFAULT_WEB_APP_URL = st.secrets.get("SHEET_WEB_APP_URL", st.secrets.get("GOOGLE_SHEET_WEB_APP_URL", ""))
DEFAULT_CSV_URL = st.secrets.get("SHEET_CSV_URL", st.secrets.get("GOOGLE_SHEET_CSV_URL", ""))

# 👇 പുതിയ ഡാറ്റാബേസ് (എറർ ഒഴിവാക്കാൻ) 👇
DB_FILE = "paichi_master_v12.db"
NOTES_DIR = "personal_notes"
os.makedirs(NOTES_DIR, exist_ok=True)

# --- TIMEZONE SETUP (GST - Dubai Time) ---
GST = timezone(timedelta(hours=4))
st_autorefresh(interval=60000, key="auto_refresh")

# ============================================
# 🗄️ DATABASE SETUP
# ============================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            sheet_url TEXT DEFAULT '',
            csv_url TEXT DEFAULT '',
            links_locked INTEGER DEFAULT 0,
            account_locked INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS personal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            category TEXT,
            title TEXT,
            details TEXT,
            status TEXT DEFAULT 'Completed'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def db_get_user(username: str):
    u = (username or "").strip().lower()
    if not u: return None
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, password_hash, sheet_url, csv_url, links_locked, account_locked FROM users WHERE username = ?", (u,))
    row = c.fetchone()
    conn.close()
    if row:
        s_url = row[2] or ""
        c_url = row[3] or ""
        return {
            "username": row[0], "password_hash": row[1], "sheet_url": s_url,
            "csv_url": c_url, "links_locked": 1 if (s_url or c_url or row[4]) else 0,
            "account_locked": row[5]
        }
    return None

def db_create_user(username: str, password: str, sheet_url: str = "", csv_url: str = ""):
    u = username.strip().lower()
    if db_get_user(u): raise ValueError("Already registered.")
    pwd_hash = hash_password(password)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash, sheet_url, csv_url, links_locked, account_locked) VALUES (?, ?, ?, ?, ?, 1)", (u, pwd_hash, sheet_url, csv_url, 1 if (sheet_url or csv_url) else 0))
    conn.commit()
    conn.close()
    return {u: {"password_hash": pwd_hash}}

def db_bind_links_once(username: str, sheet_url: str = "", csv_url: str = ""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET sheet_url = ?, csv_url = ?, links_locked = 1 WHERE username = ?", (sheet_url, csv_url, username.strip().lower()))
    conn.commit()
    conn.close()

# ============================================
# 🧠 PERSONAL AI AGENT HELPERS
# ============================================
def log_personal_activity(category: str, title: str, details: str = "", status: str = "Completed"):
    now_str = datetime.now(GST).strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO personal_logs (created_at, category, title, details, status) VALUES (?, ?, ?, ?, ?)", (now_str, category, title, details, status))
    conn.commit()
    conn.close()

def manage_personal_notes(action: str, note_title: str, content: str = "") -> str:
    act = (action or "save").strip().lower()
    if act == "list":
        files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".md"))
        return "[Notes] " + (", ".join(files) if files else "ഒന്നുമില്ല")
    filename = re.sub(r"[^\w\s-]", "", note_title.strip()).replace(" ", "_") + ".md"
    filepath = os.path.join(NOTES_DIR, filename)
    if act == "read" and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f: return f"[Notes] '{filename}':\n\n{f.read()}"
    stamp = datetime.now(GST).strftime("%Y-%m-%d %H:%M")
    with open(filepath, "a" if act == "append" else "w", encoding="utf-8") as f:
        f.write(f"\n\n---\n*Added: {stamp}*\n\n{content}" if act == "append" else f"# {note_title}\n\n*Created: {stamp}*\n\n{content}")
    log_personal_activity("Notes", f"{act.capitalize()}: {filename}", content[:50])
    return f"[Notes] '{filename}' വിജയകരമായി {act} ചെയ്തു."

def manage_tasks_and_schedule(action: str, item_title: str, time_or_priority: str = "") -> str:
    log_personal_activity("Schedule / Task", f"{action}: {item_title}", time_or_priority)
    return f"[Task/Reminder] '{item_title}' ({time_or_priority}) വിജയകരമായി രേഖപ്പെടുത്തി."

# ============================================
# 📧 EMAIL OTP & AUTH
# ============================================
def send_otp_email(to_email: str, otp_code: str, purpose: str = "OTP Verification") -> bool:
    brevo_key = (st.secrets.get("BREVO_API_KEY", BREVO_API_KEY) or "").strip()
    brevo_sender = (st.secrets.get("BREVO_SENDER_EMAIL", BREVO_SENDER_EMAIL) or "").strip()
    resend_key = (st.secrets.get("RESEND_API_KEY", RESEND_API_KEY) or "").strip()
    from_email = (st.secrets.get("OTP_FROM_EMAIL", OTP_FROM_EMAIL) or "onboarding@resend.dev").strip()

    body_text = f"Hello,\n\nYour 6-digit OTP code for PAICHI ({purpose}) is:\n\nOTP: {otp_code}\n\nPlease do not share this code."

    if brevo_key and brevo_sender:
        resp = requests.post("https://api.brevo.com/v3/smtp/email", headers={"api-key": brevo_key, "Content-Type": "application/json"}, json={"sender": {"name": "PAICHI", "email": brevo_sender}, "to": [{"email": to_email}], "subject": f"PAICHI - {purpose} OTP", "textContent": body_text}, timeout=15)
        if resp.status_code in (200, 201, 202): return True
        raise RuntimeError(f"Brevo Error: {resp.text}")

    if resend_key:
        resp = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"}, json={"from": from_email, "to": [to_email], "subject": f"PAICHI - {purpose} OTP", "text": body_text}, timeout=15)
        if resp.status_code in (200, 201): return True
        raise RuntimeError(f"Resend Error: {resp.text}")

    sender = (st.secrets.get("SMTP_EMAIL", SMTP_EMAIL) or "").strip()
    app_pwd = (st.secrets.get("SMTP_APP_PASSWORD", SMTP_APP_PASSWORD) or "").replace(" ", "").strip()

    if not sender or not app_pwd: raise ValueError("Email config missing.")
    msg = EmailMessage()
    msg["Subject"] = f"PAICHI - {purpose} OTP"
    msg["From"], msg["To"] = sender, to_email
    msg.set_content(body_text)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        server.login(sender, app_pwd)
        server.send_message(msg)
    return True

def create_session_token(username: str) -> str:
    sig = hmac.new(SECRET_KEY.encode(), username.strip().lower().encode(), hashlib.sha256).hexdigest()[:24]
    return base64.urlsafe_b64encode(f"{username.strip().lower()}:{sig}".encode()).decode()

def verify_session_token(token: str):
    try:
        u, sig = base64.urlsafe_b64decode(token.encode()).decode().split(":", 1)
        expected = hmac.new(SECRET_KEY.encode(), u.encode(), hashlib.sha256).hexdigest()[:24]
        if hmac.compare_digest(sig, expected): return u
    except: pass
    return None

def restore_session_from_url():
    if not st.session_state.get("auth", False):
        token = st.query_params.get("session", "")
        if token:
            valid_user = verify_session_token(token)
            if valid_user and db_get_user(valid_user):
                st.session_state.auth, st.session_state.user = True, valid_user

def set_persistent_login(username: str):
    st.session_state.auth, st.session_state.user = True, username.strip().lower()
    st.query_params["session"] = create_session_token(username)

def clear_persistent_login():
    st.session_state.auth, st.session_state.user = False, ""
    if "session" in st.query_params: del st.query_params["session"]

# ============================================
# 🎨 CSS & HELPER FUNCTIONS
# ============================================
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-image: linear-gradient(rgba(10, 10, 25, 0.85), rgba(10, 10, 25, 0.95)), url("{BG_IMAGE_URL}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background: rgba(20, 20, 35, 0.6) !important; backdrop-filter: blur(15px); }}
    .stButton>button {{ background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border-radius: 12px; font-weight: bold; }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px; text-align: center; margin-bottom: 25px; }}
    .balance-banner {{ background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02)); padding: 30px; border-radius: 20px; border-left: 8px solid #FFD700; text-align: center; margin-bottom: 25px; }}
    .login-card {{ background: rgba(20, 20, 35, 0.8); padding: 40px; border-radius: 20px; max-width: 450px; margin: auto; margin-top: 80px; }}
    h1, h2, h3, p, label {{ color: #FFFFFF !important; font-weight: bold !important; }}
    input, textarea {{ color: #FFFFFF !important; background-color: rgba(0, 0, 0, 0.5) !important; }}
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if "ai_chat_history" not in st.session_state: st.session_state.ai_chat_history = []
if "pending_entry" not in st.session_state: st.session_state.pending_entry = None
if "signup_otp" not in st.session_state: st.session_state.signup_otp = None

restore_session_from_url()

def format_display_name(username: str) -> str: return username.split("@")[0] if "@" in username else username
def format_english_datetime(dt_value=None) -> str: return (datetime.now(GST) if dt_value is None else pd.to_datetime(dt_value)).strftime("%d %b %Y %H:%M:%S")

def translate_to_english_label(text: str, default_label: str = "Expense") -> str:
    raw = (text or "").strip()
    if not raw: return default_label
    mapping = {"ചായ": "Tea", "കാപ്പി": "Coffee", "ഭക്ഷണം": "Food", "ചിക്കൻ": "Chicken", "മീൻ": "Fish", "ബിരിയാണി": "Biryani", "കട": "Shop", "യാത്ര": "Travel", "പെട്രോൾ": "Petrol", "വാടക": "Rent"}
    for k, v in mapping.items():
        if k in raw.lower(): return v
    if GROQ_API_KEY and re.search(r"[^\x00-\x7F]", raw):
        try:
            resp = Groq(api_key=GROQ_API_KEY).chat.completions.create(model="openai/gpt-oss-120b", messages=[{"role": "system", "content": "Translate to concise English."}, {"role": "user", "content": raw}], max_tokens=30)
            return (resp.choices[0].message.content or "").strip().strip('"')
        except: pass
    return re.sub(r"[^\x00-\x7F]+", "", raw).strip() or default_label

def get_active_web_app_url() -> str:
    prof = db_get_user(st.session_state.get("user", ""))
    return prof["sheet_url"].strip() if prof and prof.get("sheet_url") else ""

def get_active_csv_url() -> str:
    prof = db_get_user(st.session_state.get("user", ""))
    return prof["csv_url"].strip() if prof and prof.get("csv_url") else ""

def refresh_user_sheet_cache(): st.cache_data.clear()

@st.cache_data(ttl=5)
def load_data(active_csv_url="", cache_buster=0):
    try:
        if not active_csv_url: return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])
        sep = "&" if "?" in active_csv_url else "?"
        df = pd.read_csv(f"{active_csv_url}{sep}r={random.randint(1,999999)}_{cache_buster}")
        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except Exception: return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])

def add_new_entry(item, amount, category="Others", type="Debit", entry_date=None):
    try:
        target_url = get_active_web_app_url()
        eng_item = translate_to_english_label(item, "Expense")
        payload = {"item": eng_item, "amount": amount, "category": category, "type": type, "date": format_english_datetime(entry_date)}
        if target_url:
            requests.post(target_url, json=payload, timeout=10)
            refresh_user_sheet_cache()
        return True, f"Saved: {eng_item} - ₹{amount}"
    except Exception as e: return False, f"Failed: {e}"

def send_whatsapp_auto(msg):
    try:
        account_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
        auth_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
        if account_sid and auth_token and WA_PHONE:
            client = Client(account_sid, auth_token)
            client.messages.create(from_='whatsapp:+14155238886', body=msg, to=f'whatsapp:+{WA_PHONE}')
    except Exception: pass

# --- 🔒 LOGIN & SIGN UP WITH OTP ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("🔐 PAICHI EXPENSES")
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            l_user = st.text_input("📧 Email", key="login_user").strip().lower()
            l_pass = st.text_input("🔑 Password", type="password", key="login_pass")
            if st.button("LOGIN 🔓"):
                user_rec = db_get_user(l_user)
                if user_rec and user_rec["password_hash"] == hash_password(l_pass):
                    set_persistent_login(l_user)
                    st.rerun()
                else: st.error("❌ Invalid credentials.")
                
        with tab2:
            s_user = st.text_input("📧 Email", key="signup_user").strip().lower()
            if st.button("📩 Send OTP"):
                if not s_user or "@" not in s_user: st.error("Enter valid email.")
                elif db_get_user(s_user): st.error("Already registered.")
                else:
                    code = f"{random.randint(100000, 999999)}"
                    st.session_state.signup_otp = code
                    try:
                        send_otp_email(s_user, code, "Sign Up")
                        st.success("OTP Sent!")
                    except Exception as e: st.error(f"Failed: {e}")
            
            if st.session_state.signup_otp:
                otp_in = st.text_input("🔢 Enter OTP", max_chars=6)
                s_pass = st.text_input("🔑 Create Password", type="password")
                if st.button("SIGN UP ✨"):
                    if otp_in == st.session_state.signup_otp and s_pass:
                        db_create_user(s_user, s_pass)
                        set_persistent_login(s_user)
                        st.rerun()
                    else: st.error("Invalid OTP or empty password.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APP ---
else:
    user_profile = db_get_user(st.session_state.user) or {}
    active_csv = get_active_csv_url()
    df = load_data(active_csv)
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out

    st.sidebar.caption(f"👤 {format_display_name(st.session_state.user)}")
    
    with st.sidebar.expander("🔗 Link Sheet (One-Time)"):
        if user_profile.get("links_locked") == 1 or user_profile.get("sheet_url"):
            st.info("🔒 Sheet links locked.")
        else:
            sb_sheet = st.text_input("Sheet Web App Link", key="sb_sheet_url").strip()
            sb_csv = st.text_input("Sheet CSV Link", key="sb_csv_url").strip()
            if st.button("SUBMIT LINK ONCE 🔒"):
                if sb_sheet or sb_csv:
                    db_bind_links_once(st.session_state.user, sb_sheet, sb_csv)
                    refresh_user_sheet_cache()
                    st.success("✅ Links locked!")
                    time.sleep(1)
                    st.rerun()

    menu = ["🏠 Dashboard", "💰 Add Entry", "📅 Calendar", "📊 Report", "🧠 Personal AI Buddy", "🤖 AI Chat"]
    page = st.sidebar.radio("Menu", menu)

    if st.sidebar.button("Logout"):
        clear_persistent_login()
        st.rerun()

    # --- DASHBOARD ---
    if page == "🏠 Dashboard":
        if bal < 6000:
            st.markdown(f'<div style="background:red; color:white; padding:10px; border-radius:10px; text-align:center;">⚠️ Low Balance Alert! (₹{bal:,.2f})</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="balance-banner"><span style="font-size:22px; color:#E0B0FF;">AVAILABLE BALANCE</span><br><span style="font-size:50px; color:#FFD700;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)

    # --- ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml-IN', key='voice_v9')
        v_cat, v_amt, v_desc, v_type = "Others", "", "", "Debit"
        if v_raw:
            raw = v_raw.lower().replace('.', '').replace(',', '')
            nums = re.findall(r'\d+', raw)
            v_amt = nums[0] if nums else ""
            v_desc = translate_to_english_label(re.sub(r'\d+', '', raw).strip(), "Expense")
            if any(x in raw for x in ["food", "tea", "ഭക്ഷണം", "ചായ"]): v_cat = "Food"
            if any(x in raw for x in ["credit", "received", "salary", "കിട്ടി"]): v_type = "Credit"

        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount", value=str(v_amt))
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True, index=0 if v_type == "Debit" else 1)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    ok, msg = add_new_entry(it, float(am_str), cat, ty)
                    if ok: 
                        send_whatsapp_auto(f"✅ Entry Added: {it} - ₹{am_str}")
                        st.success("Saved!"); time.sleep(1); st.rerun()
                    else: st.error(msg)
                except Exception as e: st.error(f"Error: {e}")

    # --- CALENDAR ---
    elif page == "📅 Calendar":
        st.title("P&L Calendar View 📅")
        if df.empty: st.info("No data available yet.")
        else:
            df_cal = df.dropna(subset=['Date']).copy()
            df_cal['DayKey'] = df_cal['Date'].dt.strftime('%Y-%m-%d')
            summary = df_cal.groupby('DayKey', as_index=False).agg({'Debit': 'sum', 'Credit': 'sum'})
            events = []
            for _, row in summary.iterrows():
                if row['Debit'] > 0: events.append({"title": f"-₹{row['Debit']:,.0f}", "start": row['DayKey'], "backgroundColor": "#d9383a"})
                if row['Credit'] > 0: events.append({"title": f"+₹{row['Credit']:,.0f}", "start": row['DayKey'], "backgroundColor": "#2e8b57"})
            calendar_options = {"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth", "height": "auto"}
            cal_data = calendar(events=events, options=calendar_options, key="pnl_calendar_view")
            if cal_data and cal_data.get("callback") == "dateClick":
                selected_date = cal_data.get("dateClick", {}).get("date", "").split("T")[0]
                st.subheader(f"📋 Details for {selected_date}")
                day_df = df_cal[df_cal['DayKey'] == selected_date]
                if not day_df.empty: st.dataframe(day_df[['Item', 'Debit', 'Credit']], use_container_width=True)
                else: st.info("No entries for this date.")

    # --- REPORT ---
    elif page == "📊 Report":
        if df.empty: st.info("No data available yet.")
        else:
            df_rep = df.dropna(subset=['Date']).copy()
            df_rep['Month'] = df_rep['Date'].dt.strftime('%B %Y')
            months = df_rep.dropna(subset=['Month']).sort_values(by='Date', ascending=False)['Month'].unique()
            if len(months) > 0:
                sel_m = st.selectbox("Select Month", months)
                m_df = df_rep[df_rep['Month'] == sel_m].copy()
                st.dataframe(m_df, use_container_width=True)

    # --- PERSONAL AI BUDDY ---
    elif page == "🧠 Personal AI Buddy":
        st.title("🧠 Personal Notes & Tasks")
        st.subheader("📓 നോട്ടുകൾ")
        files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".md"))
        if files:
            chosen = st.selectbox("തിരഞ്ഞെടുക്കുക", files)
            with open(os.path.join(NOTES_DIR, chosen), "r", encoding="utf-8") as f: st.markdown(f.read())
        else: st.info("നോട്ടുകൾ ഒന്നുമില്ല.")
        st.divider()
        st.subheader("📌 ലോഗുകൾ")
        conn = sqlite3.connect(DB_FILE)
        logs_df = pd.read_sql_query("SELECT created_at AS Time, category AS Category, title AS Title, details AS Details FROM personal_logs ORDER BY id DESC LIMIT 10", conn)
        conn.close()
        if not logs_df.empty: st.dataframe(logs_df, use_container_width=True, hide_index=True)

    # --- AI CHAT (Agentic AI) ---
    elif page == "🤖 AI Chat":
        st.title("🤖 Agentic AI Chat")
        
        for h_msg in st.session_state.ai_chat_history[-8:]:
            with st.chat_message(h_msg["role"]): st.markdown(h_msg["content"])

        v_raw = speech_to_text(language='ml-IN', start_prompt="🎙️ Speak", stop_prompt="⏹️ Stop", just_once=True, key="ai_voice_chat")
        prompt = st.chat_input("Type here...")
        
        final_prompt = v_raw if v_raw else prompt

        if final_prompt:
            with st.chat_message("user"): st.markdown(final_prompt)
            st.session_state.ai_chat_history.append({"role": "user", "content": final_prompt})
            
            with st.spinner("ഏജന്റ് ചിന്തിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    sys_prompt = """
                    You are a multi-tasking AI Agent. Reply ONLY with JSON.
                    1. For expenses: {"action":"expense", "item":"Name", "amount":100, "category":"Food", "type":"Debit"}
                    2. For notes: {"action":"note", "note_title":"Title", "content":"Content"}
                    3. For tasks/reminders: {"action":"task", "item_title":"Task Name", "time_or_priority":"Time"}
                    4. For chat: {"action":"chat", "reply":"Your response"}
                    """
                    
                    resp = client.chat.completions.create(
                        model="openai/gpt-oss-120b", 
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": final_prompt}], 
                        max_tokens=300
                    )
                    
                    raw_out = (resp.choices[0].message.content or "").strip()
                    json_match = re.search(r"\{.*\}", raw_out, re.DOTALL)
                    
                    if json_match:
                        parsed = json.loads(json_match.group(0))
                        action = parsed.get("action")
                        
                        if action == "expense":
                            ok, msg = add_new_entry(parsed.get("item"), float(parsed.get("amount", 0)), parsed.get("category"), parsed.get("type"))
                            st.session_state.ai_chat_history.append({"role": "assistant", "content": msg})
                            st.success(msg)
                            
                        elif action == "note":
                            msg = manage_personal_notes("save", parsed.get("note_title", "Note"), parsed.get("content", ""))
                            st.session_state.ai_chat_history.append({"role": "assistant", "content": msg})
                            st.success(msg)
                            
                        elif action == "task":
                            msg = manage_tasks_and_schedule("add", parsed.get("item_title", "Task"), parsed.get("time_or_priority", ""))
                            st.session_state.ai_chat_history.append({"role": "assistant", "content": msg})
                            st.success(msg)
                            
                        else:
                            reply = parsed.get("reply", "എനിക്ക് മനസ്സിലായില്ല.")
                            st.session_state.ai_chat_history.append({"role": "assistant", "content": reply})
                            st.markdown(reply)
                    else:
                        st.session_state.ai_chat_history.append({"role": "assistant", "content": raw_out})
                        st.markdown(raw_out)
                        
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")