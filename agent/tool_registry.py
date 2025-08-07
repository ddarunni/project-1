from langchain_core.tools import BaseTool
from langchain_core.tools import Tool
from agent.tools import (
    get_sales_volume_by_division,
    get_total_sales_volume_by_division,
    get_total_sales_volume_by_fund,
    get_total_sales_volume_by_year,
    get_operating_profit_by_division,
    get_operating_profit_by_year,
    get_sales_amount_by_division,
    get_pre_tax_profit_by_division,
    get_sales_volume_by_supplier,
    get_sales_volume_by_country,
    get_overall_summary,
    # Phase 1: Advanced Multi-Column Tools
    advanced_multi_column_query,
    comparative_analysis_tool,
    detect_relevant_columns,
)

# ✅ LangGraph Studio, LangChain Agent, Streamlit 공통 등록용
registered_tools: list[BaseTool] = [
    get_sales_volume_by_division,
    get_total_sales_volume_by_division,
    get_total_sales_volume_by_fund,
    get_total_sales_volume_by_year,
    get_operating_profit_by_division,
    get_operating_profit_by_year,
    get_sales_amount_by_division,
    get_pre_tax_profit_by_division,
    get_sales_volume_by_supplier,
    get_sales_volume_by_country,
    get_overall_summary,
]

registered_tools = [
    Tool.from_function(
        func=get_sales_volume_by_division,
        name="get_sales_volume_by_division",
        description="지정된 사업부와 연도 기준으로 매출수량(M/T)을 집계합니다."
    ),
    Tool.from_function(
        func=get_total_sales_volume_by_division,
        name="get_total_sales_volume_by_division",
        description="특정 사업부의 전체 매출수량(M/T)을 계산합니다."
    ),
    Tool.from_function(
        func=get_total_sales_volume_by_fund,
        name="get_total_sales_volume_by_fund",
        description="특정 Funds Center의 전체 매출수량(M/T)을 계산합니다."
    ),
    Tool.from_function(
        func=get_total_sales_volume_by_year,
        name="get_total_sales_volume_by_year",
        description="특정 연도의 전체 매출수량(M/T)을 계산합니다."
    ),
    Tool.from_function(
        func=get_operating_profit_by_division,
        name="get_operating_profit_by_division",
        description="특정 사업부의 전체 영업이익을 계산합니다."
    ),
    Tool.from_function(
        func=get_operating_profit_by_year,
        name="get_operating_profit_by_year",
        description="특정 연도의 전체 영업이익을 계산합니다."
    ),
    Tool.from_function(
        func=get_sales_amount_by_division,
        name="get_sales_amount_by_division",
        description="특정 사업부의 전체 매출액을 계산합니다."
    ),
    Tool.from_function(
        func=get_pre_tax_profit_by_division,
        name="get_pre_tax_profit_by_division",
        description="특정 사업부의 전체 세전이익을 계산합니다."
    ),
    Tool.from_function(
        func=get_sales_volume_by_supplier,
        name="get_sales_volume_by_supplier",
        description="특정 공급사의 전체 매출수량을 계산합니다."
    ),
    Tool.from_function(
        func=get_sales_volume_by_country,
        name="get_sales_volume_by_country",
        description="특정 국가의 전체 매출수량을 계산합니다."
    ),
    Tool.from_function(
        func=get_overall_summary,
        name="get_overall_summary",
        description="전체 매출수량, 매출액, 영업이익을 요약합니다."
    ),
    # === Phase 1: Advanced Multi-Column Tools ===
    Tool.from_function(
        func=advanced_multi_column_query,
        name="advanced_multi_column_query",
        description="복합 조건(사업부+국가+연도 등)으로 데이터를 필터링하고 지정된 지표를 계산합니다. 여러 조건이 조합된 복잡한 질문에 사용하세요."
    ),
    Tool.from_function(
        func=comparative_analysis_tool,
        name="comparative_analysis_tool", 
        description="두 조건을 비교 분석합니다. '한국 vs 중국', '스테인리스 vs 전기강판' 등의 비교 질문에 사용하세요."
    ),
    Tool.from_function(
        func=detect_relevant_columns,
        name="detect_relevant_columns",
        description="질문에서 관련 컬럼들을 자동 감지하고 추천합니다. 복잡한 질문 분석 시 먼저 사용하세요."
    ),
]
