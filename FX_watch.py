# -*- coding: utf-8 -*-
"""
Created on 2022
@author: JB
"""
import streamlit as st
import pandas as pd
import yfinance as yf
# import requests
# from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# import FinanceDataReader as fdr

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



## 사이드바
st.sidebar.header("통화, 날짜 범위 지정")

name = st.sidebar.multiselect("종목(복수 선택 가능)", ['KRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"], ['KRW=X', "DX-Y.NYB"])

now = datetime.now().date()
ago = now - timedelta(weeks=12)
start_date = st.sidebar.date_input("시작 날짜", ago)
end_date = st.sidebar.date_input("끝 날짜", now) + timedelta(days=1)


### 데이터 로딩

data = yf.download(name , start=start_date, end=end_date)
data.fillna(method='ffill', inplace=True)  # 결측값 뒤로 채우기

fx = data["Close"] / data["Close"].iloc[0] -1


st.write("""
### 환율 변동추이 비교(%)   
하락시 달러대비 해당통화 강세 / 상승시 해당통화 약세
""")

fig_1 = fx.plot.line()
fig_1.layout.yaxis.tickformat = ',.1%'

st.plotly_chart(fig_1)


# 두번째 차트 기간수익률

st.write("# ")
st.write("""
### 통화별 기간수익률 비교   
60일 기준 달러대비 강한순 / 높을 수록 해당통화 약세 / DX는 달러인덱스
""")

code = ['KRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"]

chg_data = yf.download(code , start=end_date - timedelta(weeks=52), end=end_date)
chg_data = chg_data["Close"]
chg_data.fillna(method='ffill', inplace=True)

chg_1d = chg_data.iloc[-1] / chg_data.iloc[-2]  -1
chg_20d = chg_data.iloc[-1] / chg_data.iloc[-21]  -1
chg_60d = chg_data.iloc[-1] / chg_data.iloc[-61]  -1

chgs = pd.DataFrame([
    chg_1d,
    chg_20d,
    chg_60d
    ])
chg_fx = chgs.T
chg_fx.columns = ["1d", "20d", "60d"]
chg_fx.sort_values(by="60d", ascending=True, inplace=True)

fig_2 = chg_fx.plot.bar(barmode='group')
fig_2.layout.yaxis.tickformat = ',.1%'
st.plotly_chart(fig_2)





## 푸터
st.write("# ")
expander = st.expander("About")
expander.markdown("""
이 화면의 데이터는 Yahoo Finance로 부터 가져오며 티커명 역시 Yahoo Finance 참조   

**Tel:** 02-3276-5587 **| E-mail:** 112918@koreainvestment.com   
한국투자증권 패시브솔루션영업부 장 백 차장 a.k.a. 킬리만자로의 표범
""")