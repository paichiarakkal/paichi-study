import streamlit as st
from google import genai

# Secrets-ൽ നിന്ന് കീ എടുക്കുന്നു
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "AIzaSyCs2bRTki97CGu_Jgn67U_JAHdt1c1It-8"

st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# പുതിയ ക്ലയന്റ് സെറ്റപ്പ്
client = genai.Client(api_key=api_key)

# 1.5 Flash ആണ് കൂടുതൽ സ്റ്റേബിൾ
MODEL_NAME = "gemini-1.5-flash" 

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
                st.error(f"തകരാർ സംഭവിച്ചു: {str(e)}")
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")
