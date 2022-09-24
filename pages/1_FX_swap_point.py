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

## 데이터 로드
@st.cache
# 개별 스왑포인트 크롤링 함수
def get_fxswap(exp="1M", year=1, end="2022-01-01"):
    '''만기, 기간(연) 입력하여 개별 스왑포인트 불러오기'''
    years = 365 * year
    now = pd.to_datetime(end) + timedelta(days=2)
    end_date = now.strftime(format="%Y-%m-%d")
    ago = now - pd.Timedelta(days=years)
    start_date = ago.strftime(format="%Y-%m-%d")

    site = "http://www.smbs.biz"
    path = f"/Exchange/FxSwap_xml.jsp?arr_value={exp}_{start_date}_{end_date} HTTP/1.1"

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


year = 0.05
now = datetime.now()

df1 = get_fxswap(exp="1M", year=year, end=now)
df2 = get_fxswap(exp="2M", year=year, end=now)
df3 = get_fxswap(exp="3M", year=year, end=now)
df6 = get_fxswap(exp="6M", year=year, end=now)
df12 = get_fxswap(exp="1Y", year=year, end=now)

mid = pd.concat([df1["Mid"], df2["Mid"], df3["Mid"], df6["Mid"],  df12["Mid"]], axis=1)
mid.columns = ["1M", "2M", "3M", "6M", "1Y"]


#-------------------------------------------------------------------------------

## 전광판 매트릭스
sp_date = datetime.date(mid.index[-1])
st.markdown("### FX스왑포인트*")
st.markdown(f"전일({sp_date}) 종가 기준")
st.markdown("기물 / 종가가격 / 전일대비 (단위: 원)")
st.markdown("#")

col1, col2, col3, col4, col5, = st.columns(5)

last_sp_1m = mid["1M"].iloc[-1]
last_sp_2m = mid["2M"].iloc[-1]
last_sp_3m = mid["3M"].iloc[-1]
last_sp_6m = mid["6M"].iloc[-1]
last_sp_1y = mid["1Y"].iloc[-1]


col1.metric("1개월물", f"{last_sp_1m}원", round(mid["1M"].iloc[-1] - mid["1M"].iloc[-2], ndigits=3))
col2.metric("2개월물", f"{last_sp_2m}원", round(mid["2M"].iloc[-1] - mid["2M"].iloc[-2], ndigits=3))
col3.metric("3개월물", f"{last_sp_3m}원", round(mid["3M"].iloc[-1] - mid["3M"].iloc[-2], ndigits=3))
col4.metric("6개월물", f"{last_sp_6m}원", round(mid["6M"].iloc[-1] - mid["6M"].iloc[-2], ndigits=3))
col5.metric("1년물", f"{last_sp_1y}원", round(mid["1Y"].iloc[-1] - mid["1Y"].iloc[-2], ndigits=3))



## 플로팅 
st.write("# ")
st.write("# ")
st.write("### 기물별(Tenor) 스왑포인트 상세 ")

bid = pd.concat([df1["Bid"], df2["Bid"], df3["Bid"], df6["Bid"],  df12["Bid"]], axis=1)
bid.columns = ["1M", "2M", "3M", "6M", "1Y"]

mid = pd.concat([df1["Mid"], df2["Mid"], df3["Mid"], df6["Mid"],  df12["Mid"]], axis=1)
mid.columns = ["1M", "2M", "3M", "6M", "1Y"]

offer = pd.concat([df1["Offer"], df2["Offer"], df3["Offer"], df6["Offer"],  df12["Offer"]], axis=1)
offer.columns = ["1M", "2M", "3M", "6M", "1Y"]

sp_snap = pd.DataFrame([offer.iloc[-1], mid.iloc[-1], bid.iloc[-1]]).T
sp_snap.columns = ["Offer", "Mid", "Bid"]



fig = sp_snap.plot(kind="line", markers=True, text = "value", labels={
                     "index": "기물",
                     "value": "스왑포인트(원)",
                     "variable": "구분"
                 })
fig.update_traces(
    marker=dict(
        size=15,
        line=dict(
            width=2,
            color='DarkSlateGrey'
            ),
    ),
    textposition = "bottom center",
    textfont=dict(
        size=13,
        color="crimson"
    )
)
fig.layout.yaxis.tickformat = ',.1f'
fig.update_traces(hovertemplate=None)
fig.update_layout(hovermode="x unified")
fig.update_layout(height=600)

st.plotly_chart(fig, use_container_width=True)



#-------------------------------------------------------------------------------
## 푸터
st.write("# ")
expander = st.expander("About")
expander.markdown("""
본 화면은 서울외국환중개 홈페이지의 데이터를 사용함
   
* **스왑포인트(FX swap point)?**   
    * 스왑포인트 = 선도가격 - 현물가격
    * 해당 통화 보유시 발생하는 수익이나 비용을 거래자 간에 주고 받도록 가격에 반영(=캐리)
    * 예를 들어, 6개월 만기 스왑포인트 미드값이 -10원이라면   
        현재시점에서 매도자는 10원 싸게 팔고(손해), 매수자는 10원 싸게 매수할 수 있음(이익)   
    * 스왑포인트는 통화 간의 금리차 + a(스왑시장 수급)에 의해서 결정
#       
* **환헷지시 만기 기간의 고려**
    * 짧은 만기 : 대표적으로 증권사 통화선물 / 만기 도래시 롤오버 하여 연장 / 스왑포인트(수익 or 비용) 변동 불확실성 노출
    * 긴 만기 : 대표적으로 은행 선물환 / 만기까지 스왑포인트 고정 / 불확실성 없는 대신 헷지 비용 높음 (이후 섹션에서 논의)
#
**Tel:** 02-0000-0000 **| E-mail:** krwjang@gmail.com   
--------부 장 백 차장 a.k.a. 킬리만자로의 표범
""")
