from langchain_core.tools import BaseTool
from langchain_core.tools import Tool
from agent.tools import (
    # Core tools that can't be replaced by smart_query_processor
    get_total_sales_volume_by_fund,
    get_total_sales_volume_by_year,
    get_overall_summary,
    # Phase 1: Advanced Multi-Column Tools
    comparative_analysis_tool,
    # Phase 1.1: Enhanced Tools
    smart_query_processor,
    # Phase 1.2: Data Exploration Tools
    get_unique_values,
    get_column_info,
    explore_dataset,
    # Phase 2: Multi-Dataset Tools
    compare_datasets_summary,
    compare_datasets_metrics,
    compare_datasets_by_division,
    integrated_dataset_analysis,
)

# ✅ LangGraph Studio, LangChain Agent, Streamlit 공통 등록용 (Consolidated)
registered_tools: list[BaseTool] = [
    # Core tools - can't be replaced by smart_query_processor
    get_total_sales_volume_by_fund,
    get_total_sales_volume_by_year, 
    get_overall_summary,
    # Enhanced tool - replaces most specific metric tools
    smart_query_processor,
]

registered_tools = [
    # === Core Tools (can't be replaced by smart_query_processor) ===
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
        func=get_overall_summary,
        name="get_overall_summary",
        description="전체 매출수량, 매출액, 영업이익을 요약합니다."
    ),
    # === Phase 1: Advanced Multi-Column Tools ===
    Tool.from_function(
        func=comparative_analysis_tool,
        name="comparative_analysis_tool", 
        description="두 조건을 비교 분석합니다. '한국 vs 중국', '스테인리스 vs 전기강판' 등의 비교 질문에 사용하세요."
    ),
    # === Phase 1.1: Enhanced Tools (Primary Tool) ===
    Tool.from_function(
        func=smart_query_processor,
        name="smart_query_processor",
        description="복합 질문을 자동으로 파싱하여 처리합니다. '열연수출1그룹의 상반기 영업이익', '스테인리스 사업실의 POSCO 공급 매출액' 등 복잡한 한국어 질문에 최적화. 매출수량, 매출액, 영업이익, 세전이익 등 모든 메트릭과 사업실/국가/공급사/기간 필터를 지원합니다."
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
    # === Phase 2: Multi-Dataset Tools ===
    Tool.from_function(
        func=compare_datasets_summary,
        name="compare_datasets_summary", 
        description="업로드된 다중 데이터셋의 기본 정보를 비교합니다. 파일 간 행/열 수, 데이터 규모 등을 비교할 때 사용하세요."
    ),
    Tool.from_function(
        func=compare_datasets_metrics,
        name="compare_datasets_metrics",
        description="다중 데이터셋 간 특정 지표(매출수량, 매출액, 영업이익 등)를 비교 분석합니다."
    ),
    Tool.from_function(
        func=compare_datasets_by_division,
        name="compare_datasets_by_division", 
        description="다중 데이터셋에서 사업실별 데이터를 비교 분석합니다. 사업실별 파일 간 차이를 볼 때 사용하세요."
    ),
    Tool.from_function(
        func=integrated_dataset_analysis,
        name="integrated_dataset_analysis",
        description="다중 데이터셋을 통합하여 종합적인 분석을 수행합니다. 전체 데이터셋의 통합 지표가 필요할 때 사용하세요."
    ),
]
