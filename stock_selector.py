#@title ##**4.stock_selector.py**
# %%writefile stock_selector.py
# stock_selector.py
import streamlit as st
from datetime import datetime, timedelta
from pykrx import stock

class StockSelector:
    def __init__(self):
        self.start_date = None
        self.end_date = None
        self.market_filter = None
        self.show_all = None
        self.show_recent_only = None
        self.selected_stocks = None
        
        self.market_cap_filter = None  # 시가총액 필터 추가
        self.daekum_cap_filter = None  # 거래대금 필터 추가
        self.signal_verify_days = None  # 매수시그널 검증일수 추가        

    def get_all_stock_codes(self):
        """코스피와 코스닥의 모든 종목 코드와 이름을 가져오는 함수"""
        try:
            kospi_tickers = stock.get_market_ticker_list(market="KOSPI")
            kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")

            kospi_names = [f"[KOSPI] {ticker}: {stock.get_market_ticker_name(ticker)}"
                          for ticker in kospi_tickers]
            kosdaq_names = [f"[KOSDAQ] {ticker}: {stock.get_market_ticker_name(ticker)}"
                          for ticker in kosdaq_tickers]

            return kospi_names + kosdaq_names
        except Exception as e:
            st.error(f"종목 목록 조회 중 오류 발생: {str(e)}")
            return []

    def show_selector(self):
        # 날짜 선택
        # col1, col2, col3 = st.columns(3)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # 시장 선택 및 종목 필터링
            self.market_filter = st.radio(
                "시장 선택",
                ["전체", "KOSPI", "KOSDAQ"],
                horizontal=True
            )

            all_stocks = self.get_all_stock_codes()
            filtered_stocks = [stock for stock in all_stocks if
                            self.market_filter == "전체" or
                            f"[{self.market_filter}]" in stock]
        with col2:
            self.start_date = st.date_input(
                "시작일",
                datetime.now() - timedelta(days=365)
            ).strftime("%Y%m%d")
        with col3:
            self.end_date = st.date_input(
                "종료일",
                datetime.now()
            ).strftime("%Y%m%d")
            
        # 분석 옵션 설정
        col1, col2, col3 = st.columns(3)            
        with col1:   
            # 시가총액 필터 추가
            self.market_cap_filter = st.select_slider(
                "시가총액 필터 (억원)",
                options=[0, 1000, 5000, 10000, 50000, 100000, 500000, 100000000],
                value=(0, 100000000)
            ) 
            
        with col2:   
            # 거래대금 필터 추가
            self.daekum_cap_filter = st.select_slider(
                "거래대금 필터 (억원)",
                options=[0, 5, 10, 20, 30, 50, 100, 500, 1000, 1500, 5000, 10000, 100000],
                value=(0, 100000)
            )             
        with col3:    
            # 매수시그널 검증일수 추가
            self.signal_verify_days = st.number_input(
                "매수시그널 검증일수",
                min_value=1,
                max_value=20,
                value=3,
                help="매수시그널 발생 후 수익률을 계산할 기간"
            )            

        # 분석 옵션 설정
        col1, col2 = st.columns(2)
        with col1:
            self.show_all = st.checkbox("시그널이 없는 종목도 표시", value=True)
        with col2:
            self.show_recent_only = st.checkbox("최근 매수 시그널 종목만 표시", value=False)

        # 종목 선택
        self.selected_stocks = st.multiselect(
            "종목 선택 (복수 선택 가능)",
            filtered_stocks
        )

        if st.checkbox("현재 필터된 전체 종목 선택"):
            self.selected_stocks = filtered_stocks

        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'show_all': self.show_all,
            'show_recent_only': self.show_recent_only,
            'selected_stocks': self.selected_stocks,
            'market_cap_filter': self.market_cap_filter,  # 시가총액 필터 추가
            'daekum_cap_filter': self.daekum_cap_filter,
            'signal_verify_days': self.signal_verify_days  # 검증일수 추가            
        }


