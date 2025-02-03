## streamlit run "C:/Users/hm620/python basic/Nico/extractors/stock_app.py"

# 필요한 라이브러리 import
import streamlit as st   
from yahooquery import Screener, Ticker
import pandas as pd

# Streamlit 앱 제목
st.title("📈 주식 데이터 검색")

# 👉 **탭 추가 (산업군별 / 티커 검색)**
tab1, tab2 = st.tabs(["🏭 산업군별 검색", "🔍 티커별 검색"])

# **산업군별 검색 기능**
with tab1:
    st.subheader("🏭 산업군별 주식 데이터 검색")

    # Screener 객체 생성
    screener = Screener()

    # Yahoo Finance에서 제공하는 스크리너 목록 가져오기
    available_screeners = screener.available_screeners  # ✅ screen_ids 없이 사용 가능

    # 산업군 목록 생성 (자동 동기화)
    sector_mapping = {key: key.replace("_", " ").title() for key in available_screeners}  

    # 산업군 선택
    selected_sector = st.selectbox("🔍 산업군을 선택하세요:", list(sector_mapping.values()))

    # 버튼 클릭 시 데이터 가져오기
    if st.button("검색", key="sector_search"):
        # 선택한 섹터의 실제 ID 찾기
        selected_key = next((key for key, title in sector_mapping.items() if title == selected_sector), None)

        if not selected_key:
            st.warning("⚠️ 선택한 산업군이 유효하지 않습니다.")
        else:
            try:
                # ✅ 선택한 스크리너 ID로 데이터 가져오기
                results = screener.get_screeners(screen_ids=[selected_key], count=20)
                stocks = results.get(selected_key, {}).get("quotes", [])

                if stocks:
                    # 필요한 정보만 추출하여 DataFrame 생성
                    data = {
                        "티커": [stock["symbol"] for stock in stocks],
                        "주가 (USD$)": [stock.get("regularMarketPrice", "N/A") for stock in stocks],
                        "주가 변화율 (%)": [round(stock.get("regularMarketChangePercent", 0), 1) if stock.get("regularMarketChangePercent") is not None else "N/A" for stock in stocks]
                    }
                    df = pd.DataFrame(data)

                    # 테이블로 표시
                    st.write(f"📊 **{selected_sector} 산업군 주식 데이터**")
                    st.dataframe(df)
                else:
                    st.warning("⚠️ 선택한 산업군에서 데이터를 찾을 수 없습니다.")

            except Exception as e:
                st.error(f"🚨 오류 발생: {e}")

# **티커별 개별 검색 기능**
with tab2:
    st.subheader("🔍 개별 주식 검색")

    # 사용자 입력 (티커 코드)
    ticker_input = st.text_input("🎯 종목 코드를 입력하세요 (예: AAPL, TSLA, MSFT)", "")

    # 버튼 클릭 시 개별 주식 데이터 가져오기
    if st.button("🔎 검색", key="ticker_search"):
        if not ticker_input:
            st.warning("⚠️ 종목 코드를 입력하세요!")
        else:
            try:
                # Ticker 객체 생성
                stock = Ticker(ticker_input)
                info = stock.summary_detail[ticker_input]

                if info:
                    st.write(f"📌 **{ticker_input} 주식 정보**")
                    st.write(f"**현재 가격**: {info.get('regularMarketPrice', 'N/A')} USD")
                    st.write(f"**PER**: {info.get('trailingPE', 'N/A')}")
                    st.write(f"**EPS**: {info.get('epsTrailingTwelveMonths', 'N/A')}")
                    st.write(f"**시가총액**: {info.get('marketCap', 'N/A')} USD")
                else:
                    st.warning("⚠️ 종목 정보를 찾을 수 없습니다.")

            except Exception as e:
                st.error(f"🚨 오류 발생: {e}")
