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
MASTER_PROVISION_URL = st.secrets.get("MASTER_PROVISION_URL", st.secrets.get("PROVISION_WEB_APP_URL", ""))
DEFAULT_WEB_APP_URL = st.secrets.get("SHEET_WEB_APP_URL", st.secrets.get("GOOGLE_SHEET_WEB_APP_URL", ""))
DEFAULT_CSV_URL = st.secrets.get("SHEET_CSV_URL", st.secrets.get("GOOGLE_SHEET_CSV_URL", ""))
DB_FILE = "paichi_users_v2.db"

# --- TIMEZONE SETUP (GST - Dubai Time) ---
GST = timezone(timedelta(hours=4))

st_autorefresh(interval=120000, key="auto_refresh")

# ============================================
# 🗄️ DATABASE + ST.SECRETS USER STORE
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
    c.execute("PRAGMA table_info(users)")
    existing_cols = [col[1] for col in c.fetchall()]
    if "sheet_url" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN sheet_url TEXT DEFAULT ''")
    if "csv_url" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN csv_url TEXT DEFAULT ''")
    if "links_locked" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN links_locked INTEGER DEFAULT 0")
    if "account_locked" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN account_locked INTEGER DEFAULT 1")
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
    s_rec = secrets_users.get(u)
    if isinstance(s_rec, dict) and s_rec.get("password_hash"):
        sheet_val = (s_rec.get("sheet_url") or "").strip()
        csv_val = (s_rec.get("csv_url") or "").strip()
        locked_val = 1 if (sheet_val or csv_val or s_rec.get("links_locked")) else 0
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO users (username, password_hash, sheet_url, csv_url, links_locked, account_locked)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(username) DO UPDATE SET
                password_hash = excluded.password_hash,
                sheet_url = CASE WHEN users.sheet_url != '' THEN users.sheet_url ELSE excluded.sheet_url END,
                csv_url = CASE WHEN users.csv_url != '' THEN users.csv_url ELSE excluded.csv_url END,
                links_locked = CASE WHEN users.links_locked = 1 OR excluded.links_locked = 1 THEN 1 ELSE 0 END,
                account_locked = 1
            """,
            (u, s_rec.get("password_hash", ""), sheet_val, csv_val, locked_val)
        )
        conn.commit()
        c.execute("SELECT username, password_hash, sheet_url, csv_url, links_locked, account_locked FROM users WHERE username = ?", (u,))
        row = c.fetchone()
        conn.close()
        if row:
            s_url_db = row[2] or ""
            c_url_db = row[3] or ""
            is_locked = 1 if (s_url_db or c_url_db or int(row[4] or 0) == 1) else 0
            return {
                "username": row[0],
                "password_hash": row[1],
                "sheet_url": s_url_db,
                "csv_url": c_url_db,
                "links_locked": is_locked,
                "account_locked": int(row[5] if row[5] is not None else 1)
            }

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, password_hash, sheet_url, csv_url, links_locked, account_locked FROM users WHERE username = ?", (u,))
    row = c.fetchone()
    conn.close()
    if row:
        s_url_db = row[2] or ""
        c_url_db = row[3] or ""
        is_locked = 1 if (s_url_db or c_url_db or int(row[4] or 0) == 1) else 0
        return {
            "username": row[0],
            "password_hash": row[1],
            "sheet_url": s_url_db,
            "csv_url": c_url_db,
            "links_locked": is_locked,
            "account_locked": int(row[5] if row[5] is not None else 1)
        }
    return None

def db_create_user(username: str, password: str, sheet_url: str = "", csv_url: str = ""):
    init_db()
    u = username.strip().lower()
    if is_account_already_registered(u):
        raise ValueError("This Google/email account is already registered and locked.")
    pwd_hash = hash_password(password)
    s_url = (sheet_url or "").strip()
    c_url = (csv_url or "").strip()
    locked_flag = 1 if (s_url or c_url) else 0
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, sheet_url, csv_url, links_locked, account_locked) VALUES (?, ?, ?, ?, ?, 1)",
        (u, pwd_hash, s_url, c_url, locked_flag)
    )
    conn.commit()
    conn.close()
    return {
        u: {
            "password_hash": pwd_hash,
            "sheet_url": s_url,
            "csv_url": c_url,
            "links_locked": bool(locked_flag),
            "account_locked": True
        }
    }

def db_bind_links_once(username: str, sheet_url: str = "", csv_url: str = ""):
    init_db()
    u = username.strip().lower()
    existing = db_get_user(u)
    if not existing:
        return False, "Account not found."
    if existing.get("links_locked") == 1 or existing.get("sheet_url") or existing.get("csv_url"):
        return False, "Links are already submitted and permanently locked."

    s_url = (sheet_url or "").strip()
    c_url = (csv_url or "").strip()
    if not s_url and not c_url:
        return False, "Enter at least one link (Web App URL or CSV URL)."

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET sheet_url = ?, csv_url = ?, links_locked = 1 WHERE username = ?",
        (s_url, c_url, u)
    )
    conn.commit()
    conn.close()
    return True, "Links submitted and permanently locked."

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
# ⚡ AUTO PROVISIONING UPON LOGIN
# ============================================
def provision_user_sheet_on_login(username: str):
    u = (username or "").strip().lower()
    if not u:
        return

    prof = db_get_user(u) or {}
    existing_sheet = (prof.get("sheet_url") or "").strip()
    existing_csv = (prof.get("csv_url") or "").strip()

    if existing_sheet or existing_csv:
        st.session_state[f"cached_sheet_{u}"] = existing_sheet
        st.session_state[f"cached_csv_{u}"] = existing_csv
        return

    prov_url = (st.secrets.get("MASTER_PROVISION_URL", MASTER_PROVISION_URL) or "").strip()
    def_sheet = (st.secrets.get("SHEET_WEB_APP_URL", st.secrets.get("GOOGLE_SHEET_WEB_APP_URL", DEFAULT_WEB_APP_URL)) or "").strip()
    def_csv = (st.secrets.get("SHEET_CSV_URL", st.secrets.get("GOOGLE_SHEET_CSV_URL", DEFAULT_CSV_URL)) or "").strip()

    resolved_sheet = ""
    resolved_csv = ""

    if prov_url:
        try:
            resp = requests.post(
                prov_url,
                json={"action": "provision_user", "user": u, "email": u},
                timeout=8
            )
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if isinstance(data, dict):
                        resolved_sheet = (data.get("sheet_url") or data.get("web_app_url") or data.get("url") or "").strip()
                        resolved_csv = (data.get("csv_url") or "").strip()
                except Exception:
                    txt = (resp.text or "").strip()
                    if txt.startswith("http"):
                        resolved_sheet = txt
        except Exception:
            pass

    if not resolved_sheet and def_sheet:
        resolved_sheet = def_sheet
    if not resolved_csv and def_csv:
        resolved_csv = def_csv

    if resolved_sheet or resolved_csv:
        db_bind_links_once(u, resolved_sheet, resolved_csv)
        st.session_state[f"cached_sheet_{u}"] = resolved_sheet
        st.session_state[f"cached_csv_{u}"] = resolved_csv

# ============================================
# 📧 FREE EMAIL OTP HELPER (BREVO -> RESEND -> SMTP)
# ============================================
def send_otp_email(to_email: str, otp_code: str, purpose: str = "OTP Verification") -> bool:
    brevo_key = (st.secrets.get("BREVO_API_KEY", BREVO_API_KEY) or "").strip()
    brevo_sender = (st.secrets.get("BREVO_SENDER_EMAIL", BREVO_SENDER_EMAIL) or "").strip()
    resend_key = (st.secrets.get("RESEND_API_KEY", RESEND_API_KEY) or "").strip()
    from_email = (st.secrets.get("OTP_FROM_EMAIL", OTP_FROM_EMAIL) or "onboarding@resend.dev").strip()

    body_text = (
        f"Hello,\n\n"
        f"Your 6-digit OTP code for PAICHI EXPENSES ({purpose}) is:\n\n"
        f"OTP: {otp_code}\n\n"
        f"Please do not share this code with anyone."
    )

    if brevo_key and brevo_sender:
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": brevo_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "sender": {"name": "PAICHI EXPENSES", "email": brevo_sender},
                "to": [{"email": to_email}],
                "subject": f"PAICHI EXPENSES - {purpose} OTP",
                "textContent": body_text
            },
            timeout=15
        )
        if resp.status_code in (200, 201, 202):
            return True
        raise RuntimeError(f"Brevo API Error ({resp.status_code}): {resp.text}")

    if resend_key:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": from_email,
                "to": [to_email],
                "subject": f"PAICHI EXPENSES - {purpose} OTP",
                "text": body_text
            },
            timeout=15
        )
        if resp.status_code in (200, 201):
            return True
        raise RuntimeError(f"Resend API Error ({resp.status_code}): {resp.text}")

    sender = (st.secrets.get("SMTP_EMAIL", SMTP_EMAIL) or "").strip()
    app_pwd = (st.secrets.get("SMTP_APP_PASSWORD", SMTP_APP_PASSWORD) or "").replace(" ", "").strip()

    if not sender or not app_pwd:
        raise ValueError("BREVO_API_KEY / BREVO_SENDER_EMAIL, RESEND_API_KEY, or SMTP_EMAIL / SMTP_APP_PASSWORD is not configured in Secrets.")

    msg = EmailMessage()
    msg["Subject"] = f"PAICHI EXPENSES - {purpose} OTP"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body_text)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender, app_pwd)
            server.send_message(msg)
        return True
    except Exception as ssl_err:
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender, app_pwd)
                server.send_message(msg)
            return True
        except Exception as tls_err:
            raise RuntimeError(f"SSL (465) Error: {ssl_err} | TLS (587) Error: {tls_err}")

# ============================================
# 🔐 SIGNED TOKEN SESSION (Query Params)
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
        if hmac.compare_digest(sig, expected_sig):
            return u
    except Exception:
        pass
    return None

def restore_session_from_url():
    if not st.session_state.get("auth", False):
        token = st.query_params.get("session", "")
        if token:
            valid_user = verify_session_token(token)
            if valid_user and db_get_user(valid_user):
                st.session_state.auth = True
                st.session_state.user = valid_user
                provision_user_sheet_on_login(valid_user)

def set_persistent_login(username: str):
    u = username.strip().lower()
    st.session_state.auth = True
    st.session_state.user = u
    st.query_params["session"] = create_session_token(u)
    provision_user_sheet_on_login(u)

def clear_persistent_login():
    u = (st.session_state.get("user", "") or "").strip().lower()
    st.session_state.auth = False
    st.session_state.user = ""
    st.session_state.pop(f"cached_sheet_{u}", None)
    st.session_state.pop(f"cached_csv_{u}", None)
    if "session" in st.query_params:
        del st.query_params["session"]

# ============================================
# 🎨 3D GLASSMORPHISM CSS
# ============================================
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background-image: linear-gradient(rgba(10, 10, 25, 0.85), rgba(10, 10, 25, 0.95)), url("{BG_IMAGE_URL}"); 
        background-size: cover; background-attachment: fixed; background-position: center;
    }}
    [data-testid="stSidebar"] {{ 
        background: rgba(20, 20, 35, 0.6) !important; backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }}
    .stButton>button {{ 
        background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border-radius: 12px; 
        font-weight: bold; width: 100%; border: none; padding: 10px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4), inset 0 -3px 0 rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); margin-bottom: 25px; text-align: center; }}
    .balance-banner {{ background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02)); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; border-left: 8px solid #FFD700; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .category-box {{ background: rgba(0, 0, 0, 0.5); padding: 20px; border-radius: 15px; text-align: center; border-bottom: 4px solid #FFD700; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
    .category-box:hover {{ transform: scale(1.03); }}
    .alert-banner {{ background: linear-gradient(90deg, #ff4d4d, #cc0000); color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(255, 77, 77, 0.4); }}
    .login-card {{ background: rgba(20, 20, 35, 0.8); backdrop-filter: blur(20px); padding: 40px; border-radius: 20px; max-width: 450px; margin: auto; margin-top: 80px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 15px 35px rgba(0,0,0,0.6); }}
    h1, h2, h3, p, label {{ color: #FFFFFF !important; font-weight: bold !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
    [data-testid="stChatMessage"] {{ background: rgba(32, 44, 51, 0.9) !important; border-radius: 15px !important; padding: 15px !important; margin-bottom: 10px !important; border: 1px solid rgba(255,255,255,0.05) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
    [data-testid="stChatInput"] {{ background-color: rgba(42, 57, 66, 0.92) !important; border-radius: 28px !important; border: 1px solid rgba(255,255,255,0.18) !important; padding: 4px 8px !important; }}
    [data-testid="stChatInput"] textarea {{ color: white !important; }}
    input, textarea, select {{ color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; background-color: rgba(0, 0, 0, 0.5) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 8px !important; }}
    ::placeholder {{ color: #AAAAAA !important; }}
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