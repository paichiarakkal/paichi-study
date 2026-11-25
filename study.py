import streamlit as st
import pandas as pd, requests, random, re, json, time, hashlib, hmac, base64, sqlite3, smtplib, calendar as py_cal
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
from groq import Groq
from streamlit_calendar import calendar
from twilio.rest import Client

st.set_page_config(page_title="PAICHI EXPENSES", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- CONFIG ---
S = st.secrets
WA_PHONE = S.get("DEFAULT_WA_PHONE", "")
BG_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"
GROQ_KEY = S.get("GROQ_API_KEY", "")
SECRET_KEY = S.get("SESSION_SECRET_KEY", "paichi_expenses_secure_key_2026")
DB_FILE, GST = "paichi_users_v2.db", timezone(timedelta(hours=4))

# --- DB & AUTH HELPERS ---
def db_exec(q, params=(), fetch=None):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(q, params)
        conn.commit()
        return c.fetchone() if fetch == 1 else (c.fetchall() if fetch == "all" else None)

def init_db():
    db_exec("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, sheet_url TEXT DEFAULT '', csv_url TEXT DEFAULT '', links_locked INTEGER DEFAULT 0, account_locked INTEGER DEFAULT 1)")
    cols = [r[1] for r in db_exec("PRAGMA table_info(users)", fetch="all")]
    for col, df_val in [("sheet_url", "''"), ("csv_url", "''"), ("links_locked", "0"), ("account_locked", "1")]:
        if col not in cols: db_exec(f"ALTER TABLE users ADD COLUMN {col} {'INTEGER' if 'locked' in col else 'TEXT'} DEFAULT {df_val}")

init_db()
h_pwd = lambda p: hashlib.sha256(p.encode()).hexdigest()

def load_sec_users():
    raw = S.get("USERS_DATA", {})
    if isinstance(raw, str):
        try: return json.loads(raw) if isinstance(json.loads(raw), dict) else {}
        except: return {}
    return dict(raw) if isinstance(raw, dict) else {}

def is_registered(u):
    u = (u or "").strip().lower()
    return bool(u and (u in load_sec_users() or db_exec("SELECT 1 FROM users WHERE username=?", (u,), 1)))

def get_user(u):
    u = (u or "").strip().lower()
    if not u: return None
    s_rec = load_sec_users().get(u)
    if isinstance(s_rec, dict) and s_rec.get("password_hash"):
        sv, cv = (s_rec.get("sheet_url") or "").strip(), (s_rec.get("csv_url") or "").strip()
        lk = 1 if (sv or cv or s_rec.get("links_locked")) else 0
        db_exec("""INSERT INTO users VALUES (?,?,?,?,?,1) ON CONFLICT(username) DO UPDATE SET
            password_hash=excluded.password_hash, sheet_url=CASE WHEN users.sheet_url!='' THEN users.sheet_url ELSE excluded.sheet_url END,
            csv_url=CASE WHEN users.csv_url!='' THEN users.csv_url ELSE excluded.csv_url END,
            links_locked=CASE WHEN users.links_locked=1 OR excluded.links_locked=1 THEN 1 ELSE 0 END, account_locked=1""",
            (u, s_rec["password_hash"], sv, cv, lk))
    r = db_exec("SELECT username, password_hash, sheet_url, csv_url, links_locked, account_locked FROM users WHERE username=?", (u,), 1)
    if not r: return None
    return {"username": r[0], "password_hash": r[1], "sheet_url": r[2] or "", "csv_url": r[3] or "", "links_locked": 1 if (r[2] or r[3] or r[4]) else 0, "account_locked": r[5] if r[5] is not None else 1}

def create_user(u, p):
    u = u.strip().lower()
    if is_registered(u): raise ValueError("Account already registered.")
    ph = h_pwd(p)
    db_exec("INSERT INTO users VALUES (?,?,'','',0,1)", (u, ph))
    return {u: {"password_hash": ph, "sheet_url": "", "csv_url": "", "links_locked": False, "account_locked": True}}

def bind_links(u, s_url, c_url):
    ex = get_user(u)
    if not ex: return False, "Account not found."
    if ex["links_locked"] or ex["sheet_url"] or ex["csv_url"]: return False, "Links already locked."
    if not (s_url or c_url): return False, "Enter at least one link."
    db_exec("UPDATE users SET sheet_url=?, csv_url=?, links_locked=1 WHERE username=?", (s_url, c_url, u.strip().lower()))
    return True, "Links permanently locked."

def send_otp(to_email, code, purpose="OTP"):
    body = f"Hello,\n\nYour 6-digit OTP for PAICHI EXPENSES ({purpose}) is: {code}\nDo not share this code."
    bk, bs, rk = S.get("BREVO_API_KEY", "").strip(), S.get("BREVO_SENDER_EMAIL", "").strip(), S.get("RESEND_API_KEY", "").strip()
    if bk and bs:
        r = requests.post("https://api.brevo.com/v3/smtp/email", headers={"api-key": bk, "Content-Type": "application/json"},
                          json={"sender": {"name": "PAICHI EXPENSES", "email": bs}, "to": [{"email": to_email}], "subject": f"PAICHI EXPENSES - {purpose}", "textContent": body}, timeout=15)
        if r.status_code in (200, 201, 202): return True
        raise RuntimeError(f"Brevo Error: {r.text}")
    if rk:
        r = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {rk}", "Content-Type": "application/json"},
                          json={"from": S.get("OTP_FROM_EMAIL", "onboarding@resend.dev"), "to": [to_email], "subject": f"PAICHI EXPENSES - {purpose}", "text": body}, timeout=15)
        if r.status_code in (200, 201): return True
        raise RuntimeError(f"Resend Error: {r.text}")
    snd, pwd = S.get("SMTP_EMAIL", "").strip(), S.get("SMTP_APP_PASSWORD", "").replace(" ", "").strip()
    if not snd or not pwd: raise ValueError("Email secrets not configured.")
    msg = EmailMessage(); msg["Subject"], msg["From"], msg["To"] = f"PAICHI EXPENSES - {purpose}", snd, to_email; msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as srv: srv.login(snd, pwd); srv.send_message(msg)
    except Exception:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as srv: srv.starttls(); srv.login(snd, pwd); srv.send_message(msg)
    return True

# --- SESSION & STATE ---
def make_tok(u):
    u = u.strip().lower()
    return base64.urlsafe_b64encode(f"{u}:{hmac.new(SECRET_KEY.encode(), u.encode(), hashlib.sha256).hexdigest()[:24]}".encode()).decode()

def check_tok(tok):
    try:
        u, sig = base64.urlsafe_b64decode(tok.encode()).decode().split(":", 1)
        return u if hmac.compare_digest(sig, hmac.new(SECRET_KEY.encode(), u.encode(), hashlib.sha256).hexdigest()[:24]) else None
    except: return None

defaults = {"auth": False, "user": "", "custom_alert_text": "Low balance alert", "low_limit": 6000, "pending_entry": None,
            "ai_action_notice": None, "entry_saved_flag": False, "ai_chat_key_id": 0, "last_voice_text": "", "last_heard_text": "",
            "ai_chat_history": [], "buddy_messages": [], "signup_otp": None, "signup_otp_email": "", "signup_otp_verified": False,
            "reset_otp": None, "reset_otp_email": "", "reset_otp_verified": False}
for k, v in defaults.items(): st.session_state.setdefault(k, v)

if not st.session_state.auth and st.query_params.get("session"):
    vu = check_tok(st.query_params["session"])
    if vu and get_user(vu): st.session_state.auth, st.session_state.user = True, vu

# --- CSS ---
st.markdown(f"""<style>
[data-testid="stAppViewContainer"]{{background:linear-gradient(rgba(10,10,25,.85),rgba(10,10,25,.95)),url("{BG_URL}") center/cover fixed}}
[data-testid="stSidebar"]{{background:rgba(20,20,35,.6)!important;backdrop-filter:blur(15px);border-right:1px solid rgba(255,255,255,.1)}}
.stButton>button{{background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;border-radius:12px;font-weight:bold;width:100%;border:none;padding:10px;box-shadow:0 4px 15px rgba(255,215,0,.4)}}
.glass-card,.balance-banner,.category-box,.login-card{{background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);border-radius:18px;padding:20px;margin-bottom:18px;text-align:center}}
.balance-banner{{border-left:8px solid #FFD700}} .category-box{{background:rgba(0,0,0,.5);border-bottom:4px solid #FFD700}}
.alert-banner{{background:linear-gradient(90deg,#ff4d4d,#cc0000);color:#fff;padding:14px;border-radius:10px;text-align:center;font-weight:bold;margin-bottom:18px}}
.login-card{{background:rgba(20,20,35,.85);padding:35px;max-width:450px;margin:60px auto}}
h1,h2,h3,p,label{{color:#FFF!important;font-weight:bold!important}}
[data-testid="stChatMessage"]{{background:rgba(32,44,51,.9)!important;border-radius:15px!important;padding:14px!important}}
input,textarea,select{{color:#FFF!important;-webkit-text-fill-color:#FFF!important;background:rgba(0,0,0,.5)!important;border:1px solid rgba(255,255,255,.2)!important;border-radius:8px!important}}
</style>""", unsafe_allow_html=True)

# --- DATA & AI HELPERS ---
MAP_WORDS = {"ചായ":"Tea","കാപ്പി":"Coffee","കോഫി":"Coffee","ഭക്ഷണം":"Food","ചിക്കൻ":"Chicken","മീൻ":"Fish","ബിരിയാണി":"Biryani","കട":"Shop","യാത്ര":"Travel","പെട്രോൾ":"Petrol","വാടക":"Rent","ജയ":"Jaya","شاي":"Tea","قهوة":"Coffee","طعام":"Food","चाय":"Tea","खाना":"Food"}
CAT_RULES = [("Food", ["food","tea","coffee","biryani","meal","lunch","dinner","breakfast","ഭക്ഷണം","ചായ","കോഫി","ഹോട്ടൽ","ബിരിയാണി"]),
             ("Shop", ["shop","store","supermarket","grocery","കട","സാധനങ്ങൾ","സൂപ്പർമാർക്കറ്റ്"]),
             ("Fish", ["fish","meat","chicken","mutton","മീൻ","ഇറച്ചി","ചിക്കൻ"]),
             ("Travel", ["travel","petrol","fuel","taxi","bus","metro","യാത്ര","പെട്രോൾ","വണ്ടി","ടാക്സി"]),
             ("Rent", ["rent","room","വാടക","റൂം"])]

def to_eng(txt, default="Expense"):
    raw = (txt or "").strip()
    if not raw: return default
    for k, v in MAP_WORDS.items():
        if k in raw.lower(): return v
    if GROQ_KEY and re.search(r"[^\x00-\x7F]", raw):
        try:
            res = Groq(api_key=GROQ_KEY).chat.completions.create(model="openai/gpt-oss-120b", max_tokens=30,
                messages=[{"role":"system","content":"Translate expense/item/name to concise English (1-2 words). Return ONLY English text."},{"role":"user","content":raw}])
            out = (res.choices[0].message.content or "").strip().strip('"\'')
            if out: return out
        except: pass
    c = re.sub(r"[^\x00-\x7F]+", "", raw).strip()
    return c or default

def get_cat(item):
    low = str(item or "").lower()
    return next((c for c, ws in CAT_RULES if any(w in low for w in ws)), "Others")

def fmt_dt(dt=None):
    if isinstance(dt, datetime): d = dt
    elif dt: p = pd.to_datetime(str(dt).strip(), errors="coerce"); d = p.to_pydatetime() if not pd.isna(p) else datetime.now(GST)
    else: d = datetime.now(GST)
    return d.strftime("%d %b %Y %H:%M:%S")

def send_wa(msg):
    try:
        sid, tok = S.get("TWILIO_ACCOUNT_SID", ""), S.get("TWILIO_AUTH_TOKEN", "")
        if sid and tok and WA_PHONE: Client(sid, tok).messages.create(from_='whatsapp:+14155238886', body=msg, to=f'whatsapp:+{WA_PHONE}')
    except: pass

def post_sheet(payload, wa_msg=""):
    url = (get_user(st.session_state.user) or {}).get("sheet_url", "").strip()
    if url: requests.post(url, json=payload, timeout=10); st.cache_data.clear()
    if wa_msg: send_wa(wa_msg)

@st.cache_data(ttl=5)
def load_csv(url, cols):
    try:
        if not url: return pd.DataFrame(columns=cols)
        df = pd.read_csv(f"{url}{'&' if '?' in url else '?'}r={random.randint(1,999999)}")
        df.columns = df.columns.str.strip()
        if 'Date' in df and 'Debit' in df:
            df['Date'] = pd.to_datetime(df['Date'].astype(str).str.strip(), errors='coerce').fillna(pd.to_datetime(df['Date'].astype(str).str.strip(), dayfirst=True, errors='coerce'))
            for c in ['Debit', 'Credit']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        elif 'Amount' in df:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame(columns=cols)

def build_ctx(df_e, df_d):
    now = datetime.now(GST)
    rem_days = max(1, py_cal.monthrange(now.year, now.month)[1] - now.day + 1)
    tin, tout = (float(df_e["Credit"].sum()), float(df_e["Debit"].sum())) if not df_e.empty else (0.0, 0.0)
    bal = tin - tout
    t_c = t_d = m_c = m_d = 0.0
    cats, recs = "None", "None"
    if not df_e.empty and "Date" in df_e:
        v = df_e.dropna(subset=["Date"]).copy()
        if not v.empty:
            t_r, m_r = v[v["Date"].dt.strftime("%Y-%m-%d") == now.strftime("%Y-%m-%d")], v[v["Date"].dt.strftime("%Y-%m") == now.strftime("%Y-%m")]
            t_c, t_d, m_c, m_d = float(t_r["Credit"].sum()), float(t_r["Debit"].sum()), float(m_r["Credit"].sum()), float(m_r["Debit"].sum())
            ct = v.assign(Cat=v["Item"].apply(get_cat)).groupby("Cat")["Debit"].sum()
            cats = ", ".join(f"{k}: ₹{val:,.2f}" for k, val in ct.items() if val > 0) or "None"
            recs = " | ".join(f"[{r['Date'].strftime('%d %b %Y')}] {r['Item']} - {'Debit ₹'+str(r['Debit']) if r['Debit']>0 else 'Credit ₹'+str(r['Credit'])}" for _, r in v.sort_values("Date", ascending=False).head(8).iterrows())
    lp = bp = 0.0; dl = []
    if df_d is not None and not df_d.empty:
        p = df_d[df_d["Status"] == "Pending"] if "Status" in df_d else df_d
        lp = float(p[p["Type"].astype(str).str.contains("Lent", case=False, na=False)]["Amount"].sum())
        bp = float(p[p["Type"].astype(str).str.contains("Borrowed", case=False, na=False)]["Amount"].sum())
        dl = [f"{r['Name']} ({r['Type']}: ₹{float(r['Amount']):,.2f})" for _, r in p.head(8).iterrows()]
    return (f"GST: {now.strftime('%d %b %Y %H:%M:%S')}. Balance: ₹{bal:,.2f} (Credit: ₹{tin:,.2f}, Debit: ₹{tout:,.2f}). "
            f"Today: Credit ₹{t_c:,.2f}, Debit ₹{t_d:,.2f}. Month: Credit ₹{m_c:,.2f}, Debit ₹{m_d:,.2f}. "
            f"Remaining days: {rem_days}, Safe daily spend: ₹{max(0.0, bal/rem_days):,.2f}/day. Categories: {cats}. "
            f"Debts -> Lent: ₹{lp:,.2f}, Borrowed: ₹{bp:,.2f}, Items: {', '.join(dl) or 'None'}. Recent: {recs}.")

def make_pdf(df):
    try:
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14); pdf.cell(190, 10, "FINANCE REPORT", ln=True, align='C'); pdf.ln(8)
        pdf.set_font("Arial", 'B', 10); w = {"Date": 30, "Item": 85, "Debit": 35, "Credit": 35}
        for c in w: pdf.cell(w[c], 10, c, border=1, align='C')
        pdf.ln(); pdf.set_font("Arial", size=9)
        for _, r in df.iterrows():
            if pdf.get_y() > 260: pdf.add_page()
            y = pdf.get_y(); pdf.cell(30, 10, str(r['Date'])); x = pdf.get_x()
            pdf.multi_cell(85, 5, str(r['Item']).encode('ascii', 'ignore').decode())
            h = max(10, pdf.get_y() - y); pdf.set_xy(x + 85, y)
            pdf.cell(35, h, str(r['Debit']), align='R'); pdf.cell(35, h, str(r['Credit']), align='R')
            pdf.set_xy(10, y); [pdf.cell(val, h, "", border=1) for val in w.values()]; pdf.set_y(y + h)
        return bytes(pdf.output())
    except: return None

# --- AUTH SCREEN ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("🔐 PAICHI EXPENSES")
        t1, t2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        with t1:
            lu = st.text_input("📧 Email / Username", key="lu").strip().lower()
            lp = st.text_input("🔑 Password", type="password", key="lp")
            if st.button("LOGIN 🔓"):
                rec = get_user(lu)
                if rec and rec["password_hash"] == h_pwd(lp):
                    st.cache_data.clear(); st.session_state.auth, st.session_state.user = True, lu
                    st.query_params["session"] = make_tok(lu); st.rerun()
                else: st.error("❌ Invalid credentials or account not found.")
            with st.expander("🔄 Forgot Password (OTP)"):
                ru = st.text_input("📧 Registered Email", key="ru").strip().lower()
                if st.button("📩 Send Reset OTP"):
                    if get_user(ru) and "@" in ru:
                        code = f"{random.randint(100000,999999)}"
                        st.session_state.update(reset_otp=code, reset_otp_email=ru, reset_otp_verified=False)
                        try: send_otp(ru, code, "Reset Password"); st.success("✅ OTP sent!")
                        except Exception as e: st.error(f"❌ {e}")
                    else: st.error("❌ Valid registered email required.")
                if st.session_state.reset_otp and st.session_state.reset_otp_email == ru:
                    if st.button("✅ Verify OTP", key="vr_otp") and st.text_input("🔢 OTP", key="ri", max_chars=6).strip() == st.session_state.reset_otp:
                        st.session_state.reset_otp_verified = True; st.success("✅ Verified!")
                if st.session_state.reset_otp_verified and st.session_state.reset_otp_email == ru:
                    np1, np2 = st.text_input("🔑 New Password", type="password"), st.text_input("🔒 Confirm", type="password")
                    if st.button("RESET PASSWORD 🔁") and np1 and np1 == np2:
                        nh = h_pwd(np1); db_exec("UPDATE users SET password_hash=? WHERE username=?", (nh, ru))
                        st.session_state.update(reset_otp=None, reset_otp_email="", reset_otp_verified=False)
                        st.success("✅ Password updated."); st.code(f'"{ru}": {{"password_hash": "{nh}"}}', language="json")
        with t2:
            su = st.text_input("📧 Google / Email ID", key="su").strip().lower()
            if is_registered(su): st.error("❌ Already registered.")
            else:
                if st.button("📩 Send Sign Up OTP") and "@" in su:
                    code = f"{random.randint(100000,999999)}"
                    st.session_state.update(signup_otp=code, signup_otp_email=su, signup_otp_verified=False)
                    try: send_otp(su, code, "Sign Up"); st.success("✅ OTP sent!")
                    except Exception as e: st.error(f"❌ {e}")
                if st.session_state.signup_otp and st.session_state.signup_otp_email == su:
                    if st.button("✅ Verify OTP", key="vs_otp") and st.text_input("🔢 OTP", key="si", max_chars=6).strip() == st.session_state.signup_otp:
                        st.session_state.signup_otp_verified = True; st.success("✅ Verified!")
                if st.session_state.signup_otp_verified and st.session_state.signup_otp_email == su:
                    sp1, sp2 = st.text_input("🔑 Password", type="password", key="sp1"), st.text_input("🔒 Confirm", type="password", key="sp2")
                    if st.button("COMPLETE SIGN UP ✨") and sp1 and sp1 == sp2:
                        ent = create_user(su, sp1)
                        st.session_state.update(signup_otp=None, signup_otp_email="", signup_otp_verified=False, auth=True, user=su)
                        st.query_params["session"] = make_tok(su); st.code(json.dumps(ent, indent=2), language="json"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APP ---
else:
    prof = get_user(st.session_state.user) or {}
    csv_url = prof.get("csv_url", "").strip()
    df = load_csv(csv_url, ['Date', 'Item', 'Debit', 'Credit'])
    tin, tout = (df['Credit'].sum(), df['Debit'].sum()) if not df.empty else (0.0, 0.0)
    bal = tin - tout

    st.sidebar.caption(f"👤 {st.session_state.user.split('@')[0]}")
    with st.sidebar.expander("🔗 Link Sheet (One-Time)"):
        if prof.get("links_locked") or prof.get("sheet_url") or csv_url: st.info("🔒 Sheet links locked.")
        else:
            s1, s2 = st.text_input("Web App URL").strip(), st.text_input("CSV URL").strip()
            if st.button("SUBMIT LINK ONCE 🔒"):
                ok, msg = bind_links(st.session_state.user, s1, s2)
                (st.success(msg) or st.cache_data.clear() or st.rerun()) if ok else st.error(msg)

    with st.sidebar.expander("⚙️ Settings"):
        if st.button("🔄 Sync Data"): st.cache_data.clear(); st.rerun()
        st.session_state.custom_alert_text = st.text_area("Alert Message", st.session_state.custom_alert_text)
        st.session_state.low_limit = st.number_input("Low Balance Limit (₹)", value=st.session_state.low_limit)

    page = st.sidebar.radio("Menu", ["🏠 Dashboard", "💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker", "🤖 AI Chat", "🧠 My AI Buddy"])
    if st.sidebar.button("Logout"):
        st.session_state.update(auth=False, user=""); st.query_params.pop("session", None); st.rerun()

    if page == "🏠 Dashboard":
        if bal < st.session_state.low_limit:
            st.markdown(f'<div class="alert-banner">⚠️ {st.session_state.custom_alert_text} (₹{bal:,.2f})!</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="balance-banner"><span style="font-size:20px;color:#E0B0FF">AVAILABLE BALANCE</span><br><span style="font-size:48px;color:#FFD700;font-family:monospace">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h2 style="color:#00FF00">Credit: ₹{tin:,.2f}</h2><h2 style="color:#FF3131">Debit: ₹{tout:,.2f}</h2></div>', unsafe_allow_html=True)
        if not df.empty and 'Item' in df:
            cats = df.assign(Cat=df['Item'].apply(get_cat)).groupby('Cat')['Debit'].sum()
            cols = st.columns(3)
            for i, (cn, ca) in enumerate((k, v) for k, v in cats.items() if v > 0):
                cols[i % 3].markdown(f'<div class="category-box"><span style="color:#aaa">Total {cn}</span><br><span style="font-size:24px;color:#FFF">₹{ca:,.2f}</span></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml-IN', key='voice_v9')
        v_cat, v_amt, v_desc, v_type = "Others", "", "", "Debit"
        if v_raw:
            raw = v_raw.lower().replace('.', '').replace(',', '')
            nums = re.findall(r'\d+', raw)
            v_amt = nums[0] if nums else ""
            v_desc = to_eng(re.sub(r'\d+', '', raw).strip())
            v_cat = get_cat(raw)
            if any(x in raw for x in ["credit", "received", "salary", "കിട്ടി", "വന്നു", "തന്നു"]): v_type = "Credit"
        CATS = ["Food", "Shop", "Fish", "Travel", "Rent", "Others"]
        with st.form("entry_form", clear_on_submit=True):
            it, am_s = st.text_input("Description", v_desc), st.text_input("Amount", str(v_amt))
            cat = st.selectbox("Category", CATS, index=CATS.index(v_cat))
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True, index=0 if v_type == "Debit" else 1)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am, eit, edt = float(am_s.strip().replace(',', '')), to_eng(it), fmt_dt()
                    post_sheet({"item": eit, "amount": am, "category": cat, "type": ty, "date": edt}, f"✅ *Expense Entry*\n📝 {eit}\n💰 ₹{am}\n📅 {edt}")
                    st.success("Saved! ✅"); time.sleep(1); st.rerun()
                except Exception as e: st.error(f"Error! {e}")

    elif page == "📅 Calendar":
        st.title("P&L Calendar View 📅")
        st.markdown("<style>.fc{background:#fff!important;color:#111!important;padding:12px;border-radius:14px}.fc a,.fc-toolbar-title{color:#111!important}.fc-button-primary{background:#e55353!important;border:none!important}</style>", unsafe_allow_html=True)
        if df.empty: st.info("No data available.")
        else:
            dfc = df.dropna(subset=['Date']).assign(DayKey=lambda x: x['Date'].dt.strftime('%Y-%m-%d'))
            evs = []
            for _, r in dfc.groupby('DayKey', as_index=False)[['Debit', 'Credit']].sum().iterrows():
                if r['Debit'] > 0: evs.append({"title": f"-₹{r['Debit']:,.0f}", "start": r['DayKey'], "backgroundColor": "#d9383a"})
                if r['Credit'] > 0: evs.append({"title": f"+₹{r['Credit']:,.0f}", "start": r['DayKey'], "backgroundColor": "#2e8b57"})
            cd = calendar(events=evs, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth", "height": "auto", "dayMaxEvents": True}, key="pnl_cal")
            sel = (cd.get("eventClick", {}).get("event", {}).get("start", "") if cd and cd.get("callback") == "eventClick" else (cd.get("dateClick", {}).get("date", "") if cd and cd.get("callback") == "dateClick" else "")).split("T")[0]
            if sel:
                st.subheader(f"📋 Details for {sel}")
                ddf = dfc[dfc['DayKey'] == sel].copy()
                if not ddf.empty: ddf['Date'] = ddf['Date'].dt.strftime('%d %b %Y'); st.dataframe(ddf[['Date', 'Item', 'Debit', 'Credit']], use_container_width=True)

    elif page in ("📊 Report", "🔍 History"):
        if df.empty: st.info("No data available.")
        else:
            dfr = df.dropna(subset=['Date']).assign(Month=lambda x: x['Date'].dt.strftime('%B %Y'))
            months = dfr.sort_values('Date', ascending=False)['Month'].unique()
            sel_m = st.selectbox("Select Month", months)
            mdf = dfr[dfr['Month'] == sel_m].copy()
            if page == "📊 Report":
                mc, md = mdf['Credit'].sum(), mdf['Debit'].sum()
                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="glass-card"><h3 style="color:#00FF00">Credit</h3><h1>₹{mc:,.2f}</h1></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="glass-card"><h3 style="color:#FF3131">Expense</h3><h1>₹{md:,.2f}</h1></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="glass-card"><h3 style="color:#FFD700">Savings</h3><h1>₹{mc-md:,.2f}</h1></div>', unsafe_allow_html=True)
                mdf['Cat'] = mdf['Item'].apply(lambda x: x.split(':')[0] if ':' in str(x) else 'Others')
                st.plotly_chart(px.pie(mdf[mdf['Debit'] > 0], values='Debit', names='Cat', hole=0.4), use_container_width=True)
            cdf = mdf.drop(columns=['Month'], errors='ignore')
            cdf['Date'] = cdf['Date'].dt.strftime('%d %b %Y')
            st.dataframe(cdf.iloc[::-1], use_container_width=True)
            if page == "📊 Report" and (pdf_b := make_pdf(cdf)):
                st.download_button("📄 Download PDF", pdf_b, f"Report_{sel_m}.pdf", "application/pdf")

    elif page == "🤝 Debt Tracker":
        st.title("🤝 Debt Tracker")
        dfd = load_csv(csv_url, ['ID', 'Name', 'Type', 'Amount', 'Date', 'Status', 'Sender'])
        t1, t2, t3 = st.tabs(["📋 Active Debts", "➕ Add Debt", "⚙️ Settled"])
        with t1:
            pend = dfd[dfd['Status'] == "Pending"] if not dfd.empty else pd.DataFrame()
            tl = pend[pend['Type'].str.contains("Lent", na=False)]['Amount'].sum() if not pend.empty else 0.0
            tb = pend[pend['Type'].str.contains("Borrowed", na=False)]['Amount'].sum() if not pend.empty else 0.0
            ca, cb = st.columns(2)
            ca.markdown(f'<div class="glass-card"><h4 style="color:#00FF00">Receivable</h4><h2>₹{tl:,.2f}</h2></div>', unsafe_allow_html=True)
            cb.markdown(f'<div class="glass-card"><h4 style="color:#FF3131">Payable</h4><h2>₹{tb:,.2f}</h2></div>', unsafe_allow_html=True)
            for d in pend.to_dict('records'):
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.write(f"**{d['Name']}**"); c2.write(d['Type']); c3.write(f"**₹{d['Amount']:,.2f}**"); c4.write(str(d['Date']).split(' ')[0])
                if c5.button("✅ Settle", key=f"st_{d['ID']}"):
                    post_sheet({"action": "settle_debt", "id": d['ID']}); st.success("Settled!"); time.sleep(1); st.rerun()
        with t2:
            with st.form("debt_f", clear_on_submit=True):
                dn, dt_p, da, dd = st.text_input("Person"), st.selectbox("Type", ["Lent", "Borrowed"]), st.number_input("Amount", 1.0, step=10.0), st.date_input("Date", datetime.now(GST).date())
                if st.form_submit_button("SAVE 💾") and dn.strip():
                    en = to_eng(dn, "Person")
                    post_sheet({"action": "add_debt", "name": en, "type": dt_p, "amount": da, "date": dd.strftime("%d %b %Y")}, f"🤝 *Debt*\n👤 {en}\n📌 {dt_p}\n💰 ₹{da}")
                    st.success("Saved! ✅"); time.sleep(1); st.rerun()
        with t3:
            for _, it in (dfd[dfd['Status'] == "Settled"] if not dfd.empty else pd.DataFrame()).iterrows():
                st.write(f"✔️ **{it['Name']}** - {it['Type']} - ₹{it['Amount']:,.2f} ({str(it['Date']).split(' ')[0]})")

    elif page == "🧠 My AI Buddy":
        st.title("🧠 Your Personal AI Buddy")
        for m in st.session_state.buddy_messages: st.chat_message(m["role"]).markdown(m["content"])
        if ui := st.chat_input("Ask in English, Malayalam, Arabic, or Hindi..."):
            st.session_state.buddy_messages.append({"role": "user", "content": ui}); st.chat_message("user").markdown(ui)
            try:
                res = Groq(api_key=GROQ_KEY).chat.completions.create(model="openai/gpt-oss-120b", max_tokens=1024,
                    messages=[{"role": "system", "content": "Helpful personal AI assistant. Understand ML/EN/AR/HI, ALWAYS reply clearly in English."}] + st.session_state.buddy_messages[-4:])
                rep = res.choices[0].message.content
                st.session_state.buddy_messages.append({"role": "assistant", "content": rep}); st.chat_message("assistant").markdown(rep)
            except Exception as e: st.error(f"Error: {e}")

    elif page == "🤖 AI Chat":
        st.title("🤖 AI Agent & Assistant")
        if st.session_state.ai_action_notice: st.success(st.session_state.ai_action_notice)
        if st.session_state.last_heard_text: st.caption(f"🎙️ Heard: {st.session_state.last_heard_text}")
        for m in st.session_state.ai_chat_history[-8:]: st.chat_message(m["role"]).markdown(m["content"])

        def commit_pending(save=True):
            ed = st.session_state.pending_entry
            st.session_state.update(pending_entry=None, last_voice_text="")
            if save:
                post_sheet({"item": ed['item'], "amount": ed['amount'], "category": ed['category'], "type": ed['type'], "date": ed['date']}, f"✅ *AI Entry*\n📝 {ed['item']}\n💰 ₹{ed['amount']}")
                msg = f"Entry saved: {ed['item']} - ₹{ed['amount']} ({ed['type']})"
            else: msg = f"Cancelled: {ed['item']} - ₹{ed['amount']}"
            st.session_state.ai_action_notice = msg
            st.session_state.ai_chat_history.append({"role": "assistant", "content": msg})

        if st.session_state.pending_entry:
            pe = st.session_state.pending_entry
            st.info(f"**Confirm:** {pe['item']} - ₹{pe['amount']} ({pe['date']}). Save?")
            c1, c2 = st.columns(2)
            if c1.button("Yes"): commit_pending(True); st.rerun()
            if c2.button("No"): commit_pending(False); st.rerun()

        vr = speech_to_text(language='ml-IN', start_prompt="🎙️ Speak (ML / EN)", stop_prompt="⏹️ Stop", just_once=True, key=f"v_{st.session_state.ai_chat_key_id}")
        pr = st.chat_input("Type or speak...")
        fp = None
        if vr and vr.strip() != st.session_state.last_voice_text:
            st.session_state.update(last_voice_text=vr.strip(), last_heard_text=vr.strip(), ai_chat_key_id=st.session_state.ai_chat_key_id + 1); fp = vr.strip()
        elif pr and pr.strip():
            st.session_state.last_heard_text = pr.strip(); fp = pr.strip()

        if fp:
            cmd = fp.lower().strip()
            if st.session_state.pending_entry and cmd in ("yes", "y", "ok", "അതെ", "ശരി", "نعم", "हां"):
                st.session_state.ai_chat_history.append({"role": "user", "content": fp}); commit_pending(True); st.rerun()
            elif st.session_state.pending_entry and cmd in ("no", "n", "cancel", "അല്ല", "വേണ്ട", "لا", "नहीं"):
                st.session_state.ai_chat_history.append({"role": "user", "content": fp}); commit_pending(False); st.rerun()
            else:
                st.session_state.ai_action_notice = None
                st.chat_message("user").markdown(fp); st.session_state.ai_chat_history.append({"role": "user", "content": fp})
                try:
                    ctx = build_ctx(df, load_csv(csv_url, ['ID', 'Name', 'Type', 'Amount', 'Date', 'Status', 'Sender']))
                    sys_p = f'PAICHI AI router. CONTEXT: {ctx}. Reply ONLY JSON: {{"action":"single_entry","item":"Eng","amount":5,"category":"Food","type":"Debit"}} OR {{"action":"debt_entry","name":"Eng","type":"Lent","amount":500}} OR {{"action":"answer","reply":"Clear English answer"}}'
                    res = Groq(api_key=GROQ_KEY).chat.completions.create(model="openai/gpt-oss-120b", max_tokens=600,
                        messages=[{"role": "system", "content": sys_p}] + st.session_state.ai_chat_history[-5:-1] + [{"role": "user", "content": fp}])
                    raw = (res.choices[0].message.content or "").strip()
                    jm = re.search(r"\{.*\}", raw, re.DOTALL)
                    obj = json.loads(jm.group(0)) if jm else {}
                    act = obj.get("action")
                    if act == "single_entry":
                        st.session_state.pending_entry = {"item": to_eng(obj.get("item")), "amount": float(obj.get("amount", 0)), "category": to_eng(obj.get("category"), "Others"), "type": "Credit" if str(obj.get("type")).lower() == "credit" else "Debit", "date": fmt_dt()}
                        st.rerun()
                    elif act == "debt_entry":
                        dn, dt_p, da = to_eng(obj.get("name"), "Person"), "Borrowed" if "borrow" in str(obj.get("type")).lower() else "Lent", float(obj.get("amount", 0))
                        post_sheet({"action": "add_debt", "name": dn, "type": dt_p, "amount": da, "date": " ".join(fmt_dt().split()[:3])}, f"🤝 *AI Debt*\n👤 {dn}\n📌 {dt_p}\n💰 ₹{da}")
                        msg = f"Debt saved: {dt_p} - {dn} - ₹{da}"
                        st.session_state.update(ai_action_notice=msg); st.session_state.ai_chat_history.append({"role": "assistant", "content": msg}); st.rerun()
                    else:
                        rep = str(obj.get("reply") or raw or f"Balance: ₹{bal:,.2f}").strip()
                        st.chat_message("assistant").markdown(rep); st.session_state.ai_chat_history.append({"role": "assistant", "content": rep})
                except Exception as e: st.error(f"AI Error: {e}")