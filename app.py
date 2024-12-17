#@title ##**6.app.py**
# %%writefile app.py

# app.py
import streamlit as st
from stock_selector import StockSelector
from stock_display import StockDisplay
from stock_analyzer import StockAnalyzer
from side_menu import SideMenu

def main():
    st.set_page_config(page_title="이호소프트 AI 시스템", layout="wide")

    side_menu = SideMenu()
    selected_menu, sub_menu = side_menu.show_menu()

    if selected_menu == "Home":
        side_menu.show_home()
    elif selected_menu == "주식분석시스템":
        if sub_menu == "증권분석(test)":
            show_stock_analysis()
        elif sub_menu == "증권분석2":
            side_menu.show_analysis2()
        elif sub_menu == "증권분석3":
            side_menu.show_analysis3()


# app.py
def show_stock_analysis():
    st.title("주식 기술적 분석")

    # 세션 상태 초기화
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.analysis_running = False
        st.session_state.analysis_paused = False
        st.session_state.analysis_index = 0
        st.session_state.current_stocks = []
        st.session_state.analysis_results = {}

    selector = StockSelector()
    selection = selector.show_selector()

    display_manager = StockDisplay()
    display_manager.initialize_display()

    if selection['selected_stocks']:
        if st.session_state.analysis_running and not st.session_state.analysis_paused:
            # 새로운 분석 시작 시
            if not st.session_state.current_stocks:
                st.session_state.current_stocks = selection['selected_stocks']
                display_manager.create_placeholders(st.session_state.current_stocks)

            error_stocks = []
            total_stocks = len(st.session_state.current_stocks)

            # 이전 결과 표시
            if st.session_state.analysis_results:
                for stock in st.session_state.analysis_results:
                    analyzer, results = st.session_state.analysis_results[stock]
                    display_manager.display_stock_result(stock, analyzer, results)

            # 새로운 분석 진행
            for idx in range(st.session_state.analysis_index, total_stocks):
                if st.session_state.analysis_paused:
                    st.warning(f"분석이 일시중지되었습니다. ({idx}/{total_stocks})")
                    break

                selected_stock = st.session_state.current_stocks[idx]
                display_manager.update_progress(idx, total_stocks)

                try:
                    ticker = selected_stock.split(":")[0].split("]")[1].strip()
                    stock_name = selected_stock.split(":")[1].strip()

                    # display_manager.status_text.text(f"분석 중: {stock_name}")
                    display_manager.update_status(f"분석 중: {stock_name}")
                    analyzer = StockAnalyzer()
                    analyzer.set_display_option(selection['show_all'], selection['show_recent_only'])
                    df = analyzer.get_stock_data(ticker, selection['start_date'], selection['end_date'])

                    if df is not None:
                        analyzer.calculate_technical_indicators()
                        analyzer.generate_signals()
                        results = analyzer.analyze_performance()

                        if results is not None:
                            st.session_state.analysis_results[selected_stock] = (analyzer, results)
                            display_manager.display_stock_result(selected_stock, analyzer, results)
                    else:
                        error_stocks.append(stock_name)
                        if selected_stock in display_manager.result_placeholders:
                            display_manager.result_placeholders[selected_stock].empty()

                except Exception as e:
                    error_stocks.append(f"{stock_name} (오류: {str(e)})")
                    if selected_stock in display_manager.result_placeholders:
                        display_manager.result_placeholders[selected_stock].empty()
                    continue

                st.session_state.analysis_index = idx + 1
                # time.sleep(0.1)

            if st.session_state.analysis_index >= total_stocks:
                st.session_state.analysis_running = False
                st.session_state.analysis_paused = False
                display_manager.display_analysis_summary(len(st.session_state.analysis_results), error_stocks)

        elif st.session_state.analysis_paused:
            st.warning("분석이 일시중지되었습니다. '분석 재시작' 버튼을 클릭하여 계속하세요.")
            # 일시정지 상태에서도 이전 결과 표시
            for stock in st.session_state.analysis_results:
                analyzer, results = st.session_state.analysis_results[stock]
                display_manager.display_stock_result(stock, analyzer, results)
    else:
        st.warning("분석할 종목을 선택해주세요.")

if __name__ == "__main__":
    main()
