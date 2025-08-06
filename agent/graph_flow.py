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
ROUTING_KEYWORDS = ["사업실", "그룹", "판매량", "매출액", "영업이익", "공급사", "고객사", "국가"]

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

def route_logic(state: AgentState) -> str:
    """입력에 따라 다음에 실행할 노드를 결정하는 라우팅 로직입니다."""
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
    
    result = agent_executor.invoke({
        "input": state["input"],
        "chat_history": state["chat_history"]
    })
    return {"output": result["output"]}

def fallback_node(state: AgentState) -> dict:
    """분석 키워드가 없을 때 응답하는 폴백 노드입니다."""
    print("--- 폴백 노드 실행 ---")
    return {"output": "죄송합니다. 이해할 수 있는 분석 키워드를 찾지 못했어요. '사업부', '매출' 등의 키워드를 사용해 다시 질문해 주세요."}

def create_graph_workflow(agent_executor: AgentExecutor) -> StateGraph:
    """LangGraph 워크플로우를 생성하고 컴파일된 실행기를 반환합니다."""
    workflow = StateGraph(AgentState)

    # agent_node는 agent_executor를 인자로 받아야 하므로 functools.partial을 사용하거나
    # 람다 함수를 사용하여 필요한 인자를 넘겨줍니다.
    workflow.add_node("router_node", router_node)
    workflow.add_node("agent_node", lambda state: agent_node(state, agent_executor))
    workflow.add_node("fallback_node", fallback_node)

    workflow.set_entry_point("router_node")

    workflow.add_conditional_edges(
        "router_node",
        route_logic,
        {"agent_node": "agent_node", "fallback_node": "fallback_node"}
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