import streamlit as st

st.set_page_config(page_title="Family Study Tracker", layout="wide")
st.title("🎓 Family Education Portal")

# ഒരു സൈഡ്ബാർ മെനു ഉണ്ടാക്കാം
option = st.sidebar.selectbox("Choose Student", ["Select Student", "SSLC Student", "+2 Student"])

if option == "SSLC Student":
    st.header("📝 SSLC Mark Entry")
    # കുട്ടിയുടെ പേര് ചോദിക്കുന്നു
    name = st.text_input("Student Name")
    
    # മാർക്കുകൾ വാങ്ങുന്നു
    maths = st.number_input("Maths (Out of 100)", 0, 100)
    science = st.number_input("Science (Out of 100)", 0, 100)
    english = st.number_input("English (Out of 100)", 0, 100)
    
    if st.button("Generate Result"):
        total = maths + science + english
        average = total / 3
        st.success(f"ഹലോ {name}, നിന്റെ ടോട്ടൽ മാർക്ക് {total} ആണ്.")
        st.info(f"ശരാശരി (Average): {average:.2f}%")

elif option == "+2 Student":
    st.header("📚 Plus Two Grade Tracker")
    # ഇവിടെ നമുക്ക് ഗ്രേഡുകൾ നൽകാം
    physics = st.selectbox("Physics Grade", ["A+", "A", "B+", "B", "C"])
    chemistry = st.selectbox("Chemistry Grade", ["A+", "A", "B+", "B", "C"])
    
    if st.button("Show Status"):
        st.write(f"Physics: {physics}")
        st.write(f"Chemistry: {chemistry}")
        st.balloons() # ഒരു ചെറിയ ആനിമേഷൻ!
