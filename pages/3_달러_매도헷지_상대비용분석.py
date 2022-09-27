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
st.markdown("---")   # 구분 가로선


#--------------------------------------------------------------------------------------------------------------

## 사이드바
st.sidebar.header("불러올 데이터 기간(년)")
year = st.sidebar.slider("기간 설정", 1, 10, 1)




## 데이터 로드
# 개별 스왑포인트 크롤링 함수
# @st.cache(persist=True, max_entries=100)
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


now = datetime.now()

@st.cache(persist=True, max_entries=100)
def get_fxswaps(year=year, end=now, price_type="Mid"):
    df1 = get_fxswap(exp="1M", year=year, end=end)
    df2 = get_fxswap(exp="2M", year=year, end=end)
    df3 = get_fxswap(exp="3M", year=year, end=end)
    df6 = get_fxswap(exp="6M", year=year, end=end)
    df12 = get_fxswap(exp="1Y", year=year, end=end)

    result = pd.concat([df1[price_type], df2[price_type], df3[price_type], df6[price_type],  df12[price_type]], axis=1)
    result.columns = ["1M", "2M", "3M", "6M", "1Y"]

    return result 


# 데이터 로드

mid = get_fxswaps(price_type="Mid")


#-------------------------------------------------------------------------------


## 플로팅
# st.markdown("# ")
st.write("""
### 스왑포인트 1개월 단위 환산    
가격 비교를 위해 기물별 스왑포인트를 1개월 단위로 나누어 기간당 가격으로 평준화 (단위: 원)   
* 대부분의 기간에서는 만기가 짧은 순으로 가격이 높음 → **높을수록 매도자 유리**
* 단, 달러 단기자금 수요가 급증하게 되면 **장단기 스왑포인트 역전** 발생 → 일시적인 단기물 매도자 불리
""")

trans = pd.DataFrame()
trans["1M"] = mid["1M"]
trans["2M"] = mid["2M"] / 2
trans["3M"] = mid["3M"] / 3
trans["6M"] = mid["6M"] / 6
trans["1Y"] = mid["1Y"] / 12

fig_1 = trans.plot.line(labels={
                     "Date": "일자",
                     "value": "1개월당 스왑포인트(원)",
                     "variable": "기물"
                 })
fig_1.update_traces(hovertemplate=None)
fig_1.update_layout(hovermode="x unified")
fig_1.layout.yaxis.tickformat = ',.2f'
fig_1.add_hline(y=0)
fig_1.add_vrect(x0="2021-12-08", x1="2021-12-24", 
              annotation_text="역전", annotation_position="top left",
              fillcolor="orange", opacity=0.25, line_width=0)
st.plotly_chart(fig_1, use_container_width=True)


st.markdown("---")   # 구분 가로선
st.write("""
### 기물별 1개월당 스왑포인트 기술통계  
평균 / 표준편차 / 최소값 / 25%값 / 50%값 / 75%값 / 최대값 (단위: 원)   
* 장기 거래시 평균에 수렴하므로 **매도헷지는 평균 스왑포인트가 높은 단기물이 유리**
* 예) 1개월물 평균 가격이 6개월물보다 0.5원 높다면, 장기적으로 매달 평균 50전 유리하며 연간 6원 세이브
""")

dataframe = trans.describe().T[["mean", "std", "min", "25%", "50%", "75%", "max"]]
st.dataframe(dataframe)




st.markdown("# ")
st.markdown("---")   # 구분 가로선
st.write("""
### 1개월-n개월물 상대가격 비교 (Spread)   
1개월물 스왑포인트에서 환산된 n개월물 스왑포인트를 차감하여 순수한 가격 우위만 측정 (단위: 원)   
* 예) 달러선물(1개월)과 선물환(대표적으로 3개월)의 상대가격 비교
    * 최근 1년간 1개월물이 3개월물 보다 월평균 0.27원 절약    
    * 지난 10년간 1개월물이 3개월물 보다 월평균 0.12원 절약 (= 통화선물 거래수수료 수준)
""")
col1, col2 = st.columns(2)
with col2:
    nmonths = st.selectbox(
        '1개월물 - "n개월물" 선택',
        ('2M', '3M', '6M', '1Y'), 1)

spread = trans["1M"] - trans[nmonths]
fig_2 = spread.plot.area(labels={
                     "Date": "일자",
                     "value": "1개월 스왑포인트 차이(원)",
                     "variable": "기물"
                 })
fig_2.update_traces(hovertemplate=None)
fig_2.update_layout(hovermode="x unified", showlegend=False)
fig_2.layout.yaxis.tickformat = ',.2f'
sp_mean = round(spread.mean(), 2)
fig_2.add_hline(y=sp_mean, line_dash="dot",
              annotation_text=f"평균 : {sp_mean}원", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="red"
)

st.plotly_chart(fig_2, use_container_width=True)




#-------------------------------------------------------------------------------
## 푸터
st.markdown("---")   # 구분 가로선
expander = st.expander("About")
expander.markdown("""
본 화면은 서울외국환중개 홈페이지의 데이터를 사용함   

* 1개월로 단순 환산 방법   
    * 1개월물 스왑포인트   
    * 2개월물 스왑포인트 / 2   
    * 3개월물 스왑포인트 / 3   
    * 6개월물 스왑포인트 / 6
    * 1년물 스왑포인트 / 12    
###
* 환헷지 고려시 스왑포인트가 전부는 아님
    * 장기물은 헷지비용이 많이 드는 대신 거래를 채결하고 해당 기간동안 비용 고정
    * 단기물은 계속 롤오버를 해야하므로 매 거래 시점의 변동에 노출(그래도 장기적으로 평균에 수렴)
    * 은행 선물환 거래시 Credit line 필요 / 증권사 통화선물 거래시 증거금 필요
    * 은행 선물환은 Mid값 + 마진포함 가격에 거래 / 증권사 통화선물은 Mid값 수준에 거래되나 매매수수료 발생

# 
**Tel:** 02-0000-0000 **| E-mail:** krwjang@gmail.com   
장 백 차장 a.k.a. 킬리만자로의 표범
""")
