import streamlit as st
from google import genai

# ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI TRADING HUB", layout="wide")

# സൈഡ്ബാർ
st.sidebar.title("📈 PAICHI HUB")
st.sidebar.markdown("[💬 Contact Me on WhatsApp](https://wa.me/message/CILS6MWZTN1)")
page = st.sidebar.radio("Go to:", ["Dashboard", "AI Learning Zone", "Trading Calc", "Trading Bot"])

# API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "AIzaSyCs2bRTki97CGu_Jgn67U_JAHdt1c1It-8"

client = genai.Client(api_key=api_key)

if page == "Dashboard":
    st.title("🚀 PAICHI TRADING HUB")
    st.write("സ്വാഗതം ഫൈസൽ! നിന്റെ ആപ്പ് ഇപ്പോൾ റെഡിയാണ്.")
    st.metric("Focus", "Crude Oil & Nifty")

elif page == "AI Learning Zone":
    st.title("🤖 AI Assistant")
    user_input = st.text_input("എന്താണ് പഠിക്കേണ്ടത്?")
    if st.button("ചോദിക്കുക"):
        if user_input:
            response = client.models.generate_content(model="gemini-1.5-flash", contents=user_input)
            st.write(response.text)

elif page == "Trading Calc":
    st.title("💰 Profit & Loss")
    buy = st.number_input("Buy Price:", value=0.0)
    sell = st.number_input("Sell Price:", value=0.0)
    qty = st.number_input("Quantity:", value=1)
    if st.button("Calculate"):
        pnl = (sell - buy) * qty
        st.success(f"ലാഭം/നഷ്ടം: ₹{pnl}")

elif page == "Trading Bot":
    st.title("📊 Market Levels")
    st.info("നിഫ്റ്റി, ബാങ്ക് നിഫ്റ്റി ലെവലുകൾ ഇവിടെ വരും.")
