from calendar import month
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
pd.options.plotting.backend = "plotly"


st.write("# 통화별 상대강도 비교")


## 사이드바
st.sidebar.header("종목, 날짜 지정")

name = st.sidebar.multiselect("종목", ['KRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"], 'KRW=X')

now = datetime.now().date()
ago = now - timedelta(weeks=12)
start_date = st.sidebar.date_input("시작 날짜", ago)
end_date = st.sidebar.date_input("끝 날짜", now)


### 데이터 로딩

data = yf.download(name , start=start_date, end=end_date)

fx = data["Close"] / data["Close"].iloc[0] -1

fig = fx.plot.line()

st.plotly_chart(fig)
