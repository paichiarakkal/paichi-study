import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# Sidebar
st.sidebar.title("🚀 Paichi Pro")
st.sidebar.markdown("[💬 Contact on WhatsApp](https://wa.me/message/CILS6MWZTN1)")

# Main Content
st.title("🚀 Paichi AI Trader Pro")

# Simple Currency/Gold Logic (Placeholder)
st.subheader("💰 Quick Tools")
dirham = st.number_input("Dirham Amount", value=1.0)
st.write(f"₹ {dirham * 22.5} INR (Approx)")

# Market Section
st.subheader("🚀 NIFTY 50")
st.write("Current Value: ₹ 24,010.60")

st.info("എററുകൾ എല്ലാം മാറി! ഇനി നമുക്ക് ഇതിൽ കൂടുതൽ ഫീച്ചറുകൾ ചേർക്കാം.")
