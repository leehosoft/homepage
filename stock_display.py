#@title ##**5.stock_display.py**
# %%writefile stock_display.py

import streamlit as st

class StockDisplay:
    def __init__(self):
        # Initialize all required session state variables
        if 'current_progress' not in st.session_state:
            st.session_state.current_progress = 0
        if 'analysis_running' not in st.session_state:
            st.session_state.analysis_running = False
        if 'analysis_paused' not in st.session_state:
            st.session_state.analysis_paused = False
        if 'analysis_index' not in st.session_state:
            st.session_state.analysis_index = 0
        if 'current_stocks' not in st.session_state:
            st.session_state.current_stocks = []
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'current_status_text' not in st.session_state:
            st.session_state.current_status_text = ""

        # Instance variables
        self.result_placeholders = {}

    def initialize_display(self):
        # Create containers for UI elements
        progress_container = st.container()
        control_container = st.container()

        with control_container:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("분석 시작", key="start_button"):
                    self._reset_analysis_state()
            with col2:
                if st.button("분석 일시정지",
                           key="pause_button",
                           disabled=not st.session_state.analysis_running):
                    st.session_state.analysis_paused = True
            with col3:
                if st.button("분석 재시작",
                           key="resume_button",
                           disabled=not st.session_state.analysis_paused):
                    st.session_state.analysis_paused = False
                    st.session_state.analysis_running = True

        with progress_container:
            self.progress_bar = st.progress(st.session_state.current_progress)
            self.progress_text = st.empty()
            self.status_text = st.empty()

            if st.session_state.current_progress > 0:
                self.progress_text.text(
                    f"진행률: {st.session_state.current_progress*100:.1f}% "
                    f"({st.session_state.analysis_index}/{len(st.session_state.current_stocks)})"
                )
                self.status_text.text(st.session_state.current_status_text)

    def _reset_analysis_state(self):
        st.session_state.analysis_running = True
        st.session_state.analysis_paused = False
        st.session_state.analysis_index = 0
        st.session_state.current_progress = 0
        st.session_state.current_status_text = ""
        st.session_state.analysis_results = {}

        st.session_state.current_stocks = []

    def create_placeholders(self, selected_stocks):
        self.result_placeholders.clear()
        for stock in selected_stocks:
            self.result_placeholders[stock] = st.empty()

    def update_progress(self, current, total):
        if not st.session_state.analysis_paused:
            progress = (current + 1) / total
            st.session_state.current_progress = progress
            self.progress_bar.progress(progress)
            self.progress_text.text(
                f"진행률: {progress*100:.1f}% ({current+1}/{total})"
            )

    def update_status(self, text):
        if not st.session_state.analysis_paused:
            st.session_state.current_status_text = text
            self.status_text.text(text)


    def _handle_start_analysis(self):
        st.session_state.analysis_running = True
        st.session_state.analysis_paused = False
        st.session_state.analysis_index = 0
        st.session_state.current_progress = 0
        st.session_state.current_status_text = ""
        st.session_state.analysis_results = {}
        st.rerun()

    def _handle_pause_analysis(self):
        st.session_state.analysis_paused = True
        st.rerun()

    def _handle_resume_analysis(self):
        st.session_state.analysis_paused = False
        st.session_state.analysis_running = True
        st.rerun()

    def _display_current_state(self):
        if st.session_state.current_progress > 0:
            st.session_state.progress_bar.progress(st.session_state.current_progress)
            st.session_state.progress_text.text(
                f"진행률: {st.session_state.current_progress*100:.1f}% "
                f"({st.session_state.analysis_index}/{len(st.session_state.current_stocks)})"
            )
            st.session_state.status_text.text(st.session_state.current_status_text)

    def create_placeholders(self, selected_stocks):
        self.result_placeholders = {stock: st.empty() for stock in selected_stocks}

    def display_stock_result(self, selected_stock, analyzer, results, verify_days):
        if selected_stock not in self.result_placeholders:
            self.result_placeholders[selected_stock] = st.empty()

        market_type = "KOSPI" if "[KOSPI]" in selected_stock else "KOSDAQ"
        stock_name = selected_stock.split(":")[1].strip()

        with self.result_placeholders[selected_stock].container():
            with st.expander(
                f"📊 [{market_type}] {stock_name} " +
                ("(최근 매수 시그널)" if analyzer.has_recent_signal() else ""),
                expanded=True
            ):
                chart_col, metrics_col = st.columns([2, 1])
                with chart_col:
                    st.plotly_chart(analyzer.plot_stock_chart(), use_container_width=True)
                with metrics_col:
                    self.display_metrics(results, verify_days)

    def display_metrics(self, results, verify_days):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("성공률", f"{results['성공률']:.2f}%")
            st.metric("평균 수익률", f"{results['평균_수익률']:.2f}%")
        with col2:
            st.metric("최대 수익률", f"{results['최대_수익률']:.2f}%")
            st.metric(f"{verify_days}일후 평균 수익률", f"{results[f'{verify_days}일후_평균_수익률']:.2f}%")

        st.write("### 상세 분석 결과")
        st.write(f"전체 매수 시그널: {results['전체_매수_시그널']}")
        st.write(f"성공 시그널: {results['성공_시그널']}")
        st.write(f"실패 시그널: {results['실패_시그널']}")
        st.write(f"최대 손실률: {results['최대_손실률']:.2f}%")

    def display_analysis_summary(self, displayed_count, error_stocks):
        if displayed_count > 0:
            st.success(f"분석 완료: {displayed_count}개 종목이 조회되었습니다.")
        else:
            st.warning("표시할 종목이 없습니다.")

        if error_stocks:
            with st.expander("데이터 조회 실패 종목", expanded=False):
                st.write("다음 종목들은 데이터 조회에 실패했거나 분석 조건을 만족하지 않았습니다:")
                for error_stock in error_stocks:
                    st.write(f"- {error_stock}")
