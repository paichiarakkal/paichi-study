Import streamlit as st
import google.generativeai as genai

# API key Streamlit secrets-ൽ നിന്ന് എടുക്കുക (deploy ചെയ്യുമ്പോൾ)
# local testing-ന് `.env` ഉപയോഗിക്കുക
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "YOUR_API_KEY_HERE"   # local testing-ന് മാത്രം

st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# Gemini മോഡൽ ഇനീഷ്യലൈസ് ചെയ്യുക
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')   # ശരിയായ മോഡൽ പേര്

st.subheader("🤖 Ask Gemini about Python")
user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ")

if st.button("ചോദിക്കുക"):
    if user_input:
        with st.spinner("ജെമിനി മറുപടി തരുന്നു..."):
            try:
                response = model.generate_content(user_input)
                st.success("AI മറുപടി:")
                st.write(response.text)
            except Exception as e:
                st.error(f"ക്ഷമിക്കണം, ഒരു തകരാർ സംഭവിച്ചു: {str(e)}")
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")
