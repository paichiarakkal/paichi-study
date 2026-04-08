import streamlit as st
import pandas as pd
import yfinance as ticker # ലൈവ് വിലകൾ എടുക്കാൻ ഇത് സഹായിക്കും

st.set_page_config(page_title="PAICHI LIVE TRADING", layout="wide")

st.title("🚀 PAICHI LIVE MARKET")

# മാർക്കറ്റ് ഡാറ്റ കാണിക്കാനുള്ള സെക്ഷൻ
col1, col2, col3 = st.columns(3)

def get_live_price(symbol):
    data = ticker.Ticker(symbol).history(period='1d')
    return round(data['Close'].iloc[-1], 2)

try:
    with col1:
        nifty_price = get_live_price("^NSEI")
        st.metric("NIFTY 50", f"₹{nifty_price}")

    with col2:
        bank_nifty_price = get_live_price("^NSEBANK")
        st.metric("BANK NIFTY", f"₹{bank_nifty_price}")

    with col3:
        # ക്രൂഡ് ഓയിൽ വില (USD-ൽ ആണ് ലഭിക്കുക)
        crude_price = get_live_price("CL=F")
        st.metric("CRUDE OIL (USD)", f"${crude_price}")

except:
    st.write("മാന്യമായ ഇന്റർനെറ്റ് കണക്ഷൻ ഉണ്ടെന്ന് ഉറപ്പുവരുത്തുക.")

st.sidebar.markdown("[💬 Contact on WhatsApp](https://wa.me/message/CILS6MWZTN1)")
