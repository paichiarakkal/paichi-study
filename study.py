import streamlit as st
from google import genai

# API key സുരക്ഷിതമായി എടുക്കുക (deploy-ൽ st.secrets ഉപയോഗിക്കുക)
# local testing-ന് API key നേരിട്ട് എഴുതാം (പക്ഷേ അപകടകരം)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "YOUR_API_KEY_HERE"   # local test-ന് മാത്രം

st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# പുതിയ ജെമിനി ക്ലയന്റ്
client = genai.Client(api_key=api_key)

# ഏതെങ്കിലും ഒരു പ്രവർത്തിക്കുന്ന മോഡൽ തിരഞ്ഞെടുക്കുക
# (ഇവ free tier-ൽ ലഭ്യമാണ്)
MODEL_NAME = "gemini-2.0-flash-exp"   # അല്ലെങ്കിൽ "gemini-1.5-flash"

st.subheader("🤖 Ask Gemini about Python")
user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ")

if st.button("ചോദിക്കുക"):
    if user_input:
        with st.spinner("ജെമിനി മറുപടി തരുന്നു..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=user_input
                )
                st.success("AI മറുപടി:")
                st.write(response.text)
            except Exception as e:
                st.error(f"ക്ഷമിക്കണം, ഒരു തകരാർ സംഭവിച്ചു: {str(e)}")
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")
