import hashlib
import hmac
import json
import os
import random
import smtplib
import sqlite3
import time
from datetime import datetime
from email.message import EmailMessage

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------
# 1. Page Config & Secrets
# ---------------------------------------------------------
st.set_page_config(page_title="Paichi AI Expense Tracker", page_icon="💸", layout="centered")

MASTER_APPS_SCRIPT_URL = st.secrets.get("MASTER_APPS_SCRIPT_URL", os.getenv("MASTER_APPS_SCRIPT_URL", ""))
GOOGLE_FORM_URL = st.secrets.get("GOOGLE_FORM_URL", os.getenv("GOOGLE_FORM_URL", ""))
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
GROQ_MODEL = st.secrets.get("GROQ_MODEL", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
APP_SECRET_KEY = st.secrets.get("APP_SECRET_KEY", os.getenv("APP_SECRET_KEY", "paichi-default-secret-key"))

SMTP_HOST = st.secrets.get("SMTP_HOST", os.getenv("SMTP_HOST", "smtp.gmail.com"))
SMTP_PORT = int(st.secrets.get("SMTP_PORT", os.getenv("SMTP_PORT", 587)))
SMTP_USER = st.secrets.get("SMTP_USER", os.getenv("SMTP_USER", ""))
SMTP_PASS = st.secrets.get("SMTP_PASS", os.getenv("SMTP_PASS", ""))

# ---------------------------------------------------------
# 2. SQLite User Persistence (/tmp path for Streamlit Cloud)
# ---------------------------------------------------------
DB_PATH = "/tmp/paichi_users_v2.db"


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            created_at TEXT,
            last_login TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_user(email: str, name: str = ""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    now = datetime.utcnow().isoformat()
    cur = conn.execute("SELECT email FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.execute("UPDATE users SET last_login = ? WHERE email = ?", (now, email))
    else:
        conn.execute(
            "INSERT INTO users (email, name, created_at, last_login) VALUES (?, ?, ?, ?)",
            (email, name or email.split("@")[0], now, now),
        )
    conn.commit()
    conn.close()


def create_session_token(email: str) -> str:
    exp = int(time.time()) + 7 * 24 * 3600  # 7 days
    payload = f"{email}|{exp}"
    sig = hmac.new(APP_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{email}:{exp}:{sig}"


def verify_session_token(token: str):
    try:
        email, exp_str, sig = token.split(":")
        if int(exp_str) < int(time.time()):
            return None
        payload = f"{email}|{exp_str}"
        expected = hmac.new(APP_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected):
            return email
    except Exception:
        return None
    return None


def send_email_otp(to_email: str, otp_code: str) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = "Paichi Login OTP"
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg.set_content(f"Your Paichi verification code is: {otp_code}\n\nThis code expires in 10 minutes.")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception:
        return False


# ---------------------------------------------------------
# 3. Groq AI Agent Parser (No hardcoded keywords)
# ---------------------------------------------------------
def parse_message_with_ai(user_message: str) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in Secrets.")

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
You are an intelligent personal finance & expense AI agent. Today's date is {today}.
Analyze the user's message (which may be in English, Malayalam, or Manglish) and extract structured JSON.

Rules:
- Decide if this is an "expense" (spending or income) or a "debt" (money lent to someone or borrowed from someone).
- For "expense": infer a clean English item name, choose the best category (e.g., Food, Fish, Travel, Rent, Groceries, Bills, Shopping, Health, Salary, Others), and set "debit" (money spent) or "credit" (money received).
- For "debt": extract "party" (person's name), "type" ("Lent" or "Borrowed"), "amount", and "notes".
- Return ONLY valid JSON matching this schema:
{{
  "recordType": "expense" or "debt",
  "date": "{today}",
  "item": "string",
  "category": "string",
  "debit": 0,
  "credit": 0,
  "party": "string",
  "type": "Lent" or "Borrowed",
  "amount": 0,
  "notes": "string",
  "reply": "Short friendly confirmation in the user's language"
}}

User message: "{user_message}"
"""

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=20,
    )
    res.raise_for_status()
    content = res.json()["choices"][0]["message"]["content"]
    return json.loads(content)


# ---------------------------------------------------------
# 4. Master Google Sheet API Helpers
# ---------------------------------------------------------
def post_to_master_sheet(payload: dict) -> dict:
    if not MASTER_APPS_SCRIPT_URL:
        return {"ok": False, "error": "MASTER_APPS_SCRIPT_URL not configured in Secrets."}
    res = requests.post(MASTER_APPS_SCRIPT_URL, json=payload, timeout=15)
    return res.json()


def fetch_sheet_data(action: str = "expenses") -> pd.DataFrame:
    if not MASTER_APPS_SCRIPT_URL:
        return pd.DataFrame()
    try:
        res = requests.get(MASTER_APPS_SCRIPT_URL, params={"action": action}, timeout=15)
        data = res.json()
        rows = data.get(action, [])
        if len(rows) > 1:
            return pd.DataFrame(rows[1:], columns=rows[0])
    except Exception:
        pass
    return pd.DataFrame()


# ---------------------------------------------------------
# 5. Auth Flow
# ---------------------------------------------------------
init_db()

if "user_email" not in st.session_state:
    token_param = st.query_params.get("token", "")
    verified_email = verify_session_token(token_param) if token_param else None
    if verified_email:
        st.session_state.user_email = verified_email

if "user_email" not in st.session_state:
    st.title("💸 Paichi AI Expense Tracker")
    st.caption("Sign in with Email OTP to continue")

    email_input = st.text_input("Email Address", placeholder="you@example.com").strip().lower()
    if st.button("Send OTP", use_container_width=True):
        if "@" not in email_input:
            st.error("Please enter a valid email address.")
        else:
            otp = f"{random.randint(100000, 999999)}"
            st.session_state.pending_email = email_input
            st.session_state.pending_otp = otp
            sent = send_email_otp(email_input, otp)
            if sent:
                st.success(f"OTP sent to {email_input}")
            else:
                st.warning(f"SMTP not configured — Demo OTP: **{otp}**")

    if "pending_otp" in st.session_state:
        entered_otp = st.text_input("Enter 6-digit OTP", max_chars=6)
        if st.button("Verify & Login", type="primary", use_container_width=True):
            if entered_otp.strip() == st.session_state.pending_otp:
                user_email = st.session_state.pending_email
                save_user(user_email)
                st.session_state.user_email = user_email
                st.query_params["token"] = create_session_token(user_email)
                del st.session_state["pending_otp"]
                st.rerun()
            else:
                st.error("Invalid OTP. Please try again.")
    st.stop()


# ---------------------------------------------------------
# 6. Main App UI (Groq AI Chat + Summary + Form Link)
# ---------------------------------------------------------
st.title("💸 Paichi AI")
col_user, col_logout = st.columns([4, 1])
col_user.caption(f"Logged in as **{st.session_state.user_email}**")
if col_logout.button("Logout"):
    st.query_params.clear()
    del st.session_state["user_email"]
    st.rerun()

if GOOGLE_FORM_URL:
    st.link_button("📝 Open Quick Expense Google Form", GOOGLE_FORM_URL, use_container_width=True)

tab_chat, tab_expenses, tab_debts = st.tabs(["🤖 AI Chat", "📊 Expenses", "🤝 Debts"])

with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "നമസ്കാരം! ചെലവുകളോ വരവുകളോ കടം കൊടുത്തതോ ഇവിടെ ടൈപ്പ് ചെയ്യൂ (ഉദാ: *ചായയും കടിയും 25*, *ശമ്പളം 3000*, *രാഹുലിന് 500 കടം കൊടുത്തു*).",
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Type expense, income, or debt..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Groq AI analyzing & saving..."):
                try:
                    parsed = parse_message_with_ai(user_prompt)
                    res = post_to_master_sheet(parsed)
                    if res.get("ok"):
                        if parsed.get("recordType") == "debt":
                            confirm = (
                                f"✅ **Debt Saved:** {parsed.get('party')} ({parsed.get('type')}) — **{parsed.get('amount')}**\n\n"
                                f"{parsed.get('reply', '')}"
                            )
                        else:
                            confirm = (
                                f"✅ **Saved:** {parsed.get('item')} | Category: **{parsed.get('category')}** | "
                                f"Debit: **{parsed.get('debit')}** | Credit: **{parsed.get('credit')}**\n\n"
                                f"{parsed.get('reply', '')}"
                            )
                    else:
                        confirm = f"⚠️ Sheet error: {res.get('error')}"
                except Exception as exc:
                    confirm = f"❌ Error: {exc}"

                st.markdown(confirm)
                st.session_state.messages.append({"role": "assistant", "content": confirm})

with tab_expenses:
    if st.button("🔄 Refresh Expenses"):
        st.rerun()
    df_exp = fetch_sheet_data("expenses")
    if df_exp.empty:
        st.info("No expenses found yet.")
    else:
        for col in ["Debit", "Credit"]:
            if col in df_exp.columns:
                df_exp[col] = pd.to_numeric(df_exp[col], errors="coerce").fillna(0)
        c1, c2, c3 = st.columns(3)
        total_debit = df_exp["Debit"].sum() if "Debit" in df_exp.columns else 0
        total_credit = df_exp["Credit"].sum() if "Credit" in df_exp.columns else 0
        c1.metric("Total Debit", f"{total_debit:,.2f}")
        c2.metric("Total Credit", f"{total_credit:,.2f}")
        c3.metric("Balance", f"{(total_credit - total_debit):,.2f}")
        st.dataframe(df_exp, use_container_width=True, hide_index=True)

with tab_debts:
    if st.button("🔄 Refresh Debts"):
        st.rerun()
    df_debt = fetch_sheet_data("debts")
    if df_debt.empty:
        st.info("No debts recorded yet.")
    else:
        st.dataframe(df_debt, use_container_width=True, hide_index=True)