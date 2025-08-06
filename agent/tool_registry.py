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
]
