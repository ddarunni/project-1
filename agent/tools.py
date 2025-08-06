from langchain_core.tools import tool

@tool
def get_sales_volume_by_division(params: dict) -> str:
    """지정된 사업부와 연도 기준으로 매출수량(M/T)을 집계합니다."""
    df = params["df"]
    division = params.get("division")
    year = params.get("year")
    if division:
        df = df[df["Division"].str.contains(division, na=False)]
    if year:
        df = df[df["Period/Year"].astype(str).str.startswith(str(year))]
    total_volume = df["매출수량(M/T)"].sum()
    return f"{year}년 {division}의 총 매출 수량은 {total_volume:,.0f} 톤입니다."

@tool
def get_total_sales_volume_by_division(params: dict) -> str:
    """특정 사업부(Division)에 대한 전체 매출수량(M/T)을 계산합니다."""
    df = params["df"]
    division = params["division"]
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{division}의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_total_sales_volume_by_fund(params: dict) -> str:
    """특정 펀드센터(Funds Center)에 대한 전체 매출수량(M/T)을 계산합니다."""
    df = params["df"]
    fund_center = params["fund_center"]
    filtered = df[df["FundsCenter"].str.contains(fund_center, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{fund_center}의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_total_sales_volume_by_year(params: dict) -> str:
    """특정 연도(Period/Year)의 전체 매출수량(M/T)을 계산합니다."""
    df = params["df"]
    year = params["year"]
    filtered = df[df["Period/Year"].astype(str).str.contains(str(year))]
    total = filtered["매출수량(M/T)"].sum()
    return f"{year}년 전체 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_operating_profit_by_division(params: dict) -> str:
    """특정 사업부(Division)의 전체 영업이익(5.영업이익)을 계산합니다."""
    df = params["df"]
    division = params["division"]
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["5.영업이익"].sum()
    return f"{division}의 총 영업이익은 {total:,.0f}원입니다."

@tool
def get_operating_profit_by_year(params: dict) -> str:
    """특정 연도(Period/Year)의 전체 영업이익(5.영업이익)을 계산합니다."""
    df = params["df"]
    year = params["year"]
    filtered = df[df["Period/Year"].astype(str).str.contains(str(year))]
    total = filtered["5.영업이익"].sum()
    return f"{year}년의 전체 영업이익은 {total:,.0f}원입니다."

@tool
def get_sales_amount_by_division(params: dict) -> str:
    """특정 사업부(Division)의 전체 매출액(1.매출액)을 계산합니다."""
    df = params["df"]
    division = params["division"]
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["1.매출액"].sum()
    return f"{division}의 총 매출액은 {total:,.0f}원입니다."

@tool
def get_pre_tax_profit_by_division(params: dict) -> str:
    """특정 사업부(Division)의 전체 세전이익(8.세전이익)을 계산합니다."""
    df = params["df"]
    division = params["division"]
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["8.세전이익"].sum()
    return f"{division}의 총 세전이익은 {total:,.0f}원입니다."

@tool
def get_sales_volume_by_supplier(params: dict) -> str:
    """특정 공급사(Supplier)의 전체 매출수량(M/T)을 계산합니다."""
    df = params["df"]
    supplier = params["supplier"]
    filtered = df[df["Supplier"].str.contains(supplier, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{supplier} 공급사의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_sales_volume_by_country(params: dict) -> str:
    """특정 국가(Country)의 전체 매출수량(M/T)을 계산합니다."""
    df = params["df"]
    country = params["country"]
    filtered = df[df["Country"].str.contains(country, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{country}의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_overall_summary(params: dict) -> str:
    """전체 데이터셋의 총 매출수량, 매출액, 영업이익을 요약하여 반환합니다."""
    df = params["df"]
    volume = df["매출수량(M/T)"].sum()
    sales = df["1.매출액"].sum()
    profit = df["5.영업이익"].sum()
    return f"총 매출수량: {volume:,.0f} 톤, 총 매출액: {sales:,.0f}원, 총 영업이익: {profit:,.0f}원입니다."
