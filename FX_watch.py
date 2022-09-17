import streamlit as st
import pandas as pd
import yfinance as yf



start_date = '2010-01-01'
end_date = '2021-01-01'
data = yf.download(['USDKRW=X','JPYKRW=X'],start=start_date, end=end_date)

fx = data["Close"]

st.bar_chart(fx)