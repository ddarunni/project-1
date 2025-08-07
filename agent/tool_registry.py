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
    # Phase 1.1: Enhanced Tools
    smart_query_processor,
    extract_complex_entities,
    # Phase 1.2: Data Exploration Tools
    get_unique_values,
    get_column_info,
    explore_dataset,
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
    # === Phase 1.1: Enhanced Tools ===
    Tool.from_function(
        func=smart_query_processor,
        name="smart_query_processor",
        description="복합 질문을 자동으로 파싱하여 처리합니다. '열연수출1그룹의 상반기 영업이익'과 같은 복잡한 한국어 질문에 최적화되어 있습니다."
    ),
    Tool.from_function(
        func=extract_complex_entities,
        name="extract_complex_entities", 
        description="질문에서 그룹명, 기간, 메트릭 등을 정교하게 추출합니다. 복잡한 질문 분석용 헬퍼 도구입니다."
    ),
    # === Phase 1.2: Data Exploration Tools ===
    Tool.from_function(
        func=get_unique_values,
        name="get_unique_values",
        description="지정된 컬럼의 모든 고유값들을 나열합니다. '모든 그룹명', '가능한 국가 목록' 등의 질문에 사용하세요. FundsCenter 컬럼명을 사용하여 모든 그룹을 조회할 수 있습니다."
    ),
    Tool.from_function(
        func=get_column_info,
        name="get_column_info",
        description="특정 컬럼의 상세 정보와 통계를 제공합니다. 데이터 분포, 최빈값, 통계 정보가 필요할 때 사용하세요."
    ),
    Tool.from_function(
        func=explore_dataset,
        name="explore_dataset",
        description="전체 데이터셋의 구조와 모든 컬럼 정보를 제공합니다. 데이터셋 개요나 사용 가능한 컬럼을 알고 싶을 때 사용하세요."
    ),
]
