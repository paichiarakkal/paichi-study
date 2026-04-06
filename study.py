import streamlit as st
import google.generativeai as genai

# 1. സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# 2. ജെമിനി സെറ്റപ്പ് (പുതിയ കീ ഉപയോഗിക്കുന്നു)
# 'gemini-1.5-flash' എന്നതിന് പകരം 'models/gemini-1.5-flash' എന്ന് നൽകി നോക്കാം
genai.configure(api_key="AIzaSyDPVdluZOQjg4lBHh5K0XfdAYaCzmhf0Q4")
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. ചോദ്യം ചോദിക്കാനുള്ള ബോക്സ്
st.subheader("🤖 Ask Gemini about Python")
user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ")

if st.button("ചോദിക്കുക"):
    if user_input:
        with st.spinner("ജെമിനി മറുപടി തരുന്നു..."):
            try:
                # നേരിട്ട് ജനറേറ്റ് ചെയ്യാൻ ശ്രമിക്കുന്നു
                response = model.generate_content(user_input)
                st.success("AI മറുപടി:")
                st.write(response.text)
            except Exception as e:
                # എന്തെങ്കിലും എറർ വന്നാൽ അത് കൃത്യമായി കാണിക്കാൻ
                st.error(f"ക്ഷമിക്കണം, ഒരു ചെറിയ സാങ്കേതിക തകരാർ: {str(e)}")
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")
