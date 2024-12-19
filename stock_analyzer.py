# #@title ##**3.stock_analyzer.py**
# %%writefile stock_analyzer.py
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pykrx import stock
import pandas as pd
import numpy as np
import streamlit as st

class StockAnalyzer:
    def __init__(self):
        self.df = None
        self.show_all = False
        self.show_recent_only = False
        self.signal_verify_days = 3
        self.market_cap_filter = (0, 100000000) 
        self.daekum_cap_filter = (0, 1000000) 

    def set_display_option(self, show_all, show_recent_only, market_cap_filter, signal_verify_days, daekum_cap_filter):
        """디스플레이 옵션 설정"""
        self.show_all = show_all
        self.show_recent_only = show_recent_only
        self.market_cap_filter = market_cap_filter
        self.daekum_cap_filter = daekum_cap_filter
        self.signal_verify_days = signal_verify_days

    # @st.cache_data(ttl=3600)  # 1시간 캐시
    def get_stock_data(self, ticker, start_date, end_date):
        """주식 데이터 조회 및 전처리"""
        try:
            # OHLCV 데이터 조회
            df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker, adjusted=False)
            if df is None or df.empty or len(df) < 40:
                return None

            # 투자자 데이터 조회
            inv_df = stock.get_market_trading_volume_by_date(start_date, end_date, ticker)
            if inv_df is None or inv_df.empty:
                return None

            # 데이터 전처리
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.dropna()

            # 거래대금 계산
            mask = df['거래량'] != 0
            df.loc[mask, '평균거래가'] = (df.loc[mask, '거래대금'] / df.loc[mask, '거래량']).round(2)
            df.loc[~mask, '평균거래가'] = df['종가']  # 거래량이 0인 경우 종가 사용

            df['거래대금'] = (df['거래대금']/100000000).round(2)  # 억원 단위

            # 외인/기관 순매수 금액 계산
            df['외인순매수금액'] = (inv_df['외국인합계'] * df['평균거래가']) / 100000000
            df['기관순매수금액'] = (inv_df['기관합계'] * df['평균거래가']) / 100000000

            self.df = df
            return df

        except Exception as e:
            print(f"데이터 조회 중 오류 발생: {str(e)}")
            return None

    def calculate_technical_indicators(self):
        """기술적 지표 계산"""
        try:
            self.df['5일선'] = self.df['평균거래가'].rolling(window=5).mean()
            self.df['40일선'] = self.df['평균거래가'].rolling(window=40).mean()
            return self.df
        except Exception as e:
            print(f"기술적 지표 계산 중 오류: {str(e)}")
            return None

    def generate_signals(self):
        """매매 시그널 생성"""
        try:
            self.df['외인_매수'] = self.df['외인순매수금액'].fillna(0)
            self.df['기관_매수'] = self.df['기관순매수금액'].fillna(0)
            self.df['10일_매수금액'] = (self.df['외인_매수'] + self.df['기관_매수']).rolling(window=10).mean()

            self.df['Signal'] = 0
            조건1 = (self.df['5일선'] > self.df['40일선']) & (self.df['5일선'].shift(1) <= self.df['40일선'].shift(1))
            조건2 = self.df['10일_매수금액'] >= 10

            self.df.loc[조건1 & 조건2, 'Signal'] = 1
            return self.df
        except Exception as e:
            print(f"시그널 생성 중 오류: {str(e)}")
            return None

    def has_recent_signal(self):
        """최근 거래일의 매수 시그널 확인"""
        try:
            if self.df is None or self.df.empty:
                return False
            latest_date = self.df.index[-1]
            return bool(self.df.loc[latest_date, 'Signal'] == 1)
        except Exception:
            return False

    def analyze_stock(self, ticker, start_date, end_date):
        """종목 분석 통합 함수"""
        try:
            df = self.get_stock_data(ticker, start_date, end_date)
            if df is None:
                return None, None

            self.calculate_technical_indicators()
            self.generate_signals()
            results = self.analyze_performance()
            capbool = self.filter_by_market_cap(ticker, end_date)
            
            last_5_avg = df['거래대금'].tail(5).mean()

            if not(self.daekum_cap_filter[0] <= last_5_avg <= self.daekum_cap_filter[1]):
                return None, None
            
            if(not capbool):
                return None, None  
                        
            # 최근 매수 시그널 필터링
            if self.show_recent_only:
                if not self.has_recent_signal():
                    return None, None
            else:
                if not self.show_all and results['전체_매수_시그널'] == 0:
                    return None, None                                                       
                
            return df, results            

        except Exception as e:
            print(f"종목 분석 중 오류 발생: {str(e)}")
            return None, None
        
    def filter_by_market_cap(self, ticker, end_date):
        """시가총액 필터링"""
        try:
            # cap_df = stock.get_market_cap(self.end_date)
            # if ticker in cap_df.index:
            #     market_cap = cap_df.loc[ticker, '시가총액'] / 100000000  # 억원 단위
            #     return self.market_cap_filter[0] <= market_cap <= self.market_cap_filter[1]
            # return False
        
            cap_end = datetime.strptime(end_date, '%Y%m%d')
            cap_start = cap_end - timedelta(days=10)
            df1 = stock.get_market_cap_by_date(cap_start.strftime('%Y%m%d'), 
                                                end_date, 
                                                ticker)
            sigatot = df1.iloc[-1]['시가총액']/100000000 
            return self.market_cap_filter[0] <= sigatot <= self.market_cap_filter[1]

        except Exception:
            return False        

    def analyze_performance(self):
        """매매 성과 분석"""
        try:
            signals = self.df[self.df['Signal'] == 1].index
            results = {
                '전체_매수_시그널': 0,
                '성공_시그널': 0,
                '실패_시그널': 0,
                '수익률_리스트': []
            }

            for signal_date in signals:
                idx = self.df.index.get_loc(signal_date)
                if idx + self.signal_verify_days >= len(self.df):
                    continue

                entry_price = self.df.iloc[idx]['종가']
                future_prices = self.df.iloc[idx+1:idx+(self.signal_verify_days + 1)]['종가']
                max_price = future_prices.max()

                profit = ((max_price - entry_price) / entry_price) * 100
                results['수익률_리스트'].append(profit)
                results['전체_매수_시그널'] += 1

                if max_price > entry_price:
                    results['성공_시그널'] += 1
                else:
                    results['실패_시그널'] += 1

            return self.calculate_final_results(results)
        except Exception as e:
            print(f"성과 분석 중 오류: {str(e)}")
            return None

    def calculate_final_results(self, results):
        """최종 결과 계산"""
        if results['전체_매수_시그널'] == 0:
            return {
                '전체_매수_시그널': 0,
                '성공_시그널': 0,
                '실패_시그널': 0,
                '성공률': 0,
                '평균_수익률': 0,
                '최대_수익률': 0,
                '평균_손실률': 0,
                '최대_손실률': 0,
                f'{self.signal_verify_days}일후_평균_수익률': 0
            }

        수익률_array = np.array(results['수익률_리스트'])
        양수_수익률 = 수익률_array[수익률_array > 0]
        음수_수익률 = 수익률_array[수익률_array <= 0]

        return {
            '전체_매수_시그널': results['전체_매수_시그널'],
            '성공_시그널': results['성공_시그널'],
            '실패_시그널': results['실패_시그널'],
            '성공률': (results['성공_시그널'] / results['전체_매수_시그널']) * 100,
            '평균_수익률': np.mean(양수_수익률) if len(양수_수익률) > 0 else 0,
            '최대_수익률': np.max(수익률_array) if len(수익률_array) > 0 else 0,
            '평균_손실률': np.mean(음수_수익률) if len(음수_수익률) > 0 else 0,
            '최대_손실률': np.min(수익률_array) if len(수익률_array) > 0 else 0,
            f'{self.signal_verify_days}일후_평균_수익률': np.mean(수익률_array)
        }

    # @st.cache_data
    def plot_stock_chart(self):
        """주가 차트 생성"""
        try:
            if self.df is None or self.df.empty:
                return None

            fig = go.Figure()

            # 캔들스틱 차트
            fig.add_trace(go.Candlestick(
                x=self.df.index,
                open=self.df['시가'],
                high=self.df['고가'],
                low=self.df['저가'],
                close=self.df['종가'],
                increasing_line_color='red',
                decreasing_line_color='blue',
                name='주가'
            ))

            # 이동평균선
            fig.add_trace(go.Scatter(
                x=self.df.index,
                y=self.df['5일선'],
                line=dict(color='red', width=1),
                name='5일 이동평균'
            ))

            fig.add_trace(go.Scatter(
                x=self.df.index,
                y=self.df['40일선'],
                line=dict(color='blue', width=1),
                name='40일 이동평균'
            ))

            # 매수 시그널 표시
            buy_signals = self.df[self.df['Signal'] == 1]            

            if not buy_signals.empty:
                # 성공/실패 시그널 구분
                success_signals = buy_signals[buy_signals.index.map(
                    lambda x: self.df.loc[x:].iloc[1:self.signal_verify_days + 1]['종가'].max() > self.df.loc[x]['종가']
                    if x < self.df.index[self.signal_verify_days * -1] else False
                )]

                failed_signals = buy_signals[buy_signals.index.map(
                    lambda x: self.df.loc[x:].iloc[1:self.signal_verify_days + 1]['종가'].max() <= self.df.loc[x]['종가']
                    if x < self.df.index[self.signal_verify_days * -1] else False
                )]

                # 성공 시그널 표시
                if not success_signals.empty:
                    fig.add_trace(go.Scatter(
                        x=success_signals.index,
                        y=success_signals['종가'],
                        mode='markers',
                        marker=dict(symbol='star', size=15, color='yellow'),
                        name='성공 시그널'
                    ))

                # 실패 시그널 표시
                if not failed_signals.empty:
                    fig.add_trace(go.Scatter(
                        x=failed_signals.index,
                        y=failed_signals['종가'],
                        mode='markers',
                        marker=dict(symbol='x', size=12, color='white'),
                        name='실패 시그널'
                    ))

            # 차트 스타일링
            fig.update_layout(
                template='plotly_dark',
                xaxis_rangeslider_visible=False,
                showlegend=True,
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0)'),
                xaxis=dict(type='date', tickformat='%Y-%m-%d'),
                yaxis=dict(tickformat=',d'),
                height=600
            )

            return fig
        except Exception as e:
            print(f"차트 생성 중 오류: {str(e)}")
            return None



