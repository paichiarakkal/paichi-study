import streamlit as st
import google.generativeai as genai

# 1. സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# 2. പുതിയ ജെമിനി സെറ്റപ്പ്
# API Key കൃത്യമാണെന്ന് ഉറപ്പുവരുത്തുക
genai.configure(api_key="AIzaSyDPVdluZOQjg4lBHh5K0XfdAYaCzmhf0Q4")

# മോഡൽ പേര് ഇങ്ങനെ മാറ്റി നൽകുന്നു
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 3. ചാറ്റ് ബോക്സ്
st.subheader("🤖 Ask Gemini about Python")
user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ")

if st.button("ചോദിക്കുക"):
    if user_input:
        with st.spinner("ജെമിനി മറുപടി തരുന്നു..."):
            try:
                # മറുപടി ജനറേറ്റ് ചെയ്യുന്നു
                response = model.generate_content(user_input)
                st.success("AI മറുപടി:")
                st.write(response.text)
            except Exception as e:
                st.error(f"ക്ഷമിക്കണം, ഒരു തകരാർ സംഭവിച്ചു: {str(e)}")
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")
