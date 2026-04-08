import streamlit as st
import random

# ആപ്പിന്റെ സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI Study Hub", layout="wide")

# ടൈറ്റിൽ
st.title("🎓 PAICHI Family Education Portal")

# സൈഡ്ബാർ മെനു - പുതിയ സെക്ഷനുകൾ ഇവിടെ ചേർത്തു
st.sidebar.title("📌 Main Menu")
option = st.sidebar.selectbox("Choose Section", 
    ["Home", "SSLC Student", "Plus Two Student", "Photo Gallery", "Maths Lab (Loops)", "Study Resources"])

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

# 1. ഹോം പേജ്
if option == "Home":
    st.header("സ്വാഗതം ഫൈസൽ!")
    st.write("പൈത്തൺ പഠനത്തിന്റെ ഭാഗമായി നീ നിർമ്മിച്ച നിന്റെ സ്വന്തം ഫാമിലി ആപ്പ് ആണിത്.")
    st.image("https://img.freepik.com/free-vector/graduation-cap-with-diploma-scroll-realistic-style_1284-18155.jpg", width=300)

# 2. SSLC സെക്ഷൻ
elif option == "SSLC Student":
    st.header("📝 SSLC Mark Entry")
    name = st.text_input("Student Name")
    col1, col2 = st.columns(2)
    with col1:
        maths = st.number_input("Maths (0-100)", 0, 100)
        science = st.number_input("Science (0-100)", 0, 100)
    with col2:
        english = st.number_input("English (0-100)", 0, 100)
        malayalam = st.number_input("Malayalam (0-100)", 0, 100)
    
    if st.button("Generate Result"):
        total = maths + science + english + malayalam
        average = total / 4
        st.divider()
        st.success(f"ഹലോ {name}, നിന്റെ ടോട്ടൽ മാർക്ക് {total} ആണ്.")
        st.write(f"Your Progress: {average:.1f}%")
        st.progress(int(average))
        if average >= 80: st.balloons()

# 3. പ്ലസ് ടു സെക്ഷൻ
elif option == "Plus Two Student":
    st.header("📚 Plus Two Grade Tracker")
    name_p2 = st.text_input("Student Name")
    grades = ["A+", "A", "B+", "B", "C", "D+"]
    col1, col2 = st.columns(2)
    with col1:
        physics = st.selectbox("Physics", grades)
        chemistry = st.selectbox("Chemistry", grades)
    with col2:
        maths_p2 = st.selectbox("Maths", grades)
        biology = st.selectbox("Biology", grades)
    
    if st.button("Show My Grades"):
        st.success(f"ഹലോ {name_p2}, നിന്റെ ഗ്രേഡുകൾ റെഡിയാണ്!")
        st.write(f"📍 Physics: **{physics}** | Chemistry: **{chemistry}**")
        st.write(f"📍 Maths: **{maths_p2}** | Biology: **{biology}**")
        st.snow()

# 4. ഫോട്ടോ ഗാലറി
elif option == "Photo Gallery":
    st.header("📸 Family Memories")
    st.write("നമ്മുടെ പ്രിയപ്പെട്ട നിമിഷങ്ങൾ.")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://img.freepik.com/free-photo/family-celebrating-ramadan-together_23-2151240097.jpg", caption="Family Time ❤️")
    with col2:
        st.image("https://img.freepik.com/free-photo/workplace-with-laptop-charts-office_23-2148443360.jpg", caption="Learning Python 🐍")

# 5. മാത്സ് ലാബ് (Loops പഠിക്കാൻ)
elif option == "Maths Lab (Loops)":
    st.header("🔢 Multiplication Table Generator")
    num = st.number_input("ഏത് സംഖ്യയുടെ പട്ടിക വേണം?", value=5)
    if st.button("പട്ടിക കാണുക"):
        for i in range(1, 11):
            st.write(f"{num} x {i} = **{num * i}**")

# 6. സ്റ്റഡി റിസോഴ്‌സസ് (പുതിയ സെക്ഷൻ)
elif option == "Study Resources":
    st.header("📖 Textbook Downloads")
    st.write("കേരള സിലബസ് പാഠപുസ്തകങ്ങൾ താഴെയുള്ള ബട്ടണുകൾ വഴി ഡൗൺലോഡ് ചെയ്യാം:")
    st.link_button("Download SSLC Books", "https://samagra.kite.kerala.gov.in/#/textbook/view")
    st.link_button("Download Plus Two Books", "https://samagra.kite.kerala.gov.in/#/textbook/view")
    st.info("ഈ ലിങ്ക് തുറന്ന് നിനക്ക് വേണ്ട ക്ലാസ്സും മീഡിയവും തിരഞ്ഞെടുത്താൽ മതി.")

# ഫൂട്ടർ
st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ by Faisal")
