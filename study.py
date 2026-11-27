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
st.set_page_config(page_title="PAICHI EXPENSES & AI AGENT", layout="wide")

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

NOTES_DIR = "personal_notes"
os.makedirs(NOTES_DIR, exist_ok=True)

# --- TIMEZONE SETUP (GST - Dubai Time) ---
GST = timezone(timedelta(hours=4))
st_autorefresh(interval=60000, key="auto_refresh")

# ============================================
# 🗄️ DATABASE (Users + Personal Agent)
# ============================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # യൂസർ ടേബിൾ
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
    # പേഴ്സണൽ ലോഗ്സ് ടേബിൾ
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

def load_secrets_users() -> dict:
    raw_users = st.secrets.get("USERS_DATA", {})
    if isinstance(raw_users, str):
        try: return json.loads(raw_users)
        except Exception: return {}
    return dict(raw_users) if isinstance(raw_users, dict) else {}

def is_account_already_registered(username: str) -> bool:
    u = (username or "").strip().lower()
    if not u: return False
    if u in load_secrets_users(): return True
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (u,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

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
    if is_account_already_registered(u): raise ValueError("Already registered.")
    pwd_hash = hash_password(password)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash, sheet_url, csv_url, links_locked, account_locked) VALUES (?, ?, ?, ?, ?, 1)", (u, pwd_hash, sheet_url, csv_url, 1 if (sheet_url or csv_url) else 0))
    conn.commit()
    conn.close()
    return {u: {"password_hash": pwd_hash, "sheet_url": sheet_url, "csv_url": csv_url, "links_locked": True, "account_locked": True}}

# ============================================
# 🧠 PERSONAL AI AGENT HELPERS & TOOLS
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
        return "[Notes] ലഭ്യമായ നോട്ടുകൾ: " + (", ".join(files) if files else "ഒന്നുമില്ല")
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
    return f"[Task] '{item_title}' ({time_or_priority}) വിജയകരമായി രേഖപ്പെടുത്തി."

# ============================================
# 🔐 AUTH & SESSION FUNCTIONS
# ============================================
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
# 🎨 CSS & UI SETUP
# ============================================
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-image: linear-gradient(rgba(10, 10, 25, 0.85), rgba(10, 10, 25, 0.95)), url("{BG_IMAGE_URL}"); background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background: rgba(20, 20, 35, 0.6) !important; backdrop-filter: blur(15px); }}
    .stButton>button {{ background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; border-radius: 12px; font-weight: bold; }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px; text-align: center; margin-bottom: 25px; }}
    .balance-banner {{ background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02)); padding: 30px; border-radius: 20px; border-left: 8px solid #FFD700; text-align: center; margin-bottom: 25px; }}
    .category-box {{ background: rgba(0, 0, 0, 0.5); padding: 20px; border-radius: 15px; border-bottom: 4px solid #FFD700; text-align: center; }}
    .login-card {{ background: rgba(20, 20, 35, 0.8); padding: 40px; border-radius: 20px; max-width: 450px; margin: auto; margin-top: 80px; }}
    h1, h2, h3, p, label {{ color: #FFFFFF !important; font-weight: bold !important; }}
    input, textarea {{ color: #FFFFFF !important; background-color: rgba(0, 0, 0, 0.5) !important; }}
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth, st.session_state.user = False, ""
if 'custom_alert_text' not in st.session_state: st.session_state.custom_alert_text = "Low balance alert"
if 'low_limit' not in st.session_state: st.session_state.low_limit = 6000
if "ai_chat_key_id" not in st.session_state: st.session_state.ai_chat_key_id = 0
if "last_voice_text" not in st.session_state: st.session_state.last_voice_text = ""
if "last_heard_text" not in st.session_state: st.session_state.last_heard_text = ""
if "ai_chat_history" not in st.session_state: st.session_state.ai_chat_history = []
if "buddy_messages" not in st.session_state: st.session_state.buddy_messages = []

restore_session_from_url()

# --- HELPER FUNCTIONS ---
def format_display_name(username: str) -> str:
    return username.split("@")[0] if "@" in username else username

def format_english_datetime(dt_value=None) -> str:
    dt_obj = datetime.now(GST) if dt_value is None else pd.to_datetime(dt_value)
    return dt_obj.strftime("%d %b %Y %H:%M:%S")

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

def categorize_item_label(item_str: str) -> str:
    low = str(item_str or "").lower()
    if any(w in low for w in ["food", "tea", "coffee", "ഭക്ഷണം", "ചായ"]): return "Food"
    elif any(w in low for w in ["shop", "grocery", "കട"]): return "Shop"
    elif any(w in low for w in ["fish", "meat", "മീൻ", "ചിക്കൻ"]): return "Fish"
    elif any(w in low for w in ["travel", "petrol", "യാത്ര", "പെട്രോൾ"]): return "Travel"
    elif any(w in low for w in ["rent", "വാടക"]): return "Rent"
    return "Others"

def get_active_web_app_url() -> str:
    prof = db_get_user(st.session_state.get("user", ""))
    return prof["sheet_url"].strip() if prof and prof.get("sheet_url") else ""

def get_active_csv_url() -> str:
    prof = db_get_user(st.session_state.get("user", ""))
    return prof["csv_url"].strip() if prof and prof.get("csv_url") else ""

def refresh_user_sheet_cache():
    st.cache_data.clear()

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
    except Exception:
        return pd.DataFrame(columns=['Date', 'Item', 'Debit', 'Credit'])

def add_new_entry(item, amount, category="Others", type="Debit", entry_date=None):
    try:
        target_url = get_active_web_app_url()
        eng_item = translate_to_english_label(item, "Expense")
        payload = {"item": eng_item, "amount": amount, "category": category, "type": type, "date": format_english_datetime(entry_date)}
        if target_url:
            requests.post(target_url, json=payload, timeout=10)
            refresh_user_sheet_cache()
        return True, f"Saved: {eng_item} - ₹{amount}"
    except Exception as e:
        return False, f"Failed: {e}"

# --- 🔒 LOGIN & SIGN UP ---
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
            s_pass = st.text_input("🔑 Password", type="password", key="signup_pass")
            if st.button("SIGN UP ✨"):
                if not s_user or not s_pass: st.error("Fill all fields.")
                elif is_account_already_registered(s_user): st.error("Already registered.")
                else:
                    db_create_user(s_user, s_pass)
                    set_persistent_login(s_user)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APP ---
else:
    active_csv = get_active_csv_url()
    df = load_data(active_csv)
    t_in, t_out = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = t_in - t_out

    st.sidebar.caption(f"👤 {format_display_name(st.session_state.user)}")
    
    menu = ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🧠 Personal AI Buddy", "🤖 AI Chat"]
    page = st.sidebar.radio("Menu", menu)

    if st.sidebar.button("Logout"):
        clear_persistent_login()
        st.rerun()

    # --- DASHBOARD ---
    if page == "🏠 Dashboard":
        st.markdown(f'<div class="balance-banner"><span style="font-size:22px; color:#E0B0FF;">AVAILABLE BALANCE</span><br><span style="font-size:50px; color:#FFD700;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h2 style="color:#00FF00;">Credit: ₹{t_in:,.2f}</h2><h2 style="color:#FF3131;">Debit: ₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)

    # --- ADD ENTRY ---
    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description")
            am_str = st.text_input("Amount")
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    ok, msg = add_new_entry(it, float(am_str), cat, ty)
                    if ok: st.success("Saved!"); time.sleep(1); st.rerun()
                    else: st.error(msg)
                except Exception as e: st.error(f"Error: {e}")

    # --- PERSONAL AI BUDDY (Notes & Tasks) ---
    elif page == "🧠 Personal AI Buddy":
        st.title("🧠 Personal Notes & Tasks")
        st.write("ഇവിടെ നിങ്ങളുടെ നോട്ടുകളും ടാസ്കുകളും കാണാം. നിർദ്ദേശങ്ങൾ AI ചാറ്റിൽ നൽകാം.")
        
        st.subheader("📓 നോട്ടുകൾ")
        files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".md"))
        if files:
            chosen = st.selectbox("തിരഞ്ഞെടുക്കുക", files)
            with open(os.path.join(NOTES_DIR, chosen), "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("നോട്ടുകൾ ഒന്നുമില്ല.")

        st.divider()
        st.subheader("📌 ലോഗുകൾ")
        conn = sqlite3.connect(DB_FILE)
        logs_df = pd.read_sql_query("SELECT created_at AS Time, category AS Category, title AS Title, details AS Details FROM personal_logs ORDER BY id DESC LIMIT 10", conn)
        conn.close()
        if not logs_df.empty: st.dataframe(logs_df, use_container_width=True, hide_index=True)
        else: st.info("ലോഗുകൾ ഒന്നുമില്ല.")

    # --- AI CHAT (Expenses + Notes + Tasks) ---
    elif page == "🤖 AI Chat":
        st.title("🤖 Agentic AI Chat")
        
        for h_msg in st.session_state.ai_chat_history[-8:]:
            with st.chat_message(h_msg["role"]): st.markdown(h_msg["content"])

        prompt = st.chat_input("ഉദാ: 'ചായയ്ക്ക് 10 രൂപ', 'ഒരു നോട്ട് എഴുതൂ', 'ടാസ്ക് ചേർക്കൂ'...")
        
        if prompt:
            with st.chat_message("user"): st.markdown(prompt)
            st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
            
            with st.spinner("ഏജന്റ് ചിന്തിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    # AI-ക്ക് നൽകുന്ന നിർദ്ദേശങ്ങൾ (Tools)
                    sys_prompt = """
                    You are a multi-tasking AI Agent. Reply ONLY with JSON.
                    1. For expenses: {"action":"expense", "item":"Name", "amount":100, "category":"Food", "type":"Debit"}
                    2. For notes: {"action":"note", "note_title":"Title", "content":"Content"}
                    3. For tasks: {"action":"task", "item_title":"Task", "time_or_priority":"Time"}
                    4. For chat: {"action":"chat", "reply":"Your response"}
                    """
                    
                    resp = client.chat.completions.create(
                        model="openai/gpt-oss-120b", 
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}], 
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