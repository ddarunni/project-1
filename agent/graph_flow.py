import os
import operator
from typing import TypedDict, Annotated, List, Any

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# --- 1. 설정 (Configuration) ---
# 스크립트의 주요 설정을 상단에 상수로 정의하여 관리합니다.
MODEL_NAME = "gpt-4o"
ROUTING_KEYWORDS = ["사업실", "그룹", "판매량", "매출액", "영업이익", "세전이익","공급사", "고객사", "국가"]

# 프롬프트 로더 import
try:
    from agent.prompt_loader import get_combined_prompt
    SYSTEM_PROMPT = get_combined_prompt()
except ImportError:
    SYSTEM_PROMPT = "너는 철강 데이터 분석 전문가야. 사용자 질문에 맞는 도구를 선택해서 정확한 수치를 포함한 한국어 답변을 해줘."

# --- 2. 상태 정의 (State Definition) ---
# 그래프 전체에서 사용될 상태 객체의 구조를 정의합니다.
class AgentState(TypedDict):
    input: str
    output: str
    chat_history: Annotated[List[AnyMessage], operator.add]
    df: Any
    # Context Aware Node 관련
    enhanced_input: str
    context_used: bool
    context_info: dict
    # Intent Classification Node 관련
    intent_info: dict
    processing_path: str
    # Query Planning Node 관련
    query_plan: dict

# --- 3. 에이전트 및 그래프 구성 요소 (Agent & Graph Components) ---

def create_agent_executor(api_key: str, tools: list) -> AgentExecutor:
    """AgentExecutor를 생성하고 반환합니다."""
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0, openai_api_key=api_key)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])
    
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True # 파싱 에러 발생 시 에이전트가 강건하게 대응하도록 설정
    )

# --- 노드 함수들 ---
def router_node(state: AgentState) -> dict:
    """상태를 변경하지 않는 라우팅 진입점 노드입니다."""
    print("--- 라우터 진입 ---")
    return {}

def context_aware_node(state: AgentState) -> dict:
    """이전 대화 맥락을 활용하여 현재 질문을 향상시키는 노드입니다."""
    print("--- Context Aware 노드 실행 ---")
    
    current_input = state["input"]
    chat_history = state.get("chat_history", [])
    
    # 참조어 패턴 정의
    reference_patterns = ["그것", "이전", "앞서", "더", "또한", "그 결과", "그런데", "그리고"]
    
    context_info = {
        "has_reference": False,
        "reference_type": None,
        "previous_entities": [],
        "enhancement_applied": False
    }
    
    enhanced_input = current_input
    context_used = False
    
    # 참조어가 있는지 확인
    has_references = any(ref in current_input for ref in reference_patterns)
    
    if has_references and chat_history:
        context_used = True
        context_info["has_reference"] = True
        
        # 최근 대화에서 주요 엔티티 추출
        last_conversations = chat_history[-2:] if len(chat_history) >= 2 else chat_history
        entities = []
        
        for conv in last_conversations:
            if isinstance(conv, str):
                # 주요 키워드 추출
                keywords = ["사업실", "그룹", "매출", "수량", "영업이익", "세전이익"]
                for keyword in keywords:
                    if keyword in conv:
                        # 키워드 앞의 수식어까지 포함해서 추출
                        words = conv.split()
                        for i, word in enumerate(words):
                            if keyword in word:
                                if i > 0 and len(words[i-1]) > 1:
                                    entity = f"{words[i-1]} {word}"
                                    entities.append(entity)
                                else:
                                    entities.append(word)
        
        context_info["previous_entities"] = entities
        
        # 참조어 해결
        if "그것" in current_input and entities:
            main_entity = entities[-1] if entities else "이전 결과"
            enhanced_input = current_input.replace("그것", main_entity)
            context_info["reference_type"] = "direct_reference"
            context_info["enhancement_applied"] = True
            
        elif any(word in current_input for word in ["더", "또한", "추가로"]) and entities:
            # 암묵적 컨텍스트 추가
            main_entity = entities[-1] if entities else ""
            if main_entity and main_entity not in current_input:
                enhanced_input = f"{main_entity}의 {current_input}"
                context_info["reference_type"] = "implicit_context"
                context_info["enhancement_applied"] = True
    
    print(f"원본 질문: {current_input}")
    print(f"향상된 질문: {enhanced_input}")
    print(f"컨텍스트 사용: {context_used}")
    
    return {
        "enhanced_input": enhanced_input,
        "context_used": context_used,
        "context_info": context_info
    }

def intent_classification_node(state: AgentState) -> dict:
    """질문의 의도를 분류하고 처리 경로를 결정하는 노드입니다."""
    print("--- Intent Classification 노드 실행 ---")
    
    # Context Aware Node에서 향상된 질문이 있으면 사용, 없으면 원본 사용
    input_text = state.get("enhanced_input", state["input"]).lower()
    
    # 의도 분류 카테고리 정의
    intent_patterns = {
        "aggregation": ["합계", "총", "전체", "모든", "전부", "sum", "total"],
        "comparison": ["비교", "vs", "대비", "차이", "비해", "보다"],
        "ranking": ["상위", "하위", "순위", "가장", "최고", "최저", "top", "높은", "낮은"],
        "trend": ["추세", "변화", "증가", "감소", "시간별", "기간별", "년도별", "월별"],
        "filtering": ["조건", "필터", "~인", "~만", "~중에서", "~에서"],
        "statistical": ["평균", "최대", "최소", "표준편차", "분산", "중앙값"]
    }
    
    # 복잡도 지표 정의
    complexity_indicators = {
        "high": ["그룹별로", "세분화", "상세히", "각각", "비교분석", "분석해", "자세히"],
        "medium": ["기간별", "월별", "분기별", "연도별", "나누어", "구분"],
        "low": ["총", "전체", "합계", "개수", "얼마", "몇"]
    }
    
    # 의도 분류
    detected_intent = "general"
    confidence = 0.0
    
    for intent, patterns in intent_patterns.items():
        matches = sum(1 for pattern in patterns if pattern in input_text)
        if matches > 0:
            current_confidence = matches / len(patterns)
            if current_confidence > confidence:
                detected_intent = intent
                confidence = current_confidence
    
    # 복잡도 분류
    complexity = "medium"  # 기본값
    complexity_score = 0
    
    for level, indicators in complexity_indicators.items():
        matches = sum(1 for indicator in indicators if indicator in input_text)
        if matches > complexity_score:
            complexity = level
            complexity_score = matches
    
    # 필요한 도구 예측
    tool_predictions = {
        "aggregation": ["calculate_sum", "calculate_total", "group_statistics"],
        "comparison": ["compare_groups", "calculate_percentage", "filter_data"],
        "ranking": ["sort_by_column", "get_top_n", "calculate_rank"],
        "trend": ["time_series_analysis", "calculate_growth"],
        "filtering": ["filter_data", "search_data"],
        "statistical": ["calculate_statistics", "describe_data"]
    }
    
    predicted_tools = tool_predictions.get(detected_intent, ["general_analysis"])
    
    # 처리 경로 결정
    processing_path = "agent_node"  # 기본값
    
    if detected_intent == "aggregation" and complexity == "low":
        processing_path = "quick_answer_node"  # 향후 구현 예정
    elif not any(keyword in input_text for keyword in ROUTING_KEYWORDS):
        processing_path = "fallback_node"
    
    intent_info = {
        "intent": detected_intent,
        "confidence": confidence,
        "complexity": complexity,
        "predicted_tools": predicted_tools,
        "processing_path": processing_path,
        "analysis": {
            "input_length": len(input_text),
            "keyword_matches": sum(1 for keyword in ROUTING_KEYWORDS if keyword in input_text)
        }
    }
    
    print(f"감지된 의도: {detected_intent} (신뢰도: {confidence:.2f})")
    print(f"복잡도: {complexity}")
    print(f"처리 경로: {processing_path}")
    
    return {
        "intent_info": intent_info,
        "processing_path": processing_path
    }

def query_planning_node(state: AgentState) -> dict:
    """복잡한 질문을 분석하고 최적의 실행 계획을 수립합니다."""
    print("--- Query Planning 노드 실행 ---")
    
    # Context Aware Node에서 향상된 질문이 있으면 사용
    input_text = state.get("enhanced_input", state["input"]).lower()
    intent_info = state.get("intent_info", {})
    
    # 컬럼-키워드 매핑 (tools.py와 동일)
    column_keywords = {
        "Division": ["사업실", "사업부", "부문", "스테인리스", "전기강판", "열연", "냉연"],
        "Country": ["국가", "나라", "한국", "중국", "일본", "미국", "국내", "해외"],
        "Period/Year": ["년", "년도", "분기", "상반기", "하반기", "2023", "2024", "2022"],
        "Supplier": ["공급사", "공급업체", "posco", "포스코"],
        "FundsCenter": ["그룹", "센터", "funds", "펀드"]
    }
    
    metric_keywords = {
        "매출수량(M/T)": ["매출수량", "판매량", "수량", "톤"],
        "1.매출액": ["매출액", "매출", "sales"],
        "5.영업이익": ["영업이익", "이익", "profit"],
        "8.세전이익": ["세전이익", "세전"]
    }
    
    # 필요한 컬럼들 감지
    required_columns = []
    detected_metrics = []
    
    for column, keywords in column_keywords.items():
        if any(keyword in input_text for keyword in keywords):
            required_columns.append(column)
    
    for metric, keywords in metric_keywords.items():
        if any(keyword in input_text for keyword in keywords):
            detected_metrics.append(metric)
    
    # 기본 메트릭 설정
    if not detected_metrics:
        detected_metrics = ["매출수량(M/T)"]
    
    # 질문 복잡도 분석
    complexity_score = 0
    complexity_indicators = {
        "multiple_filters": len(required_columns) >= 2,
        "comparison": any(word in input_text for word in ["비교", "vs", "대비", "차이"]),
        "ranking": any(word in input_text for word in ["상위", "하위", "순위", "가장"]),
        "temporal": any(word in input_text for word in ["년도별", "기간별", "추세", "변화"]),
        "aggregation": any(word in input_text for word in ["합계", "총", "전체", "모든"])
    }
    
    complexity_score = sum(complexity_indicators.values())
    
    if complexity_score >= 3:
        query_complexity = "high"
    elif complexity_score >= 1:
        query_complexity = "medium"
    else:
        query_complexity = "low"
    
    # 실행 계획 수립
    execution_plan = {
        "strategy": "unknown",
        "recommended_tools": [],
        "parameters": {},
        "fallback_plan": "use_existing_tools"
    }
    
    # 비교 분석 계획
    if complexity_indicators["comparison"]:
        execution_plan["strategy"] = "comparative_analysis"
        execution_plan["recommended_tools"] = ["comparative_analysis_tool"]
        
        # 비교 대상 추출 시도
        comparison_entities = extract_comparison_entities(input_text)
        execution_plan["parameters"] = {
            "comparison_detected": True,
            "entities": comparison_entities,
            "primary_metric": detected_metrics[0]
        }
    
    # 다중 필터 계획
    elif len(required_columns) >= 2:
        execution_plan["strategy"] = "multi_column_query"
        execution_plan["recommended_tools"] = ["advanced_multi_column_query"]
        execution_plan["parameters"] = {
            "filter_columns": required_columns,
            "metrics": detected_metrics,
            "complexity": query_complexity
        }
    
    # 단일 조건 계획
    elif len(required_columns) == 1:
        execution_plan["strategy"] = "single_column_query" 
        execution_plan["recommended_tools"] = ["existing_single_tools"]
        execution_plan["parameters"] = {
            "column": required_columns[0],
            "metric": detected_metrics[0]
        }
    
    # 일반 계획
    else:
        execution_plan["strategy"] = "general_analysis"
        execution_plan["recommended_tools"] = ["get_overall_summary"]
    
    query_plan = {
        "required_columns": required_columns,
        "detected_metrics": detected_metrics, 
        "complexity": query_complexity,
        "complexity_indicators": complexity_indicators,
        "execution_plan": execution_plan,
        "confidence": min(0.9, 0.3 + 0.2 * len(required_columns))
    }
    
    print(f"분석된 컬럼: {required_columns}")
    print(f"감지된 메트릭: {detected_metrics}")
    print(f"복잡도: {query_complexity}")
    print(f"추천 전략: {execution_plan['strategy']}")
    
    return {
        "query_plan": query_plan
    }

def extract_comparison_entities(text: str) -> list:
    """비교 대상 엔티티를 추출합니다."""
    entities = []
    
    # 간단한 패턴 매칭으로 비교 대상 추출
    comparison_patterns = [
        r'(\w+)\s*vs\s*(\w+)',
        r'(\w+)\s*과\s*(\w+)\s*비교',
        r'(\w+)\s*와\s*(\w+)\s*비교',
        r'(\w+)\s*대비\s*(\w+)'
    ]
    
    import re
    for pattern in comparison_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            entities.extend(match)
    
    return entities[:4]  # 최대 4개까지만

def enhanced_route_logic(state: AgentState) -> str:
    """Intent Classification 결과를 기반으로 처리 경로를 결정하는 향상된 라우팅 로직입니다."""
    intent_info = state.get("intent_info", {})
    processing_path = intent_info.get("processing_path", "agent_node")
    
    print(f">> Intent 기반 경로: {processing_path}")
    
    # 현재는 quick_answer_node가 없으므로 agent_node로 라우팅
    if processing_path == "quick_answer_node":
        return "agent_node"
    
    return processing_path

def route_logic(state: AgentState) -> str:
    """기존 라우팅 로직 (호환성 유지용)"""
    user_input = state["input"]
    print(f"입력 분석: '{user_input}'")
    if any(keyword in user_input for keyword in ROUTING_KEYWORDS):
        print(">> 경로: 에이전트 노드")
        return "agent_node"
    else:
        print(">> 경로: 폴백 노드")
        return "fallback_node"

def agent_node(state: AgentState, agent_executor: AgentExecutor) -> dict:
    """데이터 분석을 수행하는 에이전트 노드입니다."""
    print("--- 에이전트 노드 실행 ---")
    
    # df를 전역 변수로 설정하여 tools에서 접근 가능하도록 함
    import agent.tools as tools_module
    if hasattr(tools_module, 'set_dataframe'):
        tools_module.set_dataframe(state["df"])
    
    # Context Aware Node에서 향상된 질문이 있으면 사용, 없으면 원본 사용
    input_to_use = state.get("enhanced_input", state["input"])
    
    print(f"사용할 입력: {input_to_use}")
    
    result = agent_executor.invoke({
        "input": input_to_use,
        "chat_history": state["chat_history"]
    })
    
    # 중간 단계와 출처 정보 포함
    df = state.get("df")
    sheet_info = ""
    if df is not None:
        # 실제 사용된 컬럼들을 추정 (키워드 기반)
        question = state["input"].lower()
        used_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ["매출", "판매", "수량", "영업이익", "사업실", "그룹"]):
                used_columns.append(col)
        
        if used_columns:
            sheet_info = f" (주요 참고 컬럼: {', '.join(used_columns[:5])})"
    
    output_with_details = {
        "output": result["output"],
        "intermediate_steps": result.get("intermediate_steps", []),
        "source_info": f"데이터 출처: 업로드된 엑셀 파일{sheet_info}"
    }
    
    return output_with_details

def fallback_node(state: AgentState) -> dict:
    """분석 키워드가 없을 때 응답하는 폴백 노드입니다."""
    print("--- 폴백 노드 실행 ---")
    return {"output": "죄송합니다. 이해할 수 있는 분석 키워드를 찾지 못했어요. '사업부', '매출' 등의 키워드를 사용해 다시 질문해 주세요."}

def create_graph_workflow(agent_executor: AgentExecutor) -> StateGraph:
    """Phase 1 향상된 LangGraph 워크플로우를 생성하고 컴파일된 실행기를 반환합니다."""
    workflow = StateGraph(AgentState)

    # 노드들 추가
    workflow.add_node("router_node", router_node)
    workflow.add_node("context_aware_node", context_aware_node)
    workflow.add_node("intent_classification_node", intent_classification_node)
    workflow.add_node("query_planning_node", query_planning_node)
    workflow.add_node("agent_node", lambda state: agent_node(state, agent_executor))
    workflow.add_node("fallback_node", fallback_node)

    # Phase 1 워크플로우: Router → Context Aware → Intent Classification → Query Planning → 분기
    workflow.set_entry_point("router_node")
    workflow.add_edge("router_node", "context_aware_node")
    workflow.add_edge("context_aware_node", "intent_classification_node")
    workflow.add_edge("intent_classification_node", "query_planning_node")

    # Query Planning 결과에 따른 분기
    workflow.add_conditional_edges(
        "query_planning_node",
        enhanced_route_logic,
        {
            "agent_node": "agent_node", 
            "fallback_node": "fallback_node"
        }
    )
    
    workflow.add_edge("agent_node", END)
    workflow.add_edge("fallback_node", END)

    return workflow.compile()

# --- 4. 메인 실행 (Main Execution) ---

def main():
    """스크립트의 메인 실행 함수입니다."""
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
    # 툴 로드
    from agent.tool_registry import registered_tools

    # 1. 에이전트 실행기 생성
    agent_executor = create_agent_executor(openai_api_key, registered_tools)

    # 2. 그래프 워크플로우 생성
    app = create_graph_workflow(agent_executor)

# The code snippet you provided is a part of the main execution function in a Python script. Here's
# what it does:
    # # 3. 테스트 실행
    # print("\n--- [Test Case 1: 에이전트 경로] ---")
    # inputs_agent = {"input": "2023년 사업부별 매출 알려줘", "chat_history": []}
    # result_agent = app.invoke(inputs_agent)
    # print("\n[최종 결과]")
    # print(result_agent['output'])

    # print("\n\n--- [Test Case 2: 폴백 경로] ---")
    # inputs_fallback = {"input": "오늘 날씨 어때?", "chat_history": []}
    # result_fallback = app.invoke(inputs_fallback)
    # print("\n[최종 결과]")
    # print(result_fallback['output'])

# Create the graph executor for LangGraph Studio
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    from agent.tool_registry import registered_tools
    agent_executor = create_agent_executor(openai_api_key, registered_tools)
    graph_executor = create_graph_workflow(agent_executor)
else:
    print("Warning: OPENAI_API_KEY not found. Graph executor not initialized.")
    graph_executor = None

if __name__ == "__main__":
    main()