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
        st.title("이호소프트 AI 시스템")
        
        # 회사 소개 섹션
        st.header("회사 소개")
        st.write("""
        이호소프트는 최첨단 AI 기술을 활용한 금융투자,게임,운세,로또 등 
        모든 흥미있는 솔루션을 제공하는 기업입니다.
        2023년 설립 이후, 빅데이터와 인공지능 기술을 기반으로 
        혁신적인 각종 서비스를 제공하려고 합니다.
        
        **핵심 가치**
        - 흥미있는 기술 솔루션
        - 신뢰성 있는 데이터 분석
        - 철저한 고객 중심 서비스
        
        **주요 서비스**
        - 실시간 주식 시장 분석
        - AI 기반 투자 추천
        - 맞춤형 포트폴리오 구성
        - AI 기반 로또 예측
        - 게임
        - 재미있는 기술 서비스 제공
        - 기타 흥미 있는 모든것들 요청에 의한 서비스 구성       
        """)
        
        # 조직도 표시
        st.header("조직도")
        
        try:
            # SVG 파일 표시
            with open("organi.svg", "r", encoding='utf-8') as file:
                svg_content = file.read()
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; margin: 20px 0;">
                        {svg_content}
                    </div>
                    """, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("조직도 파일(organi.svg)을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"조직도를 불러오는 중 오류가 발생했습니다: {str(e)}")
        
        # 시스템 주요 기능 소개
        st.header("시스템 주요 기능")
        st.write("""
        - **코스피/코스닥 종목 분석**: 실시간 시장 데이터 기반 분석
        - **AI 기반 매매 시그널**: 딥러닝 모델을 활용한 매매 포인트 제공
        - **포트폴리오 최적화**: 개인별 맞춤 포트폴리오 구성
        - **리스크 관리**: 체계적인 위험 관리 시스템
        - **로또예측**: 사주팔자,AI 모델을 이용
        - **게임**: 소소한 게임 구성
        - **신기한 것들**: 딥페이크,챗,RAG
        """)

    def show_analysis1(self):
        st.title("기술적 분석 시스템(테스트용)")
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
