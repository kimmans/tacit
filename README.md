# Tacit - 암묵지 기반 비즈니스 인사이트 도출 서비스

> *"We can know more than we can tell"* — Michael Polanyi

**Tacit**은 전문가들의 암묵지(Tacit Knowledge)를 발견하고, 이를 비즈니스 기회로 연결하는 AI 서비스입니다.

## 이론적 기반

### 마이클 폴라니 - 암묵적 지식 (Tacit Knowledge)
- 1966년 *The Tacit Dimension*에서 제시
- "우리는 말할 수 있는 것보다 더 많이 알고 있다"
- 경험을 통해 체득되지만 언어화하기 어려운 지식

### 노나카 이쿠지로 - SECI 모델
- 1995년 *The Knowledge-Creating Company*에서 제시
- 조직 내 지식이 암묵지↔형식지 사이를 순환
- 4단계: 사회화(S) → 표출화(E) → 연결화(C) → 내면화(I)

### Ba(場) - 지식창조의 장
- 지식이 공유되고, 창조되고, 활용되는 맥락(장소)
- Originating Ba (창발의 장) - 사회화
- Dialoguing Ba (대화의 장) - 표출화
- Systemising Ba (시스템화의 장) - 연결화
- Exercising Ba (실천의 장) - 내면화

## 설치 방법

### 1. 의존성 설치

```bash
cd tacit
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열고 Anthropic API 키를 입력:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. 실행

```bash
# 방법 1: run.py 사용
python run.py

# 방법 2: streamlit 직접 실행
streamlit run app/main.py
```

브라우저에서 `http://localhost:8501` 접속

## Streamlit Cloud 배포

### 1. GitHub에 코드 푸시

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Streamlit Cloud 설정

1. [Streamlit Cloud](https://share.streamlit.io)에서 새 앱 생성
2. GitHub 저장소 연결
3. Main file path: `app/main.py`
4. **Secrets** 설정에서 API 키 추가:
   ```toml
   ANTHROPIC_API_KEY = "your-anthropic-api-key"
   ```

### 3. 배포 완료

Streamlit Cloud가 자동으로 앱을 빌드하고 배포합니다.

## 사용 방법

### SECI 나선 4단계

1. **사회화 단계 (Socialization)** - 창발의 장
   - AI 공감자와 대화하며 경험을 탐색
   - 암묵지가 숨어있을 영역 발견
   - **Output**: 경험 지도(Experience Map)

2. **표출화 단계 (Externalization)** - 대화의 장
   - AI 표출자와 소크라테스식 대화
   - "말할 수 없는 것"을 언어화
   - **Output**: 암묵지 명세서(Tacit Knowledge Specification)

3. **연결화 단계 (Combination)** - 시스템화의 장
   - 암묵지의 비즈니스 가치 분석
   - 희소성, 수요, 전달가능성 평가
   - **Output**: 비즈니스 기회 카드 3개

4. **내면화 단계 (Internalization)** - 실천의 장
   - 구체적 액션플랜 수립
   - 최소 실행 가능 실험(MVE) 설계
   - **Output**: 주간 액션플랜

## 프로젝트 구조

```
tacit/
├── app/
│   ├── main.py                 # Streamlit 메인 앱
│   ├── agents/
│   │   ├── orchestrator.py     # SECI 나선 관리자
│   │   ├── socializer.py       # S: 공감자 Agent
│   │   ├── externalizer.py     # E: 표출자 Agent
│   │   ├── combiner.py         # C: 연결자 Agent
│   │   ├── internalizer.py     # I: 내면화 촉진자 Agent
│   │   └── challenger.py       # 검증자 Agent (예정)
│   ├── prompts/
│   │   └── seci_prompts.py     # SECI 단계별 프롬프트
│   ├── models/
│   │   └── knowledge.py        # Pydantic 모델
│   └── utils/
│       └── helpers.py          # 유틸리티 함수
├── .streamlit/
│   └── secrets.toml.example    # Streamlit secrets 템플릿
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
└── README.md
```

## 기술 스택

- **LLM**: Claude API (Anthropic)
- **UI**: Streamlit
- **Agent Framework**: 자체 구현 (LangGraph 스타일)
- **Data Models**: Pydantic

## 참고 문헌

- Polanyi, M. (1966). *The Tacit Dimension*
- Polanyi, M. (1958). *Personal Knowledge*
- Nonaka, I. & Takeuchi, H. (1995). *The Knowledge-Creating Company*
- Nonaka, I. & Konno, N. (1998). "The Concept of 'Ba'"

## 라이센스

MIT License
