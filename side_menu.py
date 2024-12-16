#@title ##**2.side_menu.py**
# %%writefile side_menu.py
import streamlit as st

class SideMenu:
    def __init__(self):
        self.menu_items = {
            "Home": self.show_home,
            "주식분석시스템": {
                "증권분석1": self.show_analysis1,
                "증권분석2": self.show_analysis2,
                "증권분석3": self.show_analysis3
            }
        }

    def show_menu(self):
        with st.sidebar:
            st.title("메뉴")
            selected_menu = st.radio("메인 메뉴", list(self.menu_items.keys()))

            if selected_menu == "주식분석시스템":
                sub_menu = st.radio("서브 메뉴", list(self.menu_items["주식분석시스템"].keys()))
                return selected_menu, sub_menu

            return selected_menu, None

    def show_home(self):
        st.title("주식 분석 시스템")
        st.write("""
        ### 시스템 소개
        이 시스템은 주식 시장의 기술적 분석을 제공합니다.

        ### 주요 기능
        - 코스피/코스닥 종목 분석
        - 기술적 지표 기반 매매 시그널
        - 실시간 차트 분석
        - 수익률 분석 리포트
        """)

    def show_analysis1(self):
        st.title("기술적 분석 시스템")
        st.write("""
        ### 분석 방법
        - 이동평균선 교차
        - 외인/기관 순매수
        - 거래량 분석
        """)

    def show_analysis2(self):
        st.title("펀더멘탈 분석")
        st.write("""
        ### 준비중입니다
        - 재무제표 분석
        - 시장 동향 분석
        - 산업별 분석
        """)

    def show_analysis3(self):
        st.title("포트폴리오 분석")
        st.write("""
        ### 준비중입니다
        - 포트폴리오 구성
        - 자산 배분 전략
        - 위험 관리
        """)


