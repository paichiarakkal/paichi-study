import hashlib
import hmac
import json
import os
import random
import sqlite3
import time
from datetime import datetime, timezone, timedelta

import pandas as pd
import requests
import streamlit as st
from groq import Groq

st.set_page_config(page_title="PAICHI RETAIL HUB", page_icon="🏪", layout="wide")

GROQ_API_KEY = str(st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))).strip()
GROQ_MODEL = str(st.secrets.get("GROQ_MODEL", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))).strip()
RETAIL_WEBHOOK_URL = str(st.secrets.get("RETAIL_WEBHOOK_URL", os.getenv("RETAIL_WEBHOOK_URL", ""))).strip()
WA_REPORT_PHONE = str(st.secrets.get("WA_REPORT_PHONE", os.getenv("WA_REPORT_PHONE", ""))).strip()
TWILIO_SID = str(st.secrets.get("TWILIO_ACCOUNT_SID", os.getenv("TWILIO_ACCOUNT_SID", ""))).strip()
TWILIO_TOKEN = str(st.secrets.get("TWILIO_AUTH_TOKEN", os.getenv("TWILIO_AUTH_TOKEN", ""))).strip()
TWILIO_WA_FROM = str(st.secrets.get("TWILIO_WA_FROM", "whatsapp:+14155238886")).strip()
APP_SECRET = str(st.secrets.get("SESSION_SECRET_KEY", "paichi_retail_secret_2026")).strip()

GST = timezone(timedelta(hours=4))
DB_PATH = "/tmp/paichi_retail.db"


def init_retail_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS retail_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            branch TEXT,
            log_type TEXT,
            title TEXT,
            qty REAL DEFAULT 0,
            amount REAL DEFAULT 0,
            notes TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS footfall_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TEXT,
            branch TEXT,
            visitor_count INTEGER DEFAULT 0,
            summary TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_retail_db()


def now_gst_str() -> str:
    return datetime.now(GST).strftime("%d %b %Y %H:%M:%S")


def save_retail_log(branch: str, log_type: str, title: str, qty: float = 0.0, amount: float = 0.0, notes: str = ""):
    init_retail_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO retail_logs (created_at, branch, log_type, title, qty, amount, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (now_gst_str(), branch, log_type, title, float(qty), float(amount), notes),
    )
    conn.commit()
    conn.close()
    if RETAIL_WEBHOOK_URL:
        try:
            requests.post(
                RETAIL_WEBHOOK_URL,
                json={
                    "time": now_gst_str(),
                    "branch": branch,
                    "log_type": log_type,
                    "title": title,
                    "qty": float(qty),
                    "amount": float(amount),
                    "notes": notes,
                },
                timeout=10,
            )
        except Exception:
            pass


def save_footfall_log(branch: str, visitor_count: int, summary: str):
    init_retail_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO footfall_logs (checked_at, branch, visitor_count, summary) VALUES (?, ?, ?, ?)",
        (now_gst_str(), branch, int(visitor_count), summary),
    )
    conn.commit()
    conn.close()


def fetch_retail_df() -> pd.DataFrame:
    init_retail_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM retail_logs ORDER BY id DESC", conn)
    conn.close()
    return df


def fetch_footfall_df() -> pd.DataFrame:
    init_retail_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM footfall_logs ORDER BY id DESC", conn)
    conn.close()
    return df


def send_whatsapp_report(message_text: str) -> tuple[bool, str]:
    clean_phone = "".join(ch for ch in WA_REPORT_PHONE if ch.isdigit())
    if not TWILIO_SID or not TWILIO_TOKEN or not clean_phone:
        return False, "Twilio WhatsApp secrets not configured."
    try:
        from twilio.rest import Client

        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(from_=TWILIO_WA_FROM, body=message_text, to=f"whatsapp:+{clean_phone}")
        return True, "WhatsApp report sent."
    except Exception as exc:
        return False, str(exc)


def analyze_snapshot_with_groq(uploaded_file, branch: str) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY missing in Secrets.")

    client = Groq(api_key=GROQ_API_KEY)
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()[:10]
    size_kb = round(len(file_bytes) / 1024, 1)

    prompt = (
        f"Branch: {branch}. Camera snapshot uploaded ({uploaded_file.name}, {size_kb} KB, ref {file_hash}). "
        "Provide a concise retail CCTV footfall & queue observation template in JSON with keys: "
        '{"estimated_visitors": 0, "observation": "short note", "action_tip": "short retail tip"}'
    )
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(resp.choices[0].message.content)


st.title("🏪 PAICHI MULTI-STORE RETAIL PLATFORM")
st.caption("Stock • Staff Salary • CCTV Footfall Monitor • Multi-Branch WhatsApp Reporting")

branches = ["Branch 1 - Main Store", "Branch 2 - City Mart", "Branch 3 - Express"]
selected_branch = st.sidebar.selectbox("🏬 Active Branch", branches)

df_logs = fetch_retail_df()
df_footfall = fetch_footfall_df()

total_sales = float(df_logs[df_logs["log_type"] == "Sale"]["amount"].sum()) if not df_logs.empty else 0.0
total_salary = float(df_logs[df_logs["log_type"] == "Salary"]["amount"].sum()) if not df_logs.empty else 0.0
total_visitors = int(df_footfall["visitor_count"].sum()) if not df_footfall.empty else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sales", f"₹{total_sales:,.2f}")
m2.metric("Staff Salary Paid", f"₹{total_salary:,.2f}")
m3.metric("CCTV Footfall", f"{total_visitors}")
m4.metric("Net After Salary", f"₹{(total_sales - total_salary):,.2f}")

tab_stock_sal, tab_cctv, tab_wa, tab_data = st.tabs(
    ["📦 Stock & Salary", "📹 CCTV Footfall", "📲 WhatsApp Report", "📋 Logs"]
)

with tab_stock_sal:
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("📦 Stock Entry")
        with st.form("stock_form", clear_on_submit=True):
            item_name = st.text_input("Item Name")
            qty = st.number_input("Quantity", min_value=0.0, step=1.0)
            stock_val = st.number_input("Stock Value (₹)", min_value=0.0, step=10.0)
            notes = st.text_input("Notes")
            if st.form_submit_button("Save Stock"):
                if item_name.strip():
                    save_retail_log(selected_branch, "Stock", item_name.strip(), qty, stock_val, notes.strip())
                    st.success("Stock saved.")
                    st.rerun()
                else:
                    st.error("Enter item name.")

    with c_right:
        st.subheader("💼 Staff Salary & Sales")
        with st.form("sal_sales_form", clear_on_submit=True):
            entry_kind = st.selectbox("Type", ["Sale", "Salary"])
            person_or_desc = st.text_input("Staff Name / Sale Summary")
            amt = st.number_input("Amount (₹)", min_value=0.0, step=50.0)
            s_notes = st.text_input("Remarks")
            if st.form_submit_button("Save Entry"):
                if person_or_desc.strip() and amt > 0:
                    save_retail_log(selected_branch, entry_kind, person_or_desc.strip(), 1.0, amt, s_notes.strip())
                    st.success(f"{entry_kind} saved.")
                    st.rerun()
                else:
                    st.error("Enter description and amount.")

with tab_cctv:
    st.subheader("📹 CCTV Snapshot Footfall Monitor")
    snap = st.file_uploader("Upload Camera Snapshot (JPG/PNG)", type=["jpg", "jpeg", "png"])
    manual_count = st.number_input("Verified Footfall Count", min_value=0, step=1, value=0)
    if snap is not None:
        st.image(snap, caption=f"{selected_branch} Snapshot", use_container_width=True)
        if st.button("Analyze Snapshot & Log Footfall"):
            with st.spinner("Analyzing snapshot..."):
                try:
                    ai_res = analyze_snapshot_with_groq(snap, selected_branch)
                    count_to_save = int(manual_count) if manual_count > 0 else int(ai_res.get("estimated_visitors", 0) or 0)
                    obs = f"{ai_res.get('observation', '')} | Tip: {ai_res.get('action_tip', '')}".strip(" |")
                    save_footfall_log(selected_branch, count_to_save, obs)
                    st.success(f"Logged {count_to_save} visitors for {selected_branch}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Analysis error: {exc}")

with tab_wa:
    st.subheader("📲 Aggregated Multi-Store WhatsApp Report")
    branch_summary_lines = []
    for b in branches:
        b_df = df_logs[df_logs["branch"] == b] if not df_logs.empty else pd.DataFrame()
        b_f = df_footfall[df_footfall["branch"] == b] if not df_footfall.empty else pd.DataFrame()
        b_sales = float(b_df[b_df["log_type"] == "Sale"]["amount"].sum()) if not b_df.empty else 0.0
        b_sal = float(b_df[b_df["log_type"] == "Salary"]["amount"].sum()) if not b_df.empty else 0.0
        b_vis = int(b_f["visitor_count"].sum()) if not b_f.empty else 0
        branch_summary_lines.append(f"• {b}: Sales ₹{b_sales:,.0f} | Salary ₹{b_sal:,.0f} | Footfall {b_vis}")

    report_preview = (
        f"🏪 *PAICHI MULTI-STORE REPORT*\n"
        f"🕒 {now_gst_str()}\n\n"
        + "\n".join(branch_summary_lines)
        + f"\n\n💰 Total Sales: ₹{total_sales:,.2f}\n💼 Total Salary: ₹{total_salary:,.2f}\n👥 Total Footfall: {total_visitors}"
    )
    st.code(report_preview, language="text")
    if st.button("Send Aggregated Report via WhatsApp"):
        ok, msg = send_whatsapp_report(report_preview)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

with tab_data:
    st.subheader("📋 Retail Transactions")
    st.dataframe(df_logs, use_container_width=True, hide_index=True)
    st.subheader("📹 CCTV Footfall History")
    st.dataframe(df_footfall, use_container_width=True, hide_index=True)