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
import plotly.express as px
from fbprophet import Prophet
from fbprophet.plot import plot_plotly, plot_components_plotly

# from fbprophet import plot_plotly


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

## 데이터 로드
# 개별 스왑포인트 크롤링 함수
@st.cache
def get_fxswap(exp="1M", year=1):
    '''만기, 기간(연) 입력하여 개별 스왑포인트 불러오기'''
    years = 365 * year
    now = pd.to_datetime(datetime.now()) + timedelta(days=2)
    today = now.strftime(format="%Y-%m-%d")
    ago = "2010-01-01"  # 그냥 시작일 강제지정

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


df1 = get_fxswap(exp="1M")
df3 = get_fxswap(exp="3M")

mid = pd.concat([df1["Mid"], df3["Mid"]], axis=1)
mid.columns = ["1M", "3M"]


trans = pd.DataFrame()
trans["1M"] = mid["1M"]
trans["3M"] = mid["3M"] / 3


## 플로팅

# st.markdown("# ")
st.write("""
### 1개월-3개월물 스왑포인트 역전 (spread 역전)  
2015년부터 현재까지 1-3개월 스왑포인트 스프레드 (단위: 원)
* 스왑포인트 역전 발생 시 일시적으로 단기(1M)가 불리함   
* 시장 충격 등으로 단기 달러 자금수요가 폭증하게 되면 일시적 스왑포인트 역전 현상 발생   
* **즉, 달러선물(1개월) 매도헷지시 장기적으로는 비용 우위에 있지만, 단기적 스왑포인트 역전 리스크에 노출**   
* **스왑포인트 역전을 피해갈 수는 없을까?**    
""")

trans["spread"] = trans["1M"] - trans["3M"]
fig_1 = trans["spread"].loc["2015" : ].plot.area(labels={
                     "Date": "일자",
                     "value": "1개월 스왑포인트 차이(원)"
                     }
                     )
fig_1.update_traces(hovertemplate=None)
fig_1.update_layout(hovermode="x unified", showlegend=False)
fig_1.layout.yaxis.tickformat = ',.2f'
sp_mean = round(trans["spread"].mean(), 2)
fig_1.add_hline(y=sp_mean, line_dash="dot",
              annotation_text=f"평균 : {sp_mean}원", 
              annotation_position="top right",
              annotation_font_size=15,
              annotation_font_color="red"
)
fig_1.add_vline(x="2017-12-27",line_dash="dash", line_color="orange")
fig_1.add_vline(x="2018-03-26",line_dash="dash", line_color="orange")
fig_1.add_vline(x="2018-12-17",line_dash="dash", line_color="orange")
fig_1.add_vline(x="2019-12-26",line_dash="dash", line_color="orange")
fig_1.add_vline(x="2020-03-13",line_dash="dash", line_color="orange")
fig_1.add_vline(x="2020-12-24",line_dash="dash", line_color="orange")
fig_1.add_vline(x="2021-12-15",line_dash="dash", line_color="orange")

st.plotly_chart(fig_1, use_container_width=True)


## 예측
st.markdown("---")   # 구분 가로선
st.write("""
### 1개월-3개월물 스프레드의 계절성에 주목  
* 계절적 패턴이 있지 않을까?
""")



st.markdown("---")   # 구분 가로선
st.write("""
### 시계열 분해 (Time-Series Decomposition)        
단변량 시계열 분석 라이브러리 Prophet을 활용하여 추세, 연중 계절성, 요일 계절성으로 요소 분해
""")

# 데이터 피팅 및 예측 --------------------------------------------------
with st.spinner('Wait for it...'):
    df_train = trans
    df_train["ds"] = pd.to_datetime(df_train.index.strftime("%Y-%m-%d"))
    df_train["y"] = df_train["spread"]
    df_train.reset_index(inplace=True)

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods = 252)
    forecast = m.predict(future)
    forecast = forecast[forecast['ds'].dt.dayofweek < 5]  #  주말 제거
st.success('Done!')
# --------------------------------------------------------------------


fig_2 = plot_components_plotly(m, forecast)
st.plotly_chart(fig_2, use_container_width=True)




st.markdown("---")   # 구분 가로선
st.write("""
### 🔮 스왑포인트 역전 예측 🔮  
* 1개월-3개월물 스프레드 예측
""")

# forecast_lately = forecast[forecast['ds'] > "2020-01-01"]

fig_3 = plot_plotly(m, forecast)
fig_3.update_layout(xaxis_range=['2020-01-01','2023-05-01'])
fig_3.update_traces(hovertemplate=None)
fig_3.update_layout(hovermode="x unified")

st.plotly_chart(fig_3, use_container_width=True)

st.caption("예측치 데이터")
forecast_data = forecast.iloc[-254:-1]
forecast_data = forecast_data[["ds", "yhat", "yhat_lower", "yhat_upper"]].sort_values(by="ds", ascending = False)
forecast_data.columns = ["일자", "예측값", "예측밴드_하단", "예측밴드_상단"]

st.dataframe(forecast_data)





#-------------------------------------------------------------------------------
## 푸터
st.markdown("---")   # 구분 가로선
expander = st.expander("About")
expander.markdown("""
이 화면의 데이터는 서울외국환중개로 부터 가져옴   

* 시계열 예측 알고리즘은 Facebook에서 개발한 오픈소스 Prophet을 사용
    * Prophet은 연간, 주별 및 일일 계절성과 휴일 효과에 맞는 가법 모델을 기반으로 시계열 데이터를 예측   
    * 계절 효과가 강하고 여러 시즌의 과거 데이터가 있는 시계열에서 가장 잘 작동   
    * 누락된 데이터와 추세의 변화에 ​​강하며 일반적으로 이상값을 잘 처리    
    * https://facebook.github.io/prophet/   
        

# 
**Tel:** 02-0000-0000 **| E-mail:** krwjang@gmail.com   
---솔루션영업부 장 백 차장 a.k.a. 킬리만자로의 표범
""")
