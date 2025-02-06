## streamlit run "C:/Users/hm620/python basic/Nico/extractors/stock_app.py"

# 필요한 라이브러리 import

import streamlit as st
from yahooquery import Ticker, Screener
import pandas as pd
from datetime import datetime

# 🏠 Streamlit 페이지 설정
st.set_page_config(page_title="주식 분석 앱", layout="wide")

# 📌 제목
st.title("📊 주식 데이터 검색 & 산업군 분석")

# 📌 탭 메뉴 생성
tab1, tab2 = st.tabs(["🏭 산업군별 주식", "🔍 개별 주식 검색"])

# ✅ [1] 산업군별 주식 데이터 가져오기
with tab1:
    st.subheader("🏭 산업군별 주식 데이터 검색")

    # Screener 객체 생성
    screener = Screener()

    # Yahoo Finance에서 제공하는 산업군 목록 가져오기
    available_screeners = screener.available_screeners

    # 사용자 친화적 이름 매핑
    sector_mapping = {key: key.replace("_", " ").title() for key in available_screeners}

    # 🔍 산업군 선택
    selected_sector = st.selectbox("🔍 산업군을 선택하세요:", list(sector_mapping.values()))

    # 버튼 클릭 시 데이터 가져오기
if st.button("🔎 검색", key="sector_search"):
    selected_key = next((key for key, title in sector_mapping.items() if title == selected_sector), None)

    if not selected_key:
        st.warning("⚠️ 선택한 산업군이 유효하지 않습니다.")
    else:
        try:
            results = screener.get_screeners(screen_ids=[selected_key], count=20)
            stocks = results.get(selected_key, {}).get("quotes", [])

            if stocks:
                # 주식 데이터 DataFrame 변환
                data = {
                    "티커": [stock["symbol"] for stock in stocks],
                    "주가 (USD$)": [
                        round(stock.get("regularMarketPrice", 0), 1) if isinstance(stock.get("regularMarketPrice"), (int, float)) else "N/A"
                        for stock in stocks
                    ],
                    "주가 변화율 (%)": [
                        round(stock.get("regularMarketChangePercent", 0), 1) if isinstance(stock.get("regularMarketChangePercent"), (int, float)) else "N/A"
                        for stock in stocks
                    ],
                    "PER": [
                        round(stock.get("trailingPE", 0), 1) if isinstance(stock.get("trailingPE"), (int, float)) else "N/A"
                        for stock in stocks
                    ],
                    "EPS": [
                        round(stock.get("epsTrailingTwelveMonths", 0), 1) if isinstance(stock.get("epsTrailingTwelveMonths"), (int, float)) else "N/A"
                        for stock in stocks
                    ]
                }
                df = pd.DataFrame(data)

                # 🔹 PER 순위 추가 (값이 있는 경우만 정렬)
                df["PER"] = pd.to_numeric(df["PER"], errors="coerce")  # 숫자로 변환
                df = df.sort_values(by="PER", ascending=False, na_position="last").reset_index(drop=True)
                df["PER 순위"] = df["PER"].rank(method="min", ascending=True).astype("Int64")

                # # PER 순위를 정수형으로 변환하되 NaN 값은 "N/A" 처리
                # df["PER 순위"] = df["PER 순위"].fillna("N/A").astype(str)

                # 📊 테이블 출력
                st.write(f"📊 **{selected_sector} 산업군 주식 데이터**")
                st.dataframe(df.style.format({
                    "주가 (USD$)": "{:.1f}",
                    "주가 변화율 (%)": "{:.1f}",
                    "PER": "{:.1f}",
                    "EPS": "{:.1f}"
                }, na_rep="N/A"))  # na_rep="N/A"로 NaN 값 처리

                # 산업군 PER 데이터 저장 (개별 주식 검색에서 사용)
                st.session_state["sector_per_data"] = df[["티커", "PER", "PER 순위"]].replace("N/A", None).dropna()

            else:
                st.warning("⚠️ 선택한 산업군에서 데이터를 찾을 수 없습니다.")

        except Exception as e:
            st.error(f"🚨 오류 발생: {e}")

# ✅ [2] 개별 주식 검색
with tab2:
    st.subheader("🔍 개별 주식 검색")
    
    # 🔎 종목 코드 입력
    ticker_input = st.text_input("🎯 종목 코드를 입력하세요 (예: AAPL, TSLA, MSFT)", "")

    if st.button("🔎 검색", key="ticker_search"):
        if not ticker_input:
            st.warning("⚠️ 종목 코드를 입력하세요!")
        else:
            try:
                stock = Ticker(ticker_input)

                # ✅ Yahoo Finance 정보 가져오기
                summary_detail = stock.summary_detail.get(ticker_input, {})
                price_info = stock.price.get(ticker_input, {})

                # ✅ 현재 가격
                market_price = price_info.get("regularMarketPrice") or summary_detail.get("regularMarketPrice", "N/A")
                eps = price_info.get("epsTrailingTwelveMonths") or summary_detail.get("epsTrailingTwelveMonths", "N/A")

                # ✅ PER (주가수익비율)
                per = summary_detail.get("trailingPE", "N/A")

                # ✅ 시가총액
                market_cap = summary_detail.get("marketCap", "N/A")

                # ✅ `regularMarketTime` 변환
                market_time = price_info.get("regularMarketTime", None)
                if market_time:
                    try:
                        market_time = datetime.utcfromtimestamp(int(market_time)).strftime("%Y-%m-%d %H:%M:%S (UTC)")
                    except ValueError:
                        market_time = "N/A"

                # ✅ 시장 상태 가져오기
                market_state = price_info.get("marketState", "N/A")
                market_state_map = {
                    "REGULAR": "📈 본장(Regular Market)",
                    "POST": "🌙 애프터장(After Hours)",
                    "PRE": "🌅 프리마켓(Pre-Market)",
                    "CLOSED": "🔒 시장 종료(Closed)"
                }
                market_state_text = market_state_map.get(market_state, market_state)

                # ✅ PER 순위 계산
                per_rank = "N/A"
                if per != "N/A" and "sector_per_data" in st.session_state:
                    sector_df = st.session_state["sector_per_data"].dropna().copy()
                    sector_df["PER"] = pd.to_numeric(sector_df["PER"], errors="coerce")
                
                    # 🔹 PER 높은 순으로 정렬 (높을수록 낮은 순위)
                    sector_df = sector_df.dropna().sort_values(by="PER", ascending=False).reset_index(drop=True)
                
                    if ticker_input in sector_df["티커"].values:
                        per_rank = sector_df[sector_df["티커"] == ticker_input]["PER 순위"].values[0]
                
                # ✅ 주식 정보 출력
                st.write(f"📌 **{ticker_input} 주식 정보**")
                st.write(f"**현재 가격**: {market_price} USD")
                st.write(f"**PER**: {per} ({per_rank}위)")
                st.write(f"**EPS**: {eps}")
                st.write(f"**시가총액**: {market_cap} USD")
                st.write(f"**📅 기준 날짜**: {market_time}")
                st.write(f"**⏳ 현재 시장 상태**: {market_state_text}")

            except Exception as e:
                st.error(f"🚨 오류 발생: {e}")

