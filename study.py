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
from email.message import EmailMessage
from groq import Groq
from streamlit_calendar import calendar
from twilio.rest import Client
import urllib.parse

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="PAICHI EXPENSES", layout="wide")

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

# 👇 പുതിയ മാറ്റം: എല്ലാവർക്കും ഒരേ Master URL 👇
DEFAULT_WEB_APP_URL = st.secrets.get("MASTER_WEB_APP_URL", "")
DB_FILE = "paichi_users_v2.db"

# --- TIMEZONE SETUP (GST - Dubai Time) ---
GST = timezone(timedelta(hours=4))

st_autorefresh(interval=60000, key="auto_refresh")

# ============================================
# 🗄️ DATABASE + ST.SECRETS USER STORE
# ============================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def load_secrets_users() -> dict:
    raw_users = st.secrets.get("USERS_DATA", {})
    if isinstance(raw_users, str):
        try:
            parsed = json.loads(raw_users)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    if isinstance(raw_users, dict):
        return dict(raw_users)
    return {}

def is_account_already_registered(username: str) -> bool:
    u = (username or "").strip().lower()
    if not u:
        return False
    if u in load_secrets_users():
        return True
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (u,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def db_get_user(username: str):
    init_db()
    u = (username or "").strip().lower()
    if not u:
        return None

    secrets_users = load_secrets_users()
    if u in secrets_users and isinstance(secrets_users[u], dict):
        pwd_hash = secrets_users[u].get("password_hash", "")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
            (u, pwd_hash)
        )
        conn.commit()
        conn.close()
        return {"username": u, "password_hash": pwd_hash}

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, password_hash FROM users WHERE username = ?", (u,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "password_hash": row[1]}
    return None

def db_create_user(username: str, password: str):
    init_db()
    u = username.strip().lower()
    if is_account_already_registered(u):
        raise ValueError("This Google/email account is already registered.")
    pwd_hash = hash_password(password)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (u, pwd_hash))
    conn.commit()
    conn.close()
    return {u: {"password_hash": pwd_hash}}

def db_update_password(username: str, new_password: str):
    init_db()
    u = username.strip().lower()
    pwd_hash = hash_password(new_password)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (pwd_hash, u))
    conn.commit()
    conn.close()
    return pwd_hash

# ============================================
# 📧 FREE EMAIL OTP HELPER
# ============================================
def send_otp_email(to_email: str, otp_code: str, purpose: str = "OTP Verification") -> bool:
    brevo_key = (st.secrets.get("BREVO_API_KEY", BREVO_API_KEY) or "").strip()
    brevo_sender = (st.secrets.get("BREVO_SENDER_EMAIL", BREVO_SENDER_EMAIL) or "").strip()
    resend_key = (st.secrets.get("RESEND_API_KEY", RESEND_API_KEY) or "").strip()
    from_email = (st.secrets.get("OTP_FROM_EMAIL", OTP_FROM_EMAIL) or "onboarding@resend.dev").strip()

    body_text = f"Hello,\n\nYour 6-digit OTP code for PAICHI EXPENSES ({purpose}) is:\n\nOTP: {otp_code}\n\nPlease do not share this code."

    if brevo_key and brevo_sender:
        resp = requests.post("https://api.brevo.com/v3/smtp/email", headers={"api-key": brevo_key, "Content-Type": "application/json"}, json={"sender": {"name": "PAICHI EXPENSES", "email": brevo_sender}, "to": [{"email": to_email}], "subject": f"PAICHI EXPENSES - {purpose} OTP", "textContent": body_text}, timeout=15)
        if resp.status_code in (200, 201, 202): return True
        raise RuntimeError(f"Brevo API Error: {resp.text}")

    if resend_key:
        resp = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"}, json={"from": from_email, "to": [to_email], "subject": f"PAICHI EXPENSES - {purpose} OTP", "text": body_text}, timeout=15)
        if resp.status_code in (200, 201): return True
        raise RuntimeError(f"Resend API Error: {resp.text}")

    sender = (st.secrets.get("SMTP_EMAIL", SMTP_EMAIL) or "").strip()
    app_pwd = (st.secrets.get("SMTP_APP_PASSWORD", SMTP_APP_PASSWORD) or "").replace(" ", "").strip()

    if not sender or not app_pwd: raise ValueError("Email configuration missing in Secrets.")
    msg = EmailMessage()
    msg["Subject"] = f"PAICHI EXPENSES - {purpose} OTP"
    msg["From"], msg["To"] = sender, to_email
    msg.set_content(body_text)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        server.login(sender, app_pwd)
        server.send_message(msg)
    return True

# ============================================
# 🔐 SIGNED TOKEN SESSION
# ============================================
def create_session_token(username: str) -> str:
    u = username.strip().lower()
    sig = hmac.new(SECRET_KEY.encode("utf-8"), u.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
    raw = f"{u}:{sig}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")

def verify_session_token(token: str):
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        u, sig = decoded.split(":", 1)
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), u.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
        if hmac.compare_digest(sig, expected_sig): return u
    except Exception: pass
    return None

def restore_session_from_url():
    if not st.session_state.get("auth", False):
        token = st.query_params.get("session", "")
        if token:
            valid_user = verify_session_token(token)
            if valid_user and db_get_user(valid_user):
                st.session_state.auth = True
                st.session_state.user = valid_user

def set_persistent_login(username: str):
    u = username.strip().lower()
    st.session_state.auth = True
    st.session_state.user = u
    st.query_params["session"] = create_session_token(u)

def clear_persistent_login():
    st.session_state.auth = False
    st.session_state.user = ""
    if "session" in st.query_params: del st.query_params["session"]

# ============================================
# 🎨 3D GLASSMORPHISM CSS
# ============================================
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-image: linear-gradient(rgba(10, 10, 25, 0.85), rgba(10, 10, 25, 0.95)), url("{BG_IMAGE_URL}"); background-size: cover; background-attachment: fixed; background-position: center; }}
    [data-testid="stSidebar"] {{ background: rgba(20, 20, 35, 0.6) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 5px 0 15px rgba(0,0,0,0.5); }}
    .stButton>button {{ background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border-radius: 12px; font-weight: bold; width: 100%; border: none; padding: 10px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4); }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); margin-bottom: 25px; text-align: center; }}
    .balance-banner {{ background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02)); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; border-left: 8px solid #FFD700; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .category-box {{ background: rgba(0, 0, 0, 0.5); padding: 20px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }}
    .alert-banner {{ background: linear-gradient(90deg, #ff4d4d, #cc0000); color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }}
    .login-card {{ background: rgba(20, 20, 35, 0.8); backdrop-filter: blur(20px); padding: 40px; border-radius: 20px; max-width: 450px; margin: auto; margin-top: 80px; border: 1px solid rgba(255, 255, 255, 0.1); }}
    h1, h2, h3, p, label {{ color: #FFFFFF !important; font-weight: bold !important; }}
    [data-testid="stChatMessage"] {{ background: rgba(32, 44, 51, 0.9) !important; border-radius: 15px !important; padding: 15px !important; }}
    input, textarea, select {{ color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; background-color: rgba(0, 0, 0, 0.5) !important; }}
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if 'custom_alert_text' not in st.session_state: st.session_state.custom_alert_text = "Low balance alert"
if 'low_limit' not in st.session_state: st.session_state.low_limit = 6000
if "last_processed_prompt" not in st.session_state: st.session_state.last_processed_prompt = None
if "pending_entry" not in st.session_state: st.session_state.pending_entry = None
if "ai_action_notice" not in st.session_state: st.session_state.ai_action_notice = None
if "entry_saved_flag" not in st.session_state: st.session_state.entry_saved_flag = False
if "ai_chat_key_id" not in st.session_state: st.session_state.ai_chat_key_id = 0
if "last_voice_text" not in st.session_state: st.session_state.last_voice_text = ""
if "last_heard_text" not in st.session_state: st.session_state.last_heard_text = ""
if "ai_chat_history" not in st.session_state: st.session_state.ai_chat_history = []

if "signup_otp" not in st.session_state: st.session_state.signup_otp = None
if "signup_otp_email" not in st.session_state: st.session_state.signup_otp_email = ""
if "signup_otp_verified" not in st.session_state: st.session_state.signup_otp_verified = False

if "reset_otp" not in st.session_state: st.session_state.reset_otp = None
if "reset_otp_email" not in st.session_state: st.session_state.reset_otp_email = ""
if "reset_otp_verified" not in st.session_state: st.session_state.reset_otp_verified = False

restore_session_from_url()

# --- HELPER FUNCTIONS ---
def format_display_name(username: str) -> str:
    u = (username or "").strip()
    return u.split("@", 1)[0] if "@" in u else u

def format_english_datetime(dt_value=None) -> str:
    dt_obj = datetime.now(GST) if dt_value is None else pd.to_datetime(dt_value)
    return dt_obj.strftime("%d %b %Y %H:%M:%S")

def translate_to_english_label(text: str, default_label: str = "Expense") -> str:
    raw = (text or "").strip()
    if not raw: return default_label
    low = raw.lower()
    mapping = {"ചായ": "Tea", "കാപ്പി": "Coffee", "ഭക്ഷണം": "Food", "ചിക്കൻ": "Chicken", "മീൻ": "Fish", "ബിരിയാണി": "Biryani", "കട": "Shop", "യാത്ര": "Travel", "പെട്രോൾ": "Petrol", "വാടക": "Rent"}
    for k, v in mapping.items():
        if k in low: return v
    if GROQ_API_KEY and re.search(r"[^\x00-\x7F]", raw):
        try:
            client = Groq(api_key=GROQ_API_KEY)
            resp = client.chat.completions.create(model="openai/gpt-oss-120b", messages=[{"role": "system", "content": "Translate text into concise English. Return ONLY text."}, {"role": "user", "content": raw}], max_tokens=30)
            translated = (resp.choices[0].message.content or "").strip().strip('"').strip("'")
            if translated: return translated
        except Exception: pass
    cleaned = re.sub(r"[^\x00-\x7F]+", "", raw).strip()
    return cleaned if cleaned else default_label

def categorize_item_label(item_str: str) -> str:
    low = str(item_str or "").lower()
    if any(w in low for w in ["food", "tea", "coffee", "biryani", "ഭക്ഷണം", "ചായ"]): return "Food"
    elif any(w in low for w in ["shop", "grocery", "കട"]): return "Shop"
    elif any(w in low for w in ["fish", "meat", "മീൻ", "ചിക്കൻ"]): return "Fish"
    elif any(w in low for w in ["travel", "petrol", "taxi", "യാത്ര", "പെട്രോൾ"]): return "Travel"
    elif any(w in low for w in ["rent", "വാടക"]): return "Rent"
    return "Others"

def build_full_financial_context(df_exp: pd.DataFrame, df_d: pd.DataFrame) -> str:
    now_gst = datetime.now(GST)
    t_in = float(df_exp["Credit"].sum()) if not df_exp.empty else 0.0
    t_out = float(df_exp["Debit"].sum()) if not df_exp.empty else 0.0
    bal = t_in - t_out
    return f"Current Date: {now_gst.strftime('%d %b %Y')}. Balance: ₹{bal:,.2f}, Total Credit: ₹{t_in:,.2f}, Total Debit: ₹{t_out:,.2f}."

# ============================================
# 🔥 പുതിയ മാറ്റം: എല്ലാവർക്കും MASTER URL
# ============================================
def get_active_web_app_url() -> str:
    master_url = (st.secrets.get("MASTER_WEB_APP_URL", DEFAULT_WEB_APP_URL) or "").strip()
    if not master_url: return ""
    # ഉപയോക്താവിന്റെ ഇമെയിൽ URL-ൽ ചേർക്കുന്നു
    user_email = st.session_state.get("user", "").strip().lower()
    encoded_email = urllib.parse.quote(user_email)
    sep = "&" if "?" in master_url else "?"
    return f"{master_url}{sep}email={encoded_email}"

def get_active_csv_url() -> str:
    return get_active_web_app_url() # Apps Script doGet ഇതേ URL ഉപയോഗിക്കുന്നു

def send_whatsapp_auto(msg):
    try:
        account_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
        auth_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
        if account_sid and auth_token and WA_PHONE:
            client = Client(account_sid, auth_token)
            client.messages.create(from_='whatsapp:+14155238886', body=msg, to=f'whatsapp:+{WA_PHONE}')
    except Exception: pass

def parse_mixed_dates(date_series):
    parsed = []
    for val in date_series:
        dt = pd.to_datetime(str(val).strip(), errors='coerce')
        if pd.isna(dt): dt = pd.to_datetime(str(val).strip(), dayfirst=True, errors='coerce')
        parsed.append(dt)
    return pd.Series(parsed)

@st.cache_data(ttl=5)
def load_data(active_csv_url="", cache_buster=0):
    try:
        target_csv = (active_csv_url or "").strip()
        if not target_csv: return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])
        sep = "&" if "?" in target_csv else "?"
        df = pd.read_csv(f"{target_csv}{sep}r={random.randint(1,999999)}_{cache_buster}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])

def refresh_user_sheet_cache():
    st.cache_data.clear()

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, txt="FINANCE REPORT", ln=True, align='C')
        pdf.ln(10)
        widths = {"Date": 30, "Item": 85, "Debit": 35, "Credit": 35}
        pdf.set_font("Arial", 'B', 10)
        for col in widths: pdf.cell(widths[col], 10, txt=col, border=1, align='C')
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            if pdf.get_y() > 260: pdf.add_page()
            pdf.cell(30, 10, txt=str(row['Date']), border=1)
            pdf.cell(85, 10, txt=str(row['Item']).encode('ascii', 'ignore').decode('ascii'), border=1)
            pdf.cell(35, 10, txt=str(row['Debit']), border=1, align='R')
            pdf.cell(35, 10, txt=str(row['Credit']), border=1, align='R')
            pdf.ln()
        return bytes(pdf.output())
    except Exception: return None

# ============================================
# 🚀 DATA SAVING FUNCTION (Adds email to payload)
# ============================================
def add_new_entry(item, amount, category="Others", type="Debit", entry_date=None):
    try:
        target_url = get_active_web_app_url()
        eng_item = translate_to_english_label(item, "Expense")
        eng_cat = translate_to_english_label(category, "Others")
        eng_date = format_english_datetime(entry_date)
        
        payload = {
            "user_email": st.session_state.get("user", ""), # 👈 ഉപയോക്താവിന്റെ ഇമെയിൽ ഇവിടെ ചേർക്കുന്നു
            "item": eng_item,
            "amount": amount,
            "category": eng_cat,
            "type": type,
            "date": eng_date
        }
        if target_url:
            requests.post(target_url, json=payload, timeout=10)
            refresh_user_sheet_cache()
        send_whatsapp_auto(f"✅ Entry Added: {eng_item} - ₹{amount} ({type})")
        return True, f"Entry saved: {eng_item} - ₹{amount}"
    except Exception as e:
        return False, f"Failed: {str(e)}"

def add_debt_via_ai(name, type, amount, date=None):
    try:
        target_url = get_active_web_app_url()
        eng_name = translate_to_english_label(name, "Person")
        eng_type = "Lent" if "Lent" in str(type) or "കൊടുത്ത" in str(type) else "Borrowed"
        eng_date_str = " ".join(format_english_datetime(date).split(" ")[0:3])
        
        payload = {
            "user_email": st.session_state.get("user", ""), # 👈 ഇവിടെയും ചേർക്കുന്നു
            "action": "add_debt",
            "name": eng_name,
            "type": eng_type,
            "amount": amount,
            "date": eng_date_str
        }
        if target_url:
            requests.post(target_url, json=payload, timeout=10)
            refresh_user_sheet_cache()
        return True, f"Debt saved: {eng_type} - {eng_name}"
    except Exception as e:
        return False, f"Failed: {str(e)}"

# --- 🔒 LOGIN, SIGN UP & FORGOT PASSWORD ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("🔐 PAICHI EXPENSES")

        mode_tab1, mode_tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

        with mode_tab1:
            l_user = st.text_input("📧 Email / Username", key="login_user").strip().lower()
            l_pass = st.text_input("🔑 Password", type="password", key="login_pass")

            if st.button("LOGIN 🔓", key="btn_login"):
                user_rec = db_get_user(l_user)
                if not l_user or not l_pass: st.error("❌ Enter email and password.")
                elif not user_rec: st.error("❌ Account not found. Sign up first.")
                elif user_rec["password_hash"] == hash_password(l_pass):
                    refresh_user_sheet_cache()
                    set_persistent_login(l_user)
                    st.rerun()
                else: st.error("❌ Incorrect password.")

            with st.expander("🔄 Forgot Password (Email OTP)"):
                r_user = st.text_input("📧 Registered Email", key="reset_user").strip().lower()
                if st.button("📩 Send Reset OTP", key="btn_send_reset_otp"):
                    if not r_user or not db_get_user(r_user) or "@" not in r_user: st.error("❌ Valid registered email required.")
                    else:
                        code = f"{random.randint(100000, 999999)}"
                        st.session_state.reset_otp, st.session_state.reset_otp_email, st.session_state.reset_otp_verified = code, r_user, False
                        try:
                            send_otp_email(r_user, code, purpose="Reset Password")
                            st.success("✅ OTP sent to email.")
                        except Exception as e: st.error(f"❌ Failed: {e}")

                if st.session_state.reset_otp and st.session_state.reset_otp_email == r_user:
                    r_otp_in = st.text_input("🔢 Enter Reset OTP", key="reset_otp_input", max_chars=6)
                    if st.button("✅ Verify OTP", key="btn_verify_reset_otp"):
                        if r_otp_in.strip() == st.session_state.reset_otp:
                            st.session_state.reset_otp_verified = True
                            st.success("✅ OTP verified.")
                        else: st.error("❌ Invalid OTP.")

                if st.session_state.reset_otp_verified and st.session_state.reset_otp_email == r_user:
                    r_new_pass = st.text_input("🔑 New Password", type="password", key="reset_new_pass")
                    r_confirm_pass = st.text_input("🔒 Confirm Password", type="password", key="reset_confirm_pass")
                    if st.button("RESET PASSWORD 🔁", key="btn_reset_pass"):
                        if not r_new_pass or r_new_pass != r_confirm_pass: st.error("❌ Passwords do not match/empty.")
                        else:
                            new_hash = db_update_password(r_user, r_new_pass)
                            st.session_state.reset_otp = None; st.session_state.reset_otp_email = ""; st.session_state.reset_otp_verified = False
                            st.success("✅ Password updated.")
                            st.code(f'"{r_user}": {{"password_hash": "{new_hash}"}}', language="json")

        with mode_tab2:
            st.caption("Each Google/Email account can be registered only once.")
            s_user = st.text_input("📧 Google / Email ID", key="signup_user").strip().lower()

            if is_account_already_registered(s_user):
                st.error("❌ This Google/Email account is already registered.")
            else:
                if st.button("📩 Send Sign Up OTP", key="btn_send_signup_otp"):
                    if not s_user or "@" not in s_user: st.error("❌ Valid email required.")
                    elif is_account_already_registered(s_user): st.error("❌ Already registered.")
                    else:
                        code = f"{random.randint(100000, 999999)}"
                        st.session_state.signup_otp, st.session_state.signup_otp_email, st.session_state.signup_otp_verified = code, s_user, False
                        try:
                            send_otp_email(s_user, code, purpose="Sign Up")
                            st.success("✅ OTP sent to email.")
                        except Exception as e: st.error(f"❌ Failed: {e}")

                if st.session_state.signup_otp and st.session_state.signup_otp_email == s_user:
                    s_otp_in = st.text_input("🔢 Enter OTP", key="signup_otp_input", max_chars=6)
                    if st.button("✅ Verify OTP", key="btn_verify_signup_otp"):
                        if s_otp_in.strip() == st.session_state.signup_otp:
                            st.session_state.signup_otp_verified = True
                            st.success("✅ OTP verified. Set password.")
                        else: st.error("❌ Invalid OTP.")

                if st.session_state.signup_otp_verified and st.session_state.signup_otp_email == s_user:
                    st.info("💡 നിങ്ങളുടെ അക്കൗണ്ടിൽ ഓട്ടോമാറ്റിക് ആയി Google Sheet ഉണ്ടാക്കപ്പെടും. ലിങ്കുകൾ നൽകേണ്ടതില്ല!")
                    s_pass = st.text_input("🔑 Create Password", type="password", key="signup_pass")
                    s_confirm = st.text_input("🔒 Confirm Password", type="password", key="signup_confirm")

                    if st.button("COMPLETE SIGN UP ✨", key="btn_signup"):
                        if is_account_already_registered(s_user): st.error("❌ Already registered.")
                        elif not s_pass or s_pass != s_confirm: st.error("❌ Passwords do not match/empty.")
                        else:
                            created_entry = db_create_user(s_user, s_pass) # URL നീക്കം ചെയ്തു
                            st.session_state.signup_otp = None; st.session_state.signup_otp_email = ""; st.session_state.signup_otp_verified = False
                            refresh_user_sheet_cache()
                            st.info("📌 Add this entry to `USERS_DATA` in Secrets:")
                            st.code(json.dumps(created_entry, indent=2), language="json")
                            set_persistent_login(s_user)
                            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- MAIN APP (ലോഗിൻ ചെയ്ത ശേഷം) ---
    active_csv = get_active_csv_url()
    df = load_data(active_csv)
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out

    st.sidebar.caption(f"👤 {format_display_name(st.session_state.user)}")

    with st.sidebar.expander("⚙️ Settings"):
        if st.button("🔄 Sync Data"):
            refresh_user_sheet_cache(); st.rerun()
        st.session_state.custom_alert_text = st.text_area("Alert Message", value=st.session_state.custom_alert_text)
        st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)

    menu = ["🏠 Dashboard", "💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤖 AI Chat"]
    page = st.sidebar.radio("Menu", menu)
    if st.sidebar.button("Logout"):
        clear_persistent_login(); st.rerun()

    # --- DASHBOARD ---
    if page == "🏠 Dashboard":
        if bal < st.session_state.low_limit:
            st.markdown(f'<div class="alert-banner">⚠️ Low Balance Alert: {st.session_state.custom_alert_text} (₹{bal:,.2f})!</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="balance-banner"><span style="font-size:22px; color:#E0B0FF;">AVAILABLE BALANCE</span><br><span style="font-size:50px; color:#FFD700; font-family: monospace;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)
        
        if not df.empty and 'Item' in df.columns:
            df['Cat'] = df['Item'].apply(categorize_item_label)
            cats = df.groupby('Cat')['Debit'].sum().to_dict()
            cols = st.columns(3)
            for idx, (c_name, c_amt) in enumerate(cats.items()):
                if c_amt > 0:
                    with cols[idx % 3]:
                        st.markdown(f'<div class="category-box"><span style="color:#aaa;">Total {c_name}</span><br><span style="font-size:24px; color:#FFF;">₹{c_amt:,.2f}</span></div>', unsafe_allow_html=True)

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
                    am = float(am_str.strip().replace(',', ''))
                    ok, msg = add_new_entry(it, am, cat, ty)
                    if ok:
                        st.success("Saved! ✅"); time.sleep(1); st.rerun()
                    else: st.error(msg)
                except Exception as e: st.error(f"Valid amount required. {e}")

    # --- REPORT & HISTORY ---
    elif (page == "📊 Report" or page == "🔍 History"):
        if df.empty: st.info("No data available yet.")
        else:
            df_rep = df.dropna(subset=['Date']).copy()
            df_rep['Month'] = df_rep['Date'].dt.strftime('%B %Y')
            months = df_rep.dropna(subset=['Month']).sort_values(by='Date', ascending=False)['Month'].unique()
            if len(months) > 0:
                sel_m = st.selectbox("Select Month", months)
                m_df = df_rep[df_rep['Month'] == sel_m].copy()
                m_deb, m_crd = m_df['Debit'].sum(), m_df['Credit'].sum()
                if page == "📊 Report":
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f'<div class="glass-card"><h3 style="color:#00FF00;">Credit</h3><h1 style="color:#00FF00;">₹{m_crd:,.2f}</h1></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="glass-card"><h3 style="color:#FF3131;">Expense</h3><h1 style="color:#FF3131;">₹{m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                    c3.markdown(f'<div class="glass-card"><h3 style="color:#FFD700;">Savings</h3><h1 style="color:#FFD700;">₹{m_crd - m_deb:,.2f}</h1></div>', unsafe_allow_html=True)
                    m_df['Cat'] = m_df['Item'].apply(lambda x: x.split(':')[0] if ':' in str(x) else 'Others')
                    st.plotly_chart(px.pie(m_df[m_df['Debit'] > 0], values='Debit', names='Cat', hole=0.4), use_container_width=True)
                
                clean_df = m_df.drop(columns=['Month'], errors='ignore')
                clean_df['Date'] = clean_df['Date'].dt.strftime('%d %b %Y')
                st.dataframe(clean_df.iloc[::-1], use_container_width=True)
                if page == "📊 Report":
                    pdf_bytes = create_pdf(clean_df)
                    if pdf_bytes: st.download_button("📄 Download PDF", pdf_bytes, f"Report_{sel_m}.pdf", "application/pdf")

    # --- AI CHAT ---
    elif page == "🤖 AI Chat":
        st.title("🤖 AI Agent")
        if st.session_state.ai_action_notice: st.success(st.session_state.ai_action_notice)
        if st.session_state.last_heard_text: st.caption(f"🎙️ Heard: {st.session_state.last_heard_text}")
        for h_msg in st.session_state.ai_chat_history[-8:]:
            with st.chat_message(h_msg["role"]): st.markdown(h_msg["content"])

        if st.session_state.pending_entry:
            p_item, p_amt = st.session_state.pending_entry["item"], st.session_state.pending_entry["amount"]
            st.info(f"**Confirm Entry:** {p_item} - ₹{p_amt}. Save?")
            col1, col2 = st.columns(2)
            if col1.button("Yes", key="save_entry_btn"):
                entry_data = st.session_state.pending_entry; st.session_state.pending_entry = None
                ok, status_msg = add_new_entry(entry_data['item'], entry_data['amount'], entry_data['category'], entry_data['type'], entry_data['date'])
                st.session_state.ai_action_notice = status_msg
                st.session_state.ai_chat_history.append({"role": "assistant", "content": status_msg})
                st.rerun()
            if col2.button("No", key="cancel_entry_btn"):
                st.session_state.pending_entry = None; st.session_state.ai_action_notice = "Cancelled."
                st.rerun()

        v_col, _ = st.columns([1.4, 2.6])
        with v_col:
            v_raw = speech_to_text(language='ml-IN', start_prompt="🎙️ Speak", stop_prompt="⏹️ Stop", just_once=True, key=f'ai_voice_{st.session_state.ai_chat_key_id}')
        prompt = st.chat_input("Type here...", key="ai_chat_box")

        final_prompt = None
        if v_raw and v_raw.strip() and v_raw.strip() != st.session_state.last_voice_text:
            st.session_state.last_voice_text = v_raw.strip(); st.session_state.last_heard_text = v_raw.strip()
            st.session_state.ai_chat_key_id += 1; final_prompt = v_raw.strip()
        elif prompt and prompt.strip():
            st.session_state.last_heard_text = prompt.strip(); final_prompt = prompt.strip()

        if final_prompt:
            clean_cmd = final_prompt.lower().strip()
            if clean_cmd in ["yes", "y", "അതെ", "ശരി"] and st.session_state.pending_entry:
                entry_data = st.session_state.pending_entry; st.session_state.pending_entry = None
                ok, status_msg = add_new_entry(entry_data['item'], entry_data['amount'], entry_data['category'], entry_data['type'], entry_data['date'])
                st.session_state.ai_action_notice = status_msg
                st.session_state.ai_chat_history.append({"role": "user", "content": final_prompt})
                st.session_state.ai_chat_history.append({"role": "assistant", "content": status_msg})
                st.rerun()
            elif clean_cmd in ["no", "n", "അല്ല", "വേണ്ട"] and st.session_state.pending_entry:
                st.session_state.pending_entry = None; st.session_state.ai_action_notice = "Cancelled."
                st.rerun()
            else:
                st.session_state.ai_action_notice = None
                with st.chat_message("user"): st.markdown(final_prompt)
                st.session_state.ai_chat_history.append({"role": "user", "content": final_prompt})
                with st.spinner("Processing..."):
                    try:
                        if not GROQ_API_KEY: st.error("GROQ_API_KEY missing.")
                        else:
                            full_ctx = build_full_financial_context(df, pd.DataFrame())
                            client = Groq(api_key=GROQ_API_KEY)
                            router_system = f"You are PAICHI AI. Context: {full_ctx} Reply ONLY with JSON: 1) Single entry: {{\"action\":\"single_entry\",\"item\":\"Food\",\"amount\":250,\"category\":\"Food\",\"type\":\"Debit\"}} 2) Answer: {{\"action\":\"answer\",\"reply\":\"...\"}}"
                            resp = client.chat.completions.create(model="openai/gpt-oss-120b", messages=[{"role": "system", "content": router_system}, {"role": "user", "content": final_prompt}], max_tokens=300)
                            raw_out = (resp.choices[0].message.content or "").strip()
                            json_match = re.search(r"\{.*\}", raw_out, re.DOTALL)
                            parsed_obj = json.loads(json_match.group(0)) if json_match else None

                            if isinstance(parsed_obj, dict) and parsed_obj.get("action") == "single_entry":
                                st.session_state.pending_entry = {
                                    "item": translate_to_english_label(str(parsed_obj.get("item", "Expense"))),
                                    "amount": float(parsed_obj.get("amount", 0) or 0),
                                    "category": translate_to_english_label(str(parsed_obj.get("category", "Others"))),
                                    "type": "Credit" if str(parsed_obj.get("type", "Debit")).lower() == "credit" else "Debit",
                                    "date": format_english_datetime()
                                }
                                st.rerun()
                            else:
                                reply_txt = str(parsed_obj.get("reply", "")).strip() if isinstance(parsed_obj, dict) and parsed_obj.get("reply") else raw_out
                                with st.chat_message("assistant"): st.markdown(reply_txt)
                                st.session_state.ai_chat_history.append({"role": "assistant", "content": reply_txt})
                    except Exception as e: st.error(f"Error: {e}")