# -*- coding: utf-8 -*-
"""
Created on 2022
@author: JB
"""
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import FinanceDataReader as fdr

# 판다스 플로팅 백앤드로 plotly 사용
pd.options.plotting.backend = "plotly"


# st.set_page_config(page_title='KIS FX watch',  layout='wide', page_icon=':ambulance:')


st.set_page_config(
    page_title='KIS FX Watch!',  
    layout='wide', 
    page_icon=':tiger:',     
    initial_sidebar_state="expanded",
    menu_items={'About': "### 본 웹앱은 각종 오픈소스 라이브러리 및 데이터를 활용하여 만들었으며 상업적으로 사용하지 않습니다."}
)

## 헤더부분
# st.image('image/img_signature.png', width=100)
st.title("KIS FX watch")

#--------------------------------------------------------------------------------------------------------------

st.write("# 통화별 상대강도 비교")


## 사이드바
st.sidebar.header("종목, 날짜 지정")

name = st.sidebar.multiselect("종목", ['KRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"], 'KRW=X')

now = datetime.now().date()
ago = now - timedelta(weeks=12)
start_date = st.sidebar.date_input("시작 날짜", ago)
end_date = st.sidebar.date_input("끝 날짜", now) + timedelta(days=1)


### 데이터 로딩

data = yf.download(name , start=start_date, end=end_date)

fx = data["Close"] / data["Close"].iloc[0] -1

fig = fx.plot.line()

st.plotly_chart(fig)






## 푸터
st.markdown(" **Tel:** 02-3276-5587 **| E-mail:** mailto:112918@koreainvestment.com")
