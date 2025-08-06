# 📊 Steel Sales Analysis Agent

**철강 전문 데이터 분석 Agent**는 LangGraph + LangChain + Streamlit 기반으로 구축된 자연어 기반 분석 시스템입니다.
사용자가 질문을 자연어로 입력하면, 내부 Pandas 기반 Excel 데이터를 자동으로 분석하여 정량적 통계와 요약 정보를 제공합니다.

---

## 🔧 주요 기술 스택

* **LangGraph**: 복잡한 분기형 워크플로우 관리 (멀티 노드 기반 흐름 제어)
* **LangChain**: OpenAI 기반 에이전트 구성 및 도구 자동 선택
* **Streamlit**: 웹 기반 인터페이스 제공
* **Pandas**: 역셀 데이터 분석용 백엔드 엔진
* **OpenAI (GPT-4o)**: 자연어 이해 및 분석 응답 생성

---

## 🧠 해당 기능

| 기능                    | 설명                                                     |
| --------------------- | ------------------------------------------------------ |
| ✅ 자연어 기반 질의 분석        | “2023년 냉열사업실 매주는?” 처럼 자유로운 질문 가능                       |
| ✅ 내부 분석 도구 자동 선택      | LangChain Agent가 질문 의도를 파악하여 적절한 Tool 선택               |
| ✅ 복수 노드 처리            | `router_node` → `agent_node` 또는 `fallback_node`로 자동 분기 |
| ✅ LangGraph Studio 진실 | 시각적인 플로우 트래킹 및 디버극 가능                                  |
| ✅ Streamlit 진실        | 사용자 착기적인 웹 기반 질문·\xb7응답 UI 제공                          |

---

## 폴더 구조

```
langgraph_agent/
├── agent/
│   ├── tools.py                 # 실제 분석 로직 정의
│   ├── tool_registry.py         # Tool 리스트 정의 및 등록
│   ├── graph_nodes.py           # LangGraph 노드 정의
│   ├── graph_flow.py            # 전체 플로우 정의 및 커필
├── app.py                       # Streamlit 실행 파일
├── langgraph.json               # LangGraph Studio 용 플로우 정의 파일
└── .env                         # OpenAI API 키 등 환경 변수
```

---

## 🚀 실행 방법

### 1. 환경 설정

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env` 파일 생성:

```
OPENAI_API_KEY=your_openai_key_here
```

### 2. LangGraph Studio 실행

```bash
langgraph dev langgraph.json
```

> [http://127.0.0.1:2024](http://127.0.0.1:2024) 에서 플로우 디버극 가능

### 3. Streamlit 앱 실행

```bash
streamlit run app.py
```

---

## 💡 예시 질문
* `2024년 1년기 자동차소재사업실 매주수량은?`
* `미국향 공급량은 어느러한가요?`
* `2023년 전체 영업이익은 알려줘`

---

## 📌 향후 추가 계획
* ✅ Chat history 지속 저장
* ✅ 역셀 업로드 UI 통합
* ✅ 사용자 맞춤형 자동 분석 리포트 생성
* ✅ 자동 시각화 기능 (Matplotlib / Altair 등 연계)
