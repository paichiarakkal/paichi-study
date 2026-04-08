import streamlit as st
import random

# ആപ്പിന്റെ പേരും ലേഔട്ടും സെറ്റ് ചെയ്യുന്നു
st.set_page_config(page_title="Family Education Portal", layout="wide")

# ടൈറ്റിൽ
st.title("🎓 Family Education Portal")

# സൈഡ്ബാർ മെനു
st.sidebar.title("📌 Menu")
option = st.sidebar.selectbox("Choose Section", ["Home", "SSLC Student", "Plus Two Student"])

# സ്റ്റഡി ടിപ്‌സ് ലിസ്റ്റ്
tips = [
    "📌 **Pomodoro Technique:** 25 മിനിറ്റ് പഠിക്കുക, 5 മിനിറ്റ് ബ്രേക്ക് എടുക്കുക.",
    "💧 **Stay Hydrated:** പഠിക്കുമ്പോൾ നന്നായി വെള്ളം കുടിക്കുന്നത് ഏകാഗ്രത കൂട്ടും.",
    "📝 **Write it down:** വായിക്കുന്നതിനേക്കാൾ കൂടുതൽ എഴുതി പഠിക്കാൻ ശ്രമിക്കുക.",
    "📵 **No Distractions:** പഠിക്കുമ്പോൾ ഫോൺ ദൂരേക്ക് മാറ്റി വെക്കുക.",
    "😴 **Sleep Well:** നല്ല ഉറക്കം ഓർമ്മശക്തി വർദ്ധിപ്പിക്കും.",
    "🍎 **Healthy Food:** പഠനത്തിനിടയിൽ പഴങ്ങൾ കഴിക്കുന്നത് ഉന്മേഷം നൽകും."
]

# സൈഡ്ബാറിൽ ടിപ്‌സ് ബട്ടൺ
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Study Zone")
if st.sidebar.button("Get a Study Tip"):
    st.sidebar.info(random.choice(tips))

# ഹോം പേജ്
if option == "Home":
    st.header("സ്വാഗതം!")
    st.write("ഈ ആപ്പ് ഉപയോഗിച്ച് നിനക്ക് മാർക്കുകൾ ട്രാക്ക് ചെയ്യാനും പഠനത്തിനുള്ള ടിപ്‌സ് നേടാനും കഴിയും.")
    st.image("https://img.freepik.com/free-vector/graduation-cap-with-diploma-scroll-realistic-style_1284-18155.jpg", width=300)

# SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Mark Entry")
    name = st.text_input("fiza")
    
    col1, col2 = st.columns(2)
    with col1:
        maths = st.number_input("Maths (Out of 100)", 0, 100)
        science = st.number_input("Science (Out of 100)", 0, 100)
    with col2:
        english = st.number_input("English (Out of 100)", 0, 100)
        malayalam = st.number_input("Malayalam (Out of 100)", 0, 100)
    
    if st.button("Generate Result"):
        total = maths + science + english + malayalam
        average = total / 4
        
        st.divider()
        st.success(f"ഹലോ {name}, നിന്റെ ടോട്ടൽ മാർക്ക് {total} ആണ്.")
        st.write(f"Your Progress: {average:.1f}%")
        st.progress(int(average))
        
        if average >= 80:
            st.balloons()
            st.write("🌟 **അടിപൊളി! മികച്ച പ്രകടനം.**")
        elif average >= 40:
            st.write("👍 **നന്നായിട്ടുണ്ട്! ഇനിയും മെച്ചപ്പെടുത്താം.**")
        else:
            st.write("💪 **വിഷമിക്കേണ്ട, കൂടുതൽ പരിശ്രമിച്ചാൽ അടുത്ത തവണ വിജയിക്കാം!**")

# പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Grade Tracker")
    name_p2 = st.text_input("fammu")
    
    col1, col2 = st.columns(2)
    with col1:
        physics = st.selectbox("Physics Grade", ["A+", "A", "B+", "B", "C", "D+"])
        chemistry = st.selectbox("Chemistry Grade", ["A+", "A", "B+", "B", "C", "D+"])
    with col2:
        maths_p2 = st.selectbox("Maths Grade", ["A+", "A", "B+", "B", "C", "D+"])
        biology = st.selectbox("Biology Grade", ["A+", "A", "B+", "B", "C", "D+"])
    
    if st.button("Show My Grades"):
        st.success(f"ഹലോ {name_p2}, നിന്റെ ഗ്രേഡുകൾ താഴെ നൽകുന്നു:")
        st.write(f"📍 Physics: **{physics}**")
        st.write(f"📍 Chemistry: **{chemistry}**")
        st.write(f"📍 Maths: **{maths_p2}**")
        st.write(f"📍 Biology: **{biology}**")
        st.snow() # മഞ്ഞ് വീഴുന്ന ആനിമേഷൻ!

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
