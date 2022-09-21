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


year=1
## 데이터 로드
# 개별 스왑포인트 크롤링 함수
@st.cache
def get_fxswap(exp="1M", year=1):
    '''만기, 기간(연) 입력하여 개별 스왑포인트 불러오기'''
    years = 365 * year
    now = pd.to_datetime(datetime.now()) + timedelta(days=2)
    today = now.strftime(format="%Y-%m-%d")
    ago = "2010-01-01"

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
df3 = get_fxswap(exp="3M", year=year)

mid = pd.concat([df1["Mid"], df3["Mid"]], axis=1)
mid.columns = ["1M", "3M"]


trans = pd.DataFrame()
trans["1M"] = mid["1M"]
trans["3M"] = mid["3M"] / 3


## 플로팅

# st.markdown("# ")
st.write("""
### 1개월-3개월물 스왑포인트 역전 (spread 역전)   
* 1개월물 스왑포인트에서 환산된 3개월물 스왑포인트를 차감하면 대부분 기간에서 1개월물 가격이 높음 (매도헷지 비용 낮음)   
* 시장 충격 등으로 단기 달러 자금수요가 폭증하게 되면 일시적 스왑포인트 역전 현상 발생   
* 즉, 달러선물(1개월) 매도헷지시 장기적으로는 평균에 수렴하겠지만 단기적 스왑포인트 역전 리스크에 노출   
* **스왑포인트 역전을 피해갈 수는 없을까?**ㅔㅛ    
""")

spread = trans["1M"] - trans["3M"]
fig_2 = spread.plot.area()
fig_2.update_traces(hovertemplate=None)
fig_2.update_layout(hovermode="x unified")
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
st.write("# ")
expander = st.expander("About")
expander.markdown("""
이 화면의 데이터는 서울외국환중개로 부터 가져옴   

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
    * 은행 선물환 거래시 Credit line / 증권사 통화선물 거래시 증거금
    * 은행 선물환 Mid가에 마진포함된 가격 / 증권사는 mid 수준에 거래되나 매매수수료 발생

# 
**Tel:** 02-0000-0000 **| E-mail:** krwjang@gmail.com   
---솔루션영업부 장 백 차장 a.k.a. 킬리만자로의 표범
""")
