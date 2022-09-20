# -*- coding: utf-8 -*-
"""
Created on 2022
@author: JB
"""
import streamlit as st
import pandas as pd
# import yfinance as yf
import requests
from bs4 import BeautifulSoup
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
st.title("KIS FX Watch  :leopard:")

#--------------------------------------------------------------------------------------------------------------

## 사이드바
st.sidebar.header("불러올 데이터 기간(년)")
year = st.sidebar.slider("기간 설정", 1, 10, 1)



## 데이터 로드
@st.cache
# 개별 스왑포인트 크롤링 함수
def get_fxswap(exp="1M", year=1):
    '''만기, 기간(연) 입력하여 개별 스왑포인트 불러오기'''
    years = 365 * year
    now = pd.to_datetime(datetime.now()) + timedelta(days=1)
    today = now.strftime(format="%Y-%m-%d")
    ago = now - pd.Timedelta(days=years)
    ago = ago.strftime(format="%Y-%m-%d")

    site = "http://www.smbs.biz"
    path = f"/Exchange/FxSwap_xml.jsp?arr_value={exp}_{ago}_{today} HTTP/1.1"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        "X-Requested-By": "FusionCharts",
        "X-Requested-With": "XMLHttpRequest"
    }

    url = f'{site}{path}'

    resp = requests.get(url, headers=header)

    soup = BeautifulSoup(resp.text, "lxml")

    d = soup.select("category")
    b = soup.select("dataset")[0].select("set")
    o = soup.select("dataset")[1].select("set")
    date = []
    bid = []
    offer = []
    for i in range(len(d)):
        date.append(pd.to_datetime(d[i]["label"], format="%y.%m.%d"))
        bid.append(float(b[i]["value"]))
        offer.append(float(o[i]["value"]))
    data = {"Date": date, "Bid": bid, "Offer": offer}
    df = pd.DataFrame(data)
    df.set_index("Date", inplace=True)
    df['Mid'] = (df.Bid + df.Offer) / 2
    df = df[["Bid", "Mid", "Offer"]] / 100

    return df



df1 = get_fxswap(exp="1M", year=year)
df2 = get_fxswap(exp="2M", year=year)
df3 = get_fxswap(exp="3M", year=year)
df6 = get_fxswap(exp="6M", year=year)
df12 = get_fxswap(exp="1Y", year=year)

mid = pd.concat([df1["Mid"], df2["Mid"], df3["Mid"], df6["Mid"],  df12["Mid"]], axis=1)
mid.columns = ["1M", "2M", "3M", "6M", "1Y"]




## 플로팅
# st.markdown("# ")
st.write("""
### 스왑포인트 일별 추이    
기물별 스왑포인트 종가 (단위:원)   
* 플러스  : 매도자 수익 / 매수자 비용 
* 마이너스: 매도자 비용 / 매수자 수익
""")

fig_1 = mid.plot(kind="line")
fig_1.update_traces(hovertemplate=None)
fig_1.update_layout(hovermode="x unified")
fig_1.layout.yaxis.tickformat = ',.2f'
fig_1.add_hline(y=0)
fig_1.update_layout(height=600)
st.plotly_chart(fig_1, use_container_width=True)




#-------------------------------------------------------------------------------
## 푸터
st.write("# ")
expander = st.expander("About")
expander.markdown("""
본 화면은 서울외국환중개 홈페이지의 데이터를 사용함


**Tel:** 02-0000-0000 **| E-mail:** krwjang@gmail.com   
---솔루션영업부 장 백 차장 a.k.a. 킬리만자로의 표범
""")
