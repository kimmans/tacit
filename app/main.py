"""
Tacit - SECI-based Knowledge Creation Service

Main Streamlit Application

"We can know more than we can tell" - Michael Polanyi
"""

import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv

# app 폴더를 모듈 경로에 추가
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Tacit - 당신의 지식을 비즈니스 기회로 연결하세요",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 메인 컨테이너 */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }

    /* Ba 표시 카드 */
    .ba-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    /* 단계 진행 표시 */
    .phase-indicator {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }

    .phase-item {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0 0.25rem;
    }

    .phase-active {
        background-color: #667eea;
        color: white;
    }

    .phase-completed {
        background-color: #48bb78;
        color: white;
    }

    .phase-pending {
        background-color: #e2e8f0;
        color: #718096;
    }

    /* 출력물 카드 */
    .output-card {
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* 채팅 메시지 */
    .user-message {
        background-color: #e3f2fd;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }

    .assistant-message {
        background-color: #f5f5f5;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def get_api_key() -> str:
    """API 키 가져오기 (Streamlit secrets 우선)"""
    # 1. Streamlit secrets에서 가져오기 (Streamlit Cloud 배포용)
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass

    # 2. 환경 변수에서 가져오기 (로컬 개발용)
    env_key = os.getenv("ANTHROPIC_API_KEY")
    if env_key:
        return env_key

    return ""


def init_session_state():
    """세션 상태 초기화"""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False

    if "started" not in st.session_state:
        st.session_state.started = False

    # 자동으로 API 키 설정 시도
    if not st.session_state.api_key_set:
        api_key = get_api_key()
        if api_key:
            create_orchestrator(api_key)


def create_orchestrator(api_key: str):
    """Orchestrator 생성"""
    from agents.orchestrator import SECIOrchestrator

    st.session_state.orchestrator = SECIOrchestrator(api_key=api_key)
    st.session_state.api_key_set = True


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.title("🧠 Tacit")
        st.markdown("*당신의 지식을 비즈니스 기회로 연결하세요*")

        st.divider()

        # API 키 상태 표시
        if st.session_state.api_key_set:
            st.success("✅ API 연결됨")
        else:
            st.error("❌ API 키가 설정되지 않았습니다")
            st.caption("Streamlit secrets 또는 환경 변수를 확인하세요")

        st.divider()

        # 현재 단계 표시
        if st.session_state.orchestrator:
            phase_info = st.session_state.orchestrator.get_phase_info()

            st.subheader("📍 현재 위치")
            st.markdown(f"**{phase_info['phase_name']}**")
            st.caption(phase_info['phase_description'])

            st.divider()

            st.subheader("🏛️ 현재 Ba(場)")
            st.info(phase_info['ba_description'])

            st.divider()

            st.subheader("🌀 나선 진행")
            render_phase_progress(phase_info)

        st.divider()

        # 컨트롤 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 새로 시작", use_container_width=True):
                if st.session_state.orchestrator:
                    st.session_state.orchestrator.reset()
                st.session_state.messages = []
                st.session_state.started = False
                st.rerun()

        with col2:
            if st.button("⏭️ 단계 넘기기", use_container_width=True):
                if st.session_state.orchestrator:
                    st.session_state.orchestrator.force_advance_phase()
                    st.rerun()

        st.divider()

        # 산출물 보기
        if st.session_state.orchestrator:
            outputs = st.session_state.orchestrator.get_all_outputs()
            if outputs:
                st.subheader("📋 산출물")
                for key, value in outputs.items():
                    with st.expander(key):
                        st.json(value)


def render_phase_progress(phase_info: dict):
    """단계 진행 표시"""
    phases = [
        ("S", "사회화"),
        ("E", "표출화"),
        ("C", "연결화"),
        ("I", "내면화"),
    ]

    current_phase = phase_info["phase"]
    phase_order = ["socialization", "externalization", "combination", "internalization", "complete"]
    current_idx = phase_order.index(current_phase)

    cols = st.columns(4)
    for i, (letter, name) in enumerate(phases):
        with cols[i]:
            if i < current_idx:
                st.success(f"**{letter}**\n{name}")
            elif i == current_idx and current_phase != "complete":
                st.info(f"**{letter}**\n{name}")
            else:
                st.caption(f"**{letter}**\n{name}")


def render_chat():
    """채팅 인터페이스 렌더링"""
    # 환영 메시지 표시 (첫 시작 시)
    if not st.session_state.started and st.session_state.orchestrator:
        welcome = st.session_state.orchestrator.get_welcome_message()
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome
        })
        st.session_state.started = True

    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        if not st.session_state.api_key_set:
            st.warning("먼저 사이드바에서 API 키를 설정해주세요.")
            return

        # 사용자 메시지 표시
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                response, info = st.session_state.orchestrator.chat(prompt)

                # 단계 변경 알림
                if info.get("phase_changed"):
                    st.success(f"✨ {info['phase_name']} 단계로 진입합니다!")
                    st.info(info['ba_description'])

                st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()


def render_main_content():
    """메인 컨텐츠 렌더링"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Tacit</h1>
        <p><em>"We can know more than we can tell"</em> — Michael Polanyi</p>
        <p>당신의 암묵지를 발견하고, 비즈니스 기회로 연결합니다</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.api_key_set:
        st.warning("⚠️ API 키가 설정되지 않았습니다. 관리자에게 문의하세요.")

        # 서비스 소개
        st.markdown("---")
        st.subheader("🎯 Tacit 서비스란?")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **SECI 모델 기반 지식창조**

            노나카 이쿠지로의 SECI 모델을 AI로 구현했습니다:

            1. **사회화 (S)**: 경험 공유를 통한 암묵지 탐색
            2. **표출화 (E)**: 소크라테스식 대화로 언어화
            3. **연결화 (C)**: 비즈니스 기회와 연결
            4. **내면화 (I)**: 실행 가능한 액션플랜
            """)

        with col2:
            st.markdown("""
            **Ba(場) - 지식창조의 장**

            각 단계에 맞는 대화 환경을 제공합니다:

            - 🌱 **창발의 장**: 공감과 신뢰의 공간
            - 💬 **대화의 장**: 깊은 질문과 통찰
            - ⚙️ **시스템화의 장**: 구조화와 연결
            - 🎯 **실천의 장**: 실행과 검증
            """)

        st.markdown("---")

        with st.expander("📚 이론적 배경"):
            st.markdown("""
            ### 마이클 폴라니의 암묵적 지식 (Tacit Knowledge)

            > "우리는 말할 수 있는 것보다 더 많이 알고 있다"

            - 1966년 *The Tacit Dimension*에서 제시
            - 경험을 통해 체득되지만 언어화하기 어려운 지식
            - 예: 자전거 타기, 얼굴 인식, 장인의 손맛

            ### 노나카 이쿠지로의 SECI 모델

            - 1995년 *The Knowledge-Creating Company*에서 제시
            - 조직 내 지식이 암묵지↔형식지 사이를 순환
            - 나선형으로 확장되며 지식이 증폭됨
            """)
    else:
        render_chat()


def main():
    """메인 함수"""
    init_session_state()
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()
