import streamlit as st
from google import genai

# 1. ആപ്പിന്റെ പ്രാഥമിക സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI TRADING HUB", layout="wide")

# 2. സൈഡ്‌ബാർ മെനു സെറ്റപ്പ്
st.sidebar.title("📈 PAICHI HUB")
page = st.sidebar.radio("Go to:", ["Dashboard", "AI Learning Zone", "Trading Calc", "Trading Bot"])

# 3. ഗൂഗിൾ ജെമിനി AI സെറ്റപ്പ്
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # നിന്റെ പുതിയ API Key ഇവിടെ നൽകുന്നു
    api_key = "AIzaSyCs2bRTki97CGu_Jgn67U_JAHdt1c1It-8"

client = genai.Client(api_key=api_key)

# 4. ഓരോ പേജിന്റെയും ഉള്ളടക്കം (Logic)

# --- ഡാഷ്ബോർഡ് പേജ് ---
if page == "Dashboard":
    st.title("🚀 PAICHI TRADING HUB")
    st.write("നിന്റെ സ്വന്തം ട്രേഡിംഗ് പ്ലാറ്റ്‌ഫോമിലേക്ക് സ്വാഗതം ഫൈസൽ!")
    
    col1, col2 = st.columns(2)
    col1.metric("Today's Focus", "Crude Oil")
    col2.metric("Target", "Pro Trader")
    st.info("നമുക്ക് ഒരുമിച്ച് പൈത്തണും ട്രേഡിംഗും പഠിക്കാം.")

# --- AI ലേണിംഗ് സെക്ഷൻ ---
elif page == "AI Learning Zone":
    st.title("🤖 AI Learning Assistant")
    st.write("പൈത്തണിനെക്കുറിച്ചോ ട്രേഡിംഗിനെക്കുറിച്ചോ ഉള്ള സംശയങ്ങൾ ഇവിടെ ചോദിക്കാം.")
    
    user_input = st.text_input("നിന്റെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യൂ:")
    if st.button("ചോദിക്കുക"):
        if user_input:
            with st.spinner("ജെമിനി മറുപടി നൽകുന്നു..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=user_input
                    )
                    st.success("മറുപടി:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"ക്ഷമിക്കണം, ഒരു തകരാർ: {str(e)}")

# --- പ്രോഫിറ്റ് & ലോസ് കാൽക്കുലേറ്റർ ---
elif page == "Trading Calc":
    st.title("💰 Profit & Loss Calculator")
    
    buy_price = st.number_input("വാങ്ങിയ വില (Buy Price):", value=0.0)
    sell_price = st.number_input("വിറ്റ വില (Sell Price):", value=0.0)
    quantity = st.number_input("ക്വാണ്ടിറ്റി (Quantity):", value=1)
    
    if st.button("Calculate"):
        pnl = (sell_price - buy_price) * quantity
        if pnl > 0:
            st.success(f"അടിപൊളി! നിനക്ക് ₹{pnl} ലാഭമുണ്ട്. 📈")
        elif pnl < 0:
            st.error(f"സാരമില്ല, ₹{abs(pnl)} നഷ്ടമാണ്. അടുത്ത തവണ ശരിയാക്കാം. 📉")
        else:
            st.warning("ലാഭവും നഷ്ടവും ഇല്ല (Break Even).")

# --- ട്രേഡിംഗ് ബോട്ട് (നിഫ്റ്റി ലെവൽസ്) ---
elif page == "Trading Bot":
    st.title("📊 Nifty & Bank Nifty")
    st.write("ഇവിടെ നമുക്ക് മാർക്കറ്റ് ലെവലുകൾ നോക്കാം.")
    
    st.subheader("Today's Analysis")
    st.write("നിഫ്റ്റി, ബാങ്ക് നിഫ്റ്റി എന്നിവയുടെ പ്രധാന സപ്പോർട്ട് (Support), റെസിസ്റ്റൻസ് (Resistance) ലെവലുകൾ ഇവിടെ കാണാം.")
    st.info("ലൈവ് ഡാറ്റ ഫീഡ് ഉടനെ ലഭ്യമാകും!")
