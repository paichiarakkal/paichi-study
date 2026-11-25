import requests
import sqlite3
import pandas as pd
import random
from datetime import datetime
import streamlit as st

MASTER_PROVISION_URL = st.secrets.get(
    "MASTER_PROVISION_URL",
    st.secrets.get("SHEET_WEB_APP_URL", st.secrets.get("GOOGLE_SHEET_WEB_APP_URL", ""))
)

def ensure_user_sheet_columns():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    cols = [col[1] for col in c.fetchall()]
    if "debt_csv_url" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN debt_csv_url TEXT DEFAULT ''")
    conn.commit()
    conn.close()

ensure_user_sheet_columns()

def auto_provision_user_sheet(user_email: str, force_refresh: bool = False) -> dict:
    """
    OTP / Login കഴിഞ്ഞ് യൂസർ അകത്ത് കയറുമ്പോൾ തന്നെ ആ ജിമെയിലിനായി
    Google Sheet ഓട്ടോമാറ്റിക്കായി ക്രിയേറ്റ് ചെയ്ത് / കണ്ടെത്തി DB-യിൽ സേവ് ചെയ്യുന്നു.
    """
    u = (user_email or "").strip().lower()
    if not u:
        return {}

    init_db()
    ensure_user_sheet_columns()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT sheet_url, csv_url, debt_csv_url FROM users WHERE username = ?", (u,))
    row = c.fetchone()

    existing_sheet_url = (row[0] or "").strip() if row else ""
    existing_csv_url = (row[1] or "").strip() if row else ""
    existing_debt_csv = (row[2] or "").strip() if row else ""

    if existing_csv_url and not force_refresh:
        conn.close()
        return {
            "sheet_url": existing_sheet_url,
            "csv_url": existing_csv_url,
            "debt_csv_url": existing_debt_csv or existing_csv_url
        }

    provision_endpoint = (MASTER_PROVISION_URL or "").strip()
    if not provision_endpoint:
        conn.close()
        return {
            "sheet_url": existing_sheet_url,
            "csv_url": existing_csv_url,
            "debt_csv_url": existing_debt_csv or existing_csv_url
        }

    try:
        resp = requests.post(
            provision_endpoint,
            json={"action": "provision", "email": u},
            timeout=20
        )
        data = resp.json() if resp.status_code == 200 else {}
        if data.get("status") == "ok":
            new_sheet_url = (data.get("sheet_url") or existing_sheet_url).strip()
            new_csv_url = (data.get("csv_url") or existing_csv_url).strip()
            new_debt_csv = (data.get("debt_csv_url") or new_csv_url).strip()

            c.execute(
                """
                UPDATE users
                SET sheet_url = ?, csv_url = ?, debt_csv_url = ?, links_locked = 1
                WHERE username = ?
                """,
                (new_sheet_url, new_csv_url, new_debt_csv, u)
            )
            conn.commit()
            conn.close()
            return {
                "sheet_url": new_sheet_url,
                "csv_url": new_csv_url,
                "debt_csv_url": new_debt_csv
            }
    except Exception:
        pass

    conn.close()
    return {
        "sheet_url": existing_sheet_url,
        "csv_url": existing_csv_url,
        "debt_csv_url": existing_debt_csv or existing_csv_url
    }

def get_user_sheet_urls(user_email: str) -> dict:
    u = (user_email or "").strip().lower()
    if not u:
        return {"sheet_url": "", "csv_url": "", "debt_csv_url": ""}
    init_db()
    ensure_user_sheet_columns()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT sheet_url, csv_url, debt_csv_url FROM users WHERE username = ?", (u,))
    row = c.fetchone()
    conn.close()

    s_url = (row[0] or "").strip() if row else ""
    c_url = (row[1] or "").strip() if row else ""
    d_url = (row[2] or "").strip() if row else ""

    if not c_url and MASTER_PROVISION_URL:
        return auto_provision_user_sheet(u)

    return {"sheet_url": s_url, "csv_url": c_url, "debt_csv_url": d_url or c_url}

@st.cache_data(ttl=5)
def load_user_expenses_csv(csv_url: str, cache_buster: int = 0) -> pd.DataFrame:
    target = (csv_url or "").strip()
    if not target:
        return pd.DataFrame(columns=["Date", "Timestamp", "Item", "Amount", "Debit", "Credit", "Category"])
    try:
        sep = "&" if "?" in target else "?"
        df = pd.read_csv(f"{target}{sep}r={random.randint(1, 999999)}_{cache_buster}")
        df.columns = df.columns.str.strip()

        if "Date" in df.columns:
            df["Date"] = parse_mixed_dates(df["Date"])
        elif "Timestamp" in df.columns:
            df["Date"] = parse_mixed_dates(df["Timestamp"])
        else:
            df["Date"] = pd.NaT

        if "Debit" not in df.columns:
            df["Debit"] = 0.0
        if "Credit" not in df.columns:
            df["Credit"] = 0.0

        df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce").fillna(0.0)
        df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce").fillna(0.0)

        if "Amount" not in df.columns:
            df["Amount"] = df.apply(
                lambda r: r["Credit"] if r["Credit"] > 0 else r["Debit"],
                axis=1
            )
        else:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)

        if "Item" not in df.columns:
            df["Item"] = "Expense"
        else:
            df["Item"] = df["Item"].fillna("Expense").astype(str)

        if "Category" not in df.columns:
            df["Category"] = df["Item"].apply(categorize_item_label)
        else:
            df["Category"] = df["Category"].fillna("").astype(str)
            df["Category"] = df.apply(
                lambda r: r["Category"].strip() if r["Category"].strip() else categorize_item_label(r["Item"]),
                axis=1
            )

        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Timestamp", "Item", "Amount", "Debit", "Credit", "Category"])

def save_entry_to_user_sheet(item: str, amount: float, category: str = "Others", entry_type: str = "Debit", entry_date=None):
    user_email = (st.session_state.get("user") or "").strip().lower()
    endpoint = (MASTER_PROVISION_URL or "").strip()
    if not endpoint or not user_email:
        return False, "Sheet provisioner or user email missing."

    dt_obj = entry_date if isinstance(entry_date, datetime) else datetime.now(GST)
    eng_item = translate_to_english_label(item, "Expense")
    eng_cat = translate_to_english_label(category, "Others")
    date_only_str = dt_obj.strftime("%m/%d/%Y")
    timestamp_str = dt_obj.strftime("%m/%d/%Y %H:%M:%S")

    payload = {
        "action": "add_entry",
        "email": user_email,
        "item": eng_item,
        "amount": float(amount),
        "category": eng_cat,
        "type": "Credit" if str(entry_type).lower() == "credit" else "Debit",
        "date_only": date_only_str,
        "timestamp": timestamp_str
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=15)
        if resp.status_code == 200:
            refresh_user_sheet_cache()
            return True, f"Saved to your Google Sheet: {eng_item} - ₹{float(amount):,.2f}"
        return False, f"Sheet response error ({resp.status_code})"
    except Exception as e:
        return False, f"Failed to save: {e}"