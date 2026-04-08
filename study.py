import streamlit as st

st.set_page_config(page_title="Family Study Tracker", layout="wide")
st.title("🎓 Family Education Portal")

# ഒരു സൈഡ്ബാർ മെനു ഉണ്ടാക്കാം
option = st.sidebar.selectbox("Choose Student", ["Select Student", "SSLC Student", "+2 Student"])

if option == "SSLC Student":
    st.header("📝 SSLC Mark Entry")
    # കുട്ടിയുടെ പേര് ചോദിക്കുന്നു
    name = st.text_input("fiza")
    # സ്റ്റഡി ടിപ്‌സ് സെക്ഷൻ
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Study Zone")
show_tips = st.sidebar.button("Get a Study Tip")

tips = [
    "📌 **Pomodoro Technique:** 25 മിനിറ്റ് പഠിക്കുക, 5 മിനിറ്റ് ബ്രേക്ക് എടുക്കുക.",
    "💧 **Stay Hydrated:** പഠിക്കുമ്പോൾ നന്നായി വെള്ളം കുടിക്കുന്നത് ഏകാഗ്രത കൂട്ടും.",
    "📝 **Write it down:** വായിക്കുന്നതിനേക്കാൾ കൂടുതൽ എഴുതി പഠിക്കാൻ ശ്രമിക്കുക.",
    "📵 **No Distractions:** പഠിക്കുമ്പോൾ ഫോൺ ദൂരേക്ക് മാറ്റി വെക്കുക.",
    "😴 **Sleep Well:** നല്ല ഉറക്കം ഓർമ്മശക്തി വർദ്ധിപ്പിക്കും."
]

if show_tips:
    import random
    st.sidebar.info(random.choice(tips))
    # മാർക്കുകൾ വാങ്ങുന്നു
    maths = st.number_input("Maths (Out of 100)", 0, 100)
    science = st.number_input("Science (Out of 100)", 0, 100)
    english = st.number_input("English (Out of 100)", 0, 100)
    
    if st.button("Generate Result"):
        total = maths + science + english
        average = total / 3
        st.success(f"ഹലോ {name}, നിന്റെ ടോട്ടൽ മാർക്ക് {total} ആണ്.")
        st.info(f"ശരാശരി (Average): {average:.2f}%")
        # മാർക്കിന്റെ ശതമാനം കാണിക്കാൻ ഒരു പ്രോഗ്രസ് ബാർ
        st.write(f"Your Progress: {average:.1f}%")
        st.progress(int(average)) # 0 മുതൽ 100 വരെയുള്ള ശതമാനം കാണിക്കും
elif option == "+2 Student":
    st.header("📚 Plus Two Grade Tracker")
    # ഇവിടെ നമുക്ക് ഗ്രേഡുകൾ നൽകാം
    physics = st.selectbox("Physics Grade", ["A+", "A", "B+", "B", "C"])
    chemistry = st.selectbox("Chemistry Grade", ["A+", "A", "B+", "B", "C"])
    
    if st.button("Show Status"):
        st.write(f"Physics: {physics}")
        st.write(f"Chemistry: {chemistry}")
        st.balloons() # ഒരു ചെറിയ ആനിമേഷൻ!
