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
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly


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
# 개별 스왑포인트 크롤링 함수
# @st.cache()
def get_fxswap(exp="1M", start="2010-01-01"):
    '''만기, 수집 시작일을 입력하여 개별 스왑포인트 불러오기'''

    now = pd.to_datetime(datetime.now()) + timedelta(days=3)
    today = now.strftime(format="%Y-%m-%d")

    site = "http://www.smbs.biz"
    path = f"/Exchange/FxSwap_xml.jsp?arr_value={exp}_{start}_{today} HTTP/1.1"

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

# 데이터 로딩 : 속도 개선 위해 피클로 저장-------------
# 1개월, 3개월만 수집

try:
    trans = pd.read_pickle("trans.pkl")
    
except:
    df1 = get_fxswap(exp="1M", start="2010-01-01")
    df3 = get_fxswap(exp="3M", start="2010-01-01")

    mid = pd.concat([df1["Mid"], df3["Mid"]], axis=1)
    mid.columns = ["1M", "3M"]

    trans = pd.DataFrame()
    trans["1M"] = mid["1M"]
    trans["3M"] = mid["3M"] / 3
    
    trans.to_pickle("trans.pkl")



#-------------------------------------------------------




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
              annotation_text=f"월평균 : {sp_mean}원", 
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
### 1개월-3개월물 스프레드의 계절성(seasonality)에 주목  
연도별, 월평균 스왑포인트 스프레드 히트맵 (단위: 원)   
* 분기월에 스프레드가 낮아지는 경향이 있음   
* 특히 2016년 이후, 12월 장단기 스프레드 역전이 뚜렷하게 나타남 
""")

# 스프레드를 월별로 끊어서 평균값 계산
cal = trans[["spread"]].resample("M").mean()
cal["year"] = cal.index.year
cal["month"] = cal.index.month
cal_table = cal.pivot(index="year", columns="month", values = "spread")

fig_5 = px.imshow(cal_table, text_auto=".2f", aspect="auto", color_continuous_scale='Bluered')
fig_5.update_layout(height=600)

st.plotly_chart(fig_5, use_container_width=True)




st.markdown("---")   # 구분 가로선
st.write("""
### 시계열 분해 (Time-Series Decomposition)        
단변량 시계열 분석 라이브러리 Prophet을 활용하여 추세, 연중 계절성, 요일 계절성으로 요소 분해
* 연중 1개월물 상대 가격이 2/25, 5/20, 8/20, 11/20 고점을 찍고 하락하는 패턴 확인
* 특히 11월 말에서 12월 중순까지는 가파르게 하락 → 달러선물 12월물 매도 보유시 12월-1월 스프레드 형성되는 즉시 롤오버 유리
""")

# 데이터 모델 피팅 및 예측 --------------------------------------------------
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
1개월-3개월물 스프레드 예측
* 파란선: 예측치 / 하늘색 밴드: 예측 신뢰구간 / 검은점: 실제치 
* 예측치를 중심으로 1개월물 상대가격 실제치의 고평가(밴드 위)/저평가(밴드 아래) 확인
* 다가올 예측치 하락을 확인 → 실제치 하락 전 대응
""")

# forecast_lately = forecast[forecast['ds'] > "2020-01-01"]

range_start = pd.to_datetime(datetime.now()) + timedelta(days=-250)
range_start = range_start.strftime(format="%Y-%m-%d")
range_end = pd.to_datetime(datetime.now()) + timedelta(days=+100)
range_end = range_end.strftime(format="%Y-%m-%d")

fig_3 = plot_plotly(m, forecast)
fig_3.update_layout(xaxis_range=[range_start, range_end])
fig_3.update_traces(hovertemplate=None)
fig_3.update_layout(hovermode="x unified")

st.plotly_chart(fig_3, use_container_width=True)

# st.caption("예측치 데이터")
# forecast_data = forecast.iloc[-200:-1]
# forecast_data = forecast_data[["ds", "yhat", "yhat_lower", "yhat_upper"]].sort_values(by="ds", ascending = True)
# forecast_data.columns = ["일자", "예측값", "예측밴드_하단", "예측밴드_상단"]

# st.dataframe(forecast_data)





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
OOO a.k.a. 킬리만자로의 표범
""")
