import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import re
import urllib.parse
import threading
from streamlit_calendar import calendar

# --- TWILIO CONFIG ---
TWILIO_SID = "YOUR_TWILIO_ACCOUNT_SID"  
TWILIO_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"  

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"

WA_PHONE = "971551347989"
WA_API_KEY = "7463030"

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

# --- BACKGROUND TWILIO SERVER ---
try:
    from flask import Flask, request
    from twilio.twiml.messaging_response import MessagingResponse
    
    flask_app = Flask(__name__)

    @flask_app.route("/whatsapp", methods=['POST'])
    def whatsapp_reply():
        incoming_msg = request.values.get('Body', '').lower().strip()
        resp = MessagingResponse()
        msg = resp.message()
        
        if "balance" in incoming_msg or "ബാലൻസ്" in incoming_msg:
            try:
                df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
                df.columns = df.columns.str.strip()
                t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
                t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
                bal = t_in - t_out
                
                reply_text = f"📊 *Paichi Finance Update*\n\n💰 Total Credit: ₹{t_in:,.2f}\n📉 Total Debit: ₹{t_out:,.2f}\n💵 *Available Balance: ₹{bal:,.2f}*"
                msg.body(reply_text)
            except:
                msg.body("⚠️ ഷീറ്റിൽ നിന്ന് ഡാറ്റ എടുക്കാൻ കഴിഞ്ഞില്ല. ദയവായി അല്പം കഴിഞ്ഞ് ശ്രമിക്കൂ.")
        else:
            msg.body("🤖 ഹലോ! കറന്റ് ബാലൻസ് അറിയാൻ *Balance* അല്ലെങ്കിൽ *ബാലൻസ്* എന്ന് അയക്കൂ.")
            
        return str(resp)

    def run_flask():
        flask_app.run(port=5000, host="0.0.0.0")

    if not any(t.name == "FlaskThread" for t in threading.enumerate()):
        threading.Thread(target=run_flask, name="FlaskThread", daemon=True).start()
except Exception as e:
    pass

# --- STREAMLIT UI CODE START ---
st.set_page_config(page_title="PAICHI EXPENSES v2.6", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""

# --- 🎨 HIGH-END AI PREMIUM DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0F0214, #1D062B, #05000B); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(10, 3, 18, 0.95) !important; border-right: 1px solid rgba(255, 215, 0, 0.1); }
    .stButton>button { background: linear-gradient(90deg, #FFD700, #FFA500); color: #000; border-radius: 12px; font-weight: bold; width: 100%; border: none; box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.2); transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 4px 20px rgba(255, 215, 0, 0.4); }
    .balance-banner { background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); padding: 30px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.2); backdrop-filter: blur(10px); margin-bottom: 25px; text-align: center; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
    .purple-box { background: rgba(255, 255, 255, 0.02); padding: 20px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); text-align: center; margin-bottom: 20px; }
    .category-box { background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 3px solid #FFD700; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; font-family: 'Poppins', sans-serif; }
    .stDataFrame { background: #12061C; border-radius: 12px; color: white; padding: 10px; }
    
    /* 🔥 ADVANCED DARK CALENDAR STYLING */
    .fc { background: rgba(15, 5, 25, 0.6) !important; border-radius: 20px !important; padding: 20px !important; border: 1px solid rgba(255, 215, 0, 0.15) !important; backdrop-filter: blur(10px); }
    .fc-header-toolbar { margin-bottom: 20px !important; }
    .fc-button { background: rgba(255, 215, 0, 0.1) !important; border: 1px solid #FFD700 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }
    .fc-button-active { background: #FFD700 !important; color: black !important; }
    .fc-col-header-cell { background: rgba(75, 0, 130, 0.4) !important; padding: 10px 0 !important; font-size: 14px !important; border: 1px solid rgba(255,255,255,0.05) !important; }
    .fc-daygrid-day { min-height: 100px !important; border: 1px solid rgba(255,255,255,0.03) !important; }
    .fc-day-today { background: rgba(255, 215, 0, 0.05) !important; border: 1px solid #FFD700 !important; }
    .fc-event { border-radius: 6px !important; padding: 4px 8px !important; font-size: 12px !important; font-weight: bold !important; border: none !important; margin-top: 3px !important; box-shadow: 0px 2px 5px rgba(0,0,0,0.2); }
    .fc-daygrid-day-number { color: #aaa !important; font-size: 14px !important; padding: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

def send_whatsapp_auto(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(message)}&apikey={WA_API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

def send_to_google_async(data):
    try: requests.post(FORM_API, data=data, timeout=10)
    except: pass

def get_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        t_in = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
        t_out = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
        return t_in, t_out, (t_in - t_out)
    except: return 0.0, 0.0, 0.0

def get_category_totals():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        
        def extract_cat(item_str):
            item_str = str(item_str)
            if 'total' in item_str.lower(): return None
            if ':' in item_str:
                part = item_str.split(':')[0]
                if ']' in part: return part.split(']')[1].strip().capitalize()
                return part.strip().capitalize()
            return "Others"
            
        df['Extracted_Category'] = df['Item'].apply(extract_cat)
        df = df.dropna(subset=['Extracted_Category'])
        cat_summary = df.groupby('Extracted_Category')['Debit'].sum().to_dict()
        return cat_summary
    except: return {}

def process_voice(text):
    if not text: return "Others", "", ""
    raw = text.lower().replace('.', '').replace(',', '')
    nums = re.findall(r'\d+', raw)
    amt = nums[0] if nums else ""
    desc = re.sub(r'\d+', '', raw).strip()
    category = "Others"
    if any(x in raw for x in ["food", "ഭക്ഷണം", "ചായ"]): category = "Food"
    elif any(x in raw for x in ["shop", "കട"]): category = "Shop"
    elif any(x in raw for x in ["fish", "മീൻ"]): category = "Fish"
    elif any(x in raw for x in ["travel", "യാത്ര"]): category = "Travel"
    return category, amt, desc

def create_pdf(df):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align='C')
        pdf.ln(10)
        cols = df.columns.tolist()
        pdf.set_font("Arial", 'B', 10)
        for col in cols: pdf.cell(38, 10, txt=str(col), border=1)
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            for col in cols:
                val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(38, 10, txt=val, border=1)
            pdf.ln()
        return pdf.output(dest='S').encode('latin-1')
    except: return None

def parse_mixed_dates(date_series):
    parsed_dates = []
    for val in date_series:
        val_str = str(val).strip()
        dt = pd.NaT
        try:
            dt = pd.to_datetime(val_str, errors='coerce')
            if not pd.isna(dt) and dt.year == 2026 and dt.month < 4:
                dt = datetime(2026, dt.day, dt.month)
        except: pass
        if pd.isna(dt):
            try: dt = pd.to_datetime(val_str, dayfirst=True, errors='coerce')
            except: pass
        parsed_dates.append(dt)
    return pd.Series(parsed_dates)

if not st.session_state.auth:
    st.title("🔐 PAICHI EXPENSES LOGIN")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied!")
else:
    curr_user = st.session_state.user
    t_in, t_out, balance = get_totals()
    
    st.markdown(f'''<div class="balance-banner">
        <span style="font-size:22px; color: #E0B0FF; letter-spacing: 1px;">Available Balance</span><br>
        <span style="font-size:45px; color:#FFD700; font-weight:bold; text-shadow: 0px 0px 10px rgba(255,215,0,0.3);">₹{balance:,.2f}</span>
    </div>''', unsafe_allow_html=True)

    if curr_user == "shabana": 
        menu_options = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    else: 
        menu_options = ["🏠 Dashboard", "💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker"]

    page = st.sidebar.radio("Menu", menu_options)
    if st.sidebar.button("Logout"): 
        st.session_state.auth = False
        st.rerun()

    # --- PAGES ---
    if page == "🏠 Dashboard":
        st.title("Financial Overview")
        st.markdown(f"""<div class="purple-box" style="display: flex; justify-content: space-around; align-items: center;">
            <div><h4 style="color: #aaa; margin:0;">Total Credit</h4><h2 style="color: #2DE35A; margin:5px 0 0 0;">₹{t_in:,.2f}</h2></div>
            <div style="border-left: 1px solid rgba(255,255,255,0.1); height: 50px;"></div>
            <div><h4 style="color: #aaa; margin:0;">Total Debit</h4><h2 style="color: #FF4B4B; margin:5px 0 0 0;">₹{t_out:,.2f}</h2></div>
        </div>""", unsafe_allow_html=True)
        
        st.subheader("🗂️ Categorywise Expense Breakdown")
        cat_data = get_category_totals()
        if cat_data:
            cols = st.columns(3)
            for idx, (c_name, c_amount) in enumerate(cat_data.items()):
                if c_amount > 0 and c_name:
                    with cols[idx % 3]:
                        st.markdown(f"""<div class="category-box">
                            <span style="font-size:16px; color:#aaa;">Total {c_name}</span><br>
                            <span style="font-size:24px; color:#FFF; font-weight:bold;">₹{c_amount:,.2f}</span>
                        </div>""", unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Smart Voice Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_v8')
        v_cat, v_amt, v_desc = process_voice(v_raw)
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Description", value=v_desc)
            am_str = st.text_input("Amount", value=str(v_amt))
            cat = st.selectbox("Category", ["Food", "Shop", "Fish", "Travel", "Rent", "Others"])
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE & NOTIFY"):
                try:
                    am = float(am_str.strip().replace(',', ''))
                    d, c = (am, 0) if ty == "Debit" else (0, am)
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"), 
                        "entry.2013476337": f"[{curr_user.capitalize()}] {cat}: {it}", 
                        "entry.1460982454": d, 
                        "entry.1221658767": c
                    }
                    send_to_google_async(payload)
                    send_whatsapp_auto(f"✅ *Paichi Entry*\n📝 Item: {it}\n💰 Amt: ₹{am}\n👤 User: {curr_user}")
                    st.success("Saved! ✅")
                except: st.error("Error! Please enter a valid number for amount.")

    elif page == "📅 Calendar":
        st.title("AI Premium P&L Calendar 📅")
        try:
            df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
            df.columns = df.columns.str.strip()
            df['Date'] = parse_mixed_dates(df['Date'])
            df = df.dropna(subset=['Date'])
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
            
            daily_summary = df.groupby(df['Date'].dt.strftime('%Y-%m-%d')).agg({'Debit': 'sum', 'Credit': 'sum'}).reset_index()
            
            calendar_events = []
            for _, row in daily_summary.iterrows():
                if row['Credit'] > 0:
                    calendar_events.append({
                        "id": f"credit_{row['Date']}",
                        "title": f"📈 +₹{row['Credit']:,.0f}",
                        "start": row['Date'],
                        "backgroundColor": "rgba(45, 227, 90, 0.15)",
                        "borderColor": "#2DE35A",
                        "textColor": "#2DE35A"
                    })
                if row['Debit'] > 0:
                    calendar_events.append({
                        "id": f"debit_{row['Date']}",
                        "title": f"📉 -₹{row['Debit']:,.0f}",
                        "start": row['Date'],
                        "backgroundColor": "rgba(255, 75, 75, 0.15)",
                        "borderColor": "#FF4B4B",
                        "textColor": "#FF4B4B"
                    })
            
            calendar_options = {
                "headerToolbar": {"left": "prev,next today", "center": "title", "right": ""},
                "initialView": "dayGridMonth",
                "selectable": True,
            }
            
            cal_data = calendar(events=calendar_events, options=calendar_options, key="pnl_calendar_v2")
            
            if cal_data.get("eventClick"):
                clicked_date = cal_data["eventClick"]["event"]["start"].split("T")[0]
                clicked_dt = pd.to_datetime(clicked_date)
                
                st.markdown("---")
                st.subheader(f"📋 Details for {clicked_dt.strftime('%d %B %Y')}")
                
                day_entries = df[df['Date'].dt.strftime('%Y-%m-%d') == clicked_date].copy()
                if not day_entries.empty:
                    day_entries['Date'] = day_entries['Date'].dt.strftime('%d/%m/%Y')
                    st.dataframe(day_entries[['Date', 'Item', 'Debit', 'Credit']].reset_index(drop=True), use_container_width=True)
                else:
                    st.info("No details found for this day.")
                    
        except Exception as e:
            st.error("കലണ്ടർ ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല!")

    elif page == "📊 Report" or page == "🔍 History":
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Date'] = parse_mixed_dates(df['Date'])
        # ഇവിടെ ഫിൽറ്റർ മാറ്റിയതിനാൽ എല്ലാ മാസങ്ങളും പൂർണ്ണമായി ലിസ്റ്റ് ചെയ്യും
        df = df.dropna(subset=['Date'])
        df['Month'] = df['Date'].dt.strftime('%B %Y')
        months = df.sort_values(by='Date', ascending=False)['Month'].unique()

        if page == "📊 Report":
            st.title("Monthly Expense Analysis")
            if len(months) == 0: st.warning("No data found in Google Sheets!")
            else:
                sel_month = st.selectbox("Select Month", months)
                monthly_df = df[df['Month'] == sel_month].copy()
                monthly_df['Debit'] = pd.to_numeric(monthly_df['Debit'], errors='coerce').fillna(0)
                monthly_df['Credit'] = pd.to_numeric(monthly_df['Credit'], errors='coerce').fillna(0)
                m_total_debit = monthly_df['Debit'].sum()
                m_total_credit = monthly_df['Credit'].sum()
                m_savings = m_total_credit - m_total_debit
                
                col1, col2, col3 = st.columns(3)
                with col1: st.markdown(f'<div class="purple-box"><h3 style="color: #2DE35A;">{sel_month} Total Credit</h3><h1 style="color: #2DE35A;">₹{m_total_credit:,.2f}</h1></div>', unsafe_allow_html=True)
                with col2: st.markdown(f'<div class="purple-box"><h3 style="color: #FF4B4B;">{sel_month} Total Expense</h3><h1 style="color: #FF4B4B;">₹{m_total_debit:,.2f}</h1></div>', unsafe_allow_html=True)
                with col3: st.markdown(f'<div class="purple-box"><h3 style="color: #FFD700;">{sel_month} Net Savings</h3><h1 style="color: #FFD700;">₹{m_savings:,.2f}</h1></div>', unsafe_allow_html=True)

                if m_total_debit > 0:
                    monthly_df['Category_Label'] = monthly_df['Item'].apply(lambda x: x.split(':')[0] if ':' in x else 'Others')
                    fig = px.pie(monthly_df[monthly_df['Debit'] > 0], values='Debit', names='Category_Label', hole=0.4, title=f"{sel_month} Expense Split")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                    
                st.subheader(f"📋 {sel_month} Detailed Transactions")
                clean_table_df = monthly_df.drop(columns=['Month'], errors='ignore')
                csv_data = clean_table_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Download Excel/CSV Report", data=csv_data, file_name=f"Report_{sel_month.replace(' ', '_')}.csv", mime="text/csv")
                clean_table_df['Date'] = clean_table_df['Date'].dt.strftime('%d/%m/%Y')
                st.dataframe(clean_table_df.iloc[::-1], use_container_width=True)

        elif page == "🔍 History":
            st.title("Transaction History")
            if len(months) == 0: st.warning("No transactions found!")
            else:
                sel_hist_month = st.selectbox("Select Month for History", months, key="history_month_select")
                filtered_history = df[df['Month'] == sel_hist_month].copy()
                clean_hist_df = filtered_history.drop(columns=['Month'], errors='ignore')
                csv_hist_data = clean_hist_df.to_csv(index=False).encode('utf-8')
                
                col_pdf, col_csv = st.columns(2)
                with col_pdf:
                    pdf_bytes = create_pdf(clean_hist_df)
                    if pdf_bytes: st.download_button(f"📄 Download {sel_hist_month} PDF", pdf_bytes, f"History_{sel_hist_month.replace(' ', '_')}.pdf", "application/pdf")
                with col_csv: st.download_button(label=f"📥 Download {sel_hist_month} CSV (Excel)", data=csv_hist_data, file_name=f"History_{sel_hist_month.replace(' ', '_')}.csv", mime="text/csv")
                clean_hist_df['Date'] = clean_hist_df['Date'].dt.strftime('%d/%m/%Y')
                st.dataframe(clean_hist_df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management")
        with st.form("debt_form"):
            n = st.text_input("Name")
            a = st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["vagiyade", "
