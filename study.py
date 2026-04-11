    # --- MINI 3x3 GRID (ICONS ONLY) ---
    
    # ROW 1
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.button("💰", on_click=nav, args=("ADD",), key="btn1")
    with c2: 
        st.button("📊", on_click=nav, args=("DATA",), key="btn2")
    with c3: 
        st.button("🌙", on_click=nav, args=("PEACE",), key="btn3")

    st.write("") # ചെറിയ ഗ്യാപ്പ്

    # ROW 2
    c4, c5, c6 = st.columns(3)
    with c4: 
        st.button("🔴", on_click=nav, args=("DEBTS",), key="btn4")
    with c5: 
        st.button("📝", on_click=nav, args=("TASKS",), key="btn5")
    with c6: 
        st.button("🛒", on_click=nav, args=("LIST",), key="btn6")

    st.write("")

    # ROW 3
    c7, c8, c9 = st.columns(3)
    with c7: 
        st.button("⚙️", on_click=nav, args=("SET",), key="btn7")
    with c8: 
        st.button("🔄", on_click=st.rerun, key="btn8")
    with c9: 
        st.button("📞", on_click=nav, args=("PEACE",), key="btn9")
