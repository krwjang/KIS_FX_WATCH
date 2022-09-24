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
import plotly.express as px


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
st.title("KIS FX Watch  :leopard:")
st.markdown("---")   # 구분 가로선

#--------------------------------------------------------------------------------------------------------------



## 사이드바
st.sidebar.header("통화, 날짜 범위 지정")

name = st.sidebar.multiselect("비교 통화 (복수 선택 가능)", ['KRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"], ['KRW=X', "DX-Y.NYB"])

now = datetime.now().date()
ago = now - timedelta(days=90)
start_date = st.sidebar.date_input("시작 날짜 (기본값 -3M)", ago)
end_date = st.sidebar.date_input("끝 날짜", now) + timedelta(days=1)



### 데이터 로딩 및 상대강도 비교 차트

data = yf.download(name , start=start_date, end=end_date)
data.fillna(method='ffill', inplace=True)  # 결측값 뒤로 채우기

fx = data["Close"] / data["Close"].iloc[0] -1


st.write("""
### 환율 변동추이 비교   
**하락:** 달러대비 해당통화 강세 / **상승:** 해당통화 약세 / DX는 달러인덱스 (단위: %)
""")

fig_1 = fx.plot.line()
fig_1.layout.yaxis.tickformat = ',.1%'

st.plotly_chart(fig_1, use_container_width=True)

# 상관계수
st.caption("### 상관계수 (Correlation Coefficient)")
col1, col2 = st.columns(2)
with col1:
    roll = st.selectbox("측정 단위 일수*", (2, 5, 10, 20), 1)

pct_chg = data["Close"].pct_change()
roll_pct = pct_chg.rolling(roll).sum()
correl = roll_pct.corr().loc["KRW=X"]
st.dataframe(correl)




# 두번째 차트 기간수익률
st.write("# ")
st.markdown("---")   # 구분 가로선
st.write("""
### 주요 통화 기간수익률 비교   
60일 기준 달러대비 강세순 / 높을 수록 해당통화 강세 / DX는 달러인덱스 (단위: %)
""")

code = ['KRW=X','JPY=X', "EUR=X", "CNY=X", "AUD=X", "CHF=X", "DX-Y.NYB"]

chg_data = yf.download(code , start=end_date - timedelta(weeks=52), end=end_date)
chg_data = chg_data["Close"]
chg_data.fillna(method='ffill', inplace=True)
chg_data["DX-Y.NYB"] = chg_data["DX-Y.NYB"] * -1

chg_1d = (chg_data.iloc[-1] / chg_data.iloc[-2]  -1) * -1
chg_5d = (chg_data.iloc[-1] / chg_data.iloc[-6]  -1) * -1
chg_20d = (chg_data.iloc[-1] / chg_data.iloc[-21]  -1) * -1
chg_60d = (chg_data.iloc[-1] / chg_data.iloc[-61]  -1) * -1

chgs = pd.DataFrame([
    chg_1d,
    chg_5d,
    chg_20d,
    chg_60d
    ])
chg_fx = chgs.T
chg_fx.columns = ["1d", "5d", "20d", "60d"]
chg_fx.sort_values(by="60d", ascending=False, inplace=True)

fig_2 = chg_fx.plot.bar(barmode='group')
fig_2.layout.yaxis.tickformat = ',.1%'
st.plotly_chart(fig_2, use_container_width=True)



## 실시간 환율 
# st.write("# ")
st.markdown("---")   # 구분 가로선
# st.write("# ")
st.write("""
### 실시간 환율표
""")

url_live = "https://kr.widgets.investing.com/single-currency-crosses?theme=lightTheme&hideTitle=true&roundedCorners=true&currency=28"
st.components.v1.iframe(url_live, width=None, height=300, scrolling=True)


## 경제 캘린더
st.write("# ")
st.markdown("---")   # 구분 가로선
# st.write("# ")
st.write("""
### 오늘의 경제지표
""")

url_cal = "https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timeselector,filters&countries=17,5,4,72,35,37,11,25&calType=today&timeZone=88&lang=18"
st.components.v1.iframe(url_cal, width=None, height=400, scrolling=True)



#----------------------------------------------------------------------------------
## 푸터
st.write("# ")
st.markdown("---")   # 구분 가로선
expander = st.expander("About")
expander.markdown("""
본 화면의 데이터는 Yahoo Finance 및 Investing.com로 부터 가져오며 티커은 Yahoo Finance 참조   
CFD 시세가 사용되므로 국내 현물환율과 미미한 차이가 발생할 수 있음

* **상관계수 측정 단위 일수**   
    예) 5 선택시 5일 변동성의 동행하는 정도를 측정
#
**Tel:** 02-0000-0000 **| E-mail:** krwjang@gmail.com   
--------부 장 백 차장 a.k.a. 킬리만자로의 표범
""")
