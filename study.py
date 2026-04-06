import streamlit as st
import google.generativeai as genai

# 1. സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Academy", layout="wide")
st.title("🎓 PAICHI ACADEMY")
st.write("ഇവിടെ നമുക്ക് പൈത്തൺ പഠിക്കാം!")

# 2. ജെമിനി സെറ്റപ്പ് (നിന്റെ API Key താഴെ നൽകിയിരിക്കുന്നു)
genai.configure(api_key="AIzaSyBzKD8uPmnF_agwO5-C7wMDDXXcAUlw8U4")
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. ചോദ്യം ചോദിക്കാനുള്ള ബോക്സ്
st.subheader("🤖 Ask Gemini about Python")
user_input = st.text_input("നിന്റെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ (ഉദാഹരണത്തിന്: What is a Variable?)")

if st.button("ചോദിക്കുക"):
    if user_input:
        with st.spinner("ജെമിനി മറുപടി തരുന്നു..."):
            response = model.generate_content(user_input)
            st.success("AI മറുപടി:")
            st.write(response.text)
    else:
        st.warning("ദയവായി ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ!")

# 4. പൈത്തൺ നോട്ട്സ്
st.divider()
st.subheader("📝 My Python Learning")
st.code("""
# ഇന്ന് പഠിച്ച കാര്യങ്ങൾ:
# 1. API Key ഉപയോഗിച്ച് AI-യെ ആപ്പിൽ കൊണ്ടുവന്നു.
# 2. st.text_input ഉപയോഗിച്ച് ചോദ്യം ചോദിച്ചു.
""")
