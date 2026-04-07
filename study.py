import streamlit as st
from google import genai

# 1. സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI TRADING HUB", layout="wide")

# 2. സൈഡ്‌ബാർ മെനു
st.sidebar.title("📈 PAICHI HUB")
page = st.sidebar.radio("Go to:", ["Dashboard", "AI Learning Zone", "Trading Calc","Trading Bot"])

# 3. API Key സെറ്റപ്പ്
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "AIzaSyCs2bRTki97CGu_Jgn67U_JAHdt1c1It-8"

client = genai.Client(api_key=api_key)

# 4. പേജുകളുടെ ലോജിക്
if page == "Dashboard":
    st.title("🚀 PAICHI TRADING HUB")
    st.write("നിന്റെ സ്വന്തം ട്രേഡിംഗ് പ്ലാറ്റ്‌ഫോമിലേക്ക് സ്വാഗതം!")
    col1, col2 = st.columns(2)
    col1.metric("Today's Focus", "Crude Oil")
    col2.metric("Target", "Pro Trader")

elif page == "AI Learning Zone":
    st.title("🤖 AI Learning Assistant")
    user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ചോദിക്കാം:")
    if st.button("ചോദിക്കുക"):
        if user_input:
            response = client.models.generate_content(model="gemini-1.5-flash", contents=user_input)
            st.write(response.text)

elif page == "Trading Calc":
    st.title("💰 Profit & Loss Calculator")
    buy = st.number_input("വാങ്ങിയ വില:", value=0.0)
    sell = st.number_input("വിറ്റ വില:", value=0.0)
    qty = st.number_input("ക്വാണ്ടിറ്റി:", value=1)
    if st.button("Calculate"):
        pnl = (sell - buy) * qty
        if pnl > 0:
        
            st.success(f"ലാഭം: ₹{pnl}")
        else:
            st.error(f"നഷ്ടം: ₹{abs(pnl)}"
                     
elif page=="Trading Bot":
st.title("nifty bank nifty ")
