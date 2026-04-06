import streamlit as st  # ഇവിടെ 'i' ചെറിയക്ഷരമാക്കി
from google import genai

# API key സുരക്ഷിതമായി എടുക്കുക
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "AIzaSyDPVdluZOQjg4lBHh5K0XfdAYaCzmhf0Q4" # നിന്റെ കീ ഇവിടെ നൽകാം

st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# പുതിയ ജെമിനി ക്ലയന്റ് സെറ്റപ്പ്
client = genai.Client(api_key=api_key)

# മോഡൽ പേര് (ഏറ്റവും പുതിയത്)
MODEL_NAME = "gemini-2.0-flash" 

st.subheader("🤖 Ask Gemini about Python")
user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ")

if st.button("ചോദിക്കുക"):
    if user_input:
        with st.spinner("ജെമിനി മറുപടി തരുന്നു..."):
            try:
                # പുതിയ ലൈബ്രറിയിലെ രീതി ഇതാണ്
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
