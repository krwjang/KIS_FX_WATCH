import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
pd.options.plotting.backend = "plotly"


st.write("# 환율을 읽어옵니다")


## 사이드바
st.sidebar.header("종목, 날짜 지정")

name = st.sidebar.selectbox("종목", ['USDKRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"])

now = datetime.now().date()
ago = now - timedelta(weeks=12)
start_date = st.sidebar.date_input("시작 날짜", ago)
end_date = st.sidebar.date_input("끝 날짜", now)



data = yf.download(name , start=start_date, end=end_date)
fx = data["Close"]

fig = fx.plot.line()

st.plotly_chart(fig, use_container_width = True)