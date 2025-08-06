from langchain_core.runnables import RunnableLambda, RunnableMap
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

# ✅ .env 파일 로드 및 API 키 설정
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ LLM 정의 (기본: gpt-4o)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=openai_api_key
)

# ✅ 툴 레지스트리 불러오기
from agent.tool_registry import registered_tools

# ✅ 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 철강 데이터 분석 전문가야. 사용자 질문에 맞는 도구를 선택해서 정확한 수치를 포함한 한국어 답변을 해줘."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

# ✅ Agent 구성
agent = create_openai_functions_agent(
    llm=llm,
    tools=registered_tools,
    prompt=prompt
)

# ✅ LangGraph 실행기 형태로 래핑
agent_executor = AgentExecutor(
    agent=agent,
    tools=registered_tools,
    verbose=True
)
