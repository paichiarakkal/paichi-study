import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# നിന്റെ പുതിയ API Key ഇവിടെ നൽകുക
genai.configure(api_key="AIzaSyDPVdluZOQjg4lBHh5K0XfdAYaCzmhf0Q4")

# മോഡൽ പേര് കൃത്യമായി നൽകുന്നു
model = genai.GenerativeModel('gemini-1.5-flash')

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
                st.error(f"തകരാർ: {str(e)}")
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")
