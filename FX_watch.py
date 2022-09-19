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

## 사이드바
st.sidebar.header("비교 날짜 지정")

now = datetime.now().date()
ago = now - timedelta(weeks=12)
start_date = st.sidebar.date_input("시작 날짜", ago)
end_date = st.sidebar.date_input("끝 날짜", now)



## 데이터 로드
@st.cache
def get_fxs(year=1):
    fx_list = [
        ["USD/KRW", "USD/KRW"],
        ["USD/AUD", "USD/AUD"],
        ["USD/CNY", "USD/CNH"],
        ["USD/EUR", "USD/EUR"],
        # ["USD/GBP", "USD/GBP"],
        # ["USD/CAD", "USD/CAD"],
        ["USD/JPY", "USD/JPY"],
        ["USD/CHF", "USD/CHF"]
        # ["DollarIdx", "DX"]
    ]

    # years = 365 * year
    # now = pd.to_datetime(datetime.now())
    # today = now.strftime(format="%Y-%m-%d")
    # ago = now - pd.Timedelta(days=years)
    # ago = ago.strftime(format="%Y-%m-%d")

    df_list = [fdr.DataReader(code, start=start_date, end=end_date)['Close'] for name, code in fx_list]
    df = pd.concat(df_list, axis=1)
    df.columns = [name for name, code in fx_list]

    return df

df = get_fxs(0.5)

df_compare = df / df.iloc[0] - 1






## 플로팅
st.markdown("### ")
st.markdown("### 주요 통화별 %Chg. 상대 비교")
# st.markdown("* 상승=약세 / 하락=강세")
# st.markdown("* 기간 : 6개월")

fig_1 = df_compare.plot(kind="line")
fig_1.layout.yaxis.tickformat = ',.1%'
fig_1.update_traces(hovertemplate=None)
fig_1.update_layout(hovermode="x unified")
fig_1.update_layout(height=500)

st.plotly_chart(fig_1, use_container_width=True)






## 푸터
st.markdown(" **Tel:** 02-3276-5587 **| E-mail:** mailto:112918@koreainvestment.com")
