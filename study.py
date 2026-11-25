from datetime import datetime
import random
import sqlite3
import pandas as pd
import requests
import streamlit as st

DB_FILE = globals().get("DB_FILE", "expense_users.db")

MASTER_PROVISION_URL = st.secrets.get(
    "MASTER_PROVISION_URL",
    st.secrets.get("SHEET_WEB_APP_URL", "")
)


def init_sheet_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            sheet_url TEXT DEFAULT '',
            csv_url TEXT DEFAULT '',
            debt_csv_url TEXT DEFAULT '',
            links_locked INTEGER DEFAULT 0
        )
        """
    )
    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]
    for col_name, col_def in [
        ("sheet_url", "TEXT DEFAULT ''"),
        ("csv_url", "TEXT DEFAULT ''"),
        ("debt_csv_url", "TEXT DEFAULT ''"),
        ("links_locked", "INTEGER DEFAULT 0"),
    ]:
        if col_name not in cols:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
    conn.commit()
    conn.close()


init_sheet_db()


def ensure_user_sheet_columns():
    init_sheet_db()


def provision_user_sheet(user_email: str, force_refresh: bool = False) -> dict:
    email = (user_email or "").strip().lower()
    if not email:
        return {"sheet_url": "", "csv_url": "", "debt_csv_url": ""}

    init_sheet_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT sheet_url, csv_url, debt_csv_url FROM users WHERE username = ?",
        (email,),
    )
    row = c.fetchone()

    sheet_url = (row[0] or "").strip() if row else ""
    csv_url = (row[1] or "").strip() if row else ""
    debt_csv_url = (row[2] or "").strip() if row else ""

    if csv_url and not force_refresh:
        conn.close()
        return {
            "sheet_url": sheet_url,
            "csv_url": csv_url,
            "debt_csv_url": debt_csv_url or csv_url,
        }

    endpoint = (MASTER_PROVISION_URL or "").strip()
    if endpoint:
        try:
            res = requests.post(
                endpoint,
                json={"action": "provision", "email": email},
                timeout=20,
            )
            data = res.json() if res.status_code == 200 else {}
            if data.get("status") == "ok":
                sheet_url = (data.get("sheet_url") or sheet_url).strip()
                csv_url = (data.get("csv_url") or csv_url).strip()
                debt_csv_url = (data.get("debt_csv_url") or csv_url).strip()

                c.execute(
                    """
                    INSERT INTO users (username, sheet_url, csv_url, debt_csv_url, links_locked)
                    VALUES (?, ?, ?, ?, 1)
                    ON CONFLICT(username) DO UPDATE SET
                        sheet_url = excluded.sheet_url,
                        csv_url = excluded.csv_url,
                        debt_csv_url = excluded.debt_csv_url,
                        links_locked = 1
                    """,
                    (email, sheet_url, csv_url, debt_csv_url),
                )
                conn.commit()
        except Exception:
            pass

    conn.close()
    return {
        "sheet_url": sheet_url,
        "csv_url": csv_url,
        "debt_csv_url": debt_csv_url or csv_url,
    }


@st.cache_data(ttl=5)
def load_sheet_expenses(csv_url: str, cache_buster: int = 0) -> pd.DataFrame:
    empty_cols = ["Timestamp", "Date", "Item", "Debit", "Credit", "Category", "Amount"]
    target = (csv_url or "").strip()
    if not target:
        return pd.DataFrame(columns=empty_cols)

    try:
        sep = "&" if "?" in target else "?"
        df = pd.read_csv(f"{target}{sep}cb={random.randint(1, 999999)}_{cache_buster}")
        df.columns = df.columns.str.strip()

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        elif "Timestamp" in df.columns:
            df["Date"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        else:
            df["Date"] = pd.NaT

        if "Timestamp" not in df.columns:
            df["Timestamp"] = ""

        for col in ["Debit", "Credit"]:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        df["Amount"] = df.apply(
            lambda r: r["Credit"] if r["Credit"] > 0 else r["Debit"],
            axis=1,
        )

        if "Item" not in df.columns:
            df["Item"] = "Expense"
        else:
            df["Item"] = df["Item"].fillna("Expense").astype(str)

        if "Category" not in df.columns:
            df["Category"] = "Others"
        else:
            df["Category"] = df["Category"].fillna("Others").astype(str)
            df["Category"] = df["Category"].apply(
                lambda x: x.strip() if x.strip() else "Others"
            )

        return df
    except Exception:
        return pd.DataFrame(columns=empty_cols)


def send_expense_to_sheet(
    item: str,
    amount: float = 0.0,
    category: str = "Others",
    entry_type: str = "Debit",
    entry_date=None,
    debit: float = None,
    credit: float = None,
):
    email = (st.session_state.get("user") or "").strip().lower()
    endpoint = (MASTER_PROVISION_URL or "").strip()
    if not email or not endpoint:
        return False, "Missing user email or MASTER_PROVISION_URL."

    dt = entry_date if isinstance(entry_date, datetime) else datetime.now()
    is_credit = str(entry_type).strip().lower() == "credit"
    base_amt = float(amount or 0.0)

    debit_val = float(debit) if debit is not None else (0.0 if is_credit else base_amt)
    credit_val = float(credit) if credit is not None else (base_amt if is_credit else 0.0)
    shown_amt = credit_val if credit_val > 0 else debit_val

    payload = {
        "action": "add_entry",
        "email": email,
        "timestamp": dt.strftime("%m/%d/%Y %H:%M:%S"),
        "date_only": dt.strftime("%m/%d/%Y"),
        "item": (item or "Expense").strip(),
        "debit": debit_val,
        "credit": credit_val,
        "amount": shown_amt,
        "category": (category or "Others").strip(),
        "type": "Credit" if is_credit else "Debit",
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=15)
        if res.status_code == 200:
            load_sheet_expenses.clear()
            return True, f"Saved: {payload['item']} ({shown_amt:,.2f})"
        return False, f"Error ({res.status_code})"
    except Exception as exc:
        return False, f"Failed: {exc}"