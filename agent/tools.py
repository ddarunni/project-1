import os
import pandas as pd
from langchain_core.tools import tool

# 전역 DataFrame 변수
_global_df = None

def set_dataframe(df: pd.DataFrame):
    """전역 DataFrame을 설정합니다."""
    global _global_df
    _global_df = df

def get_dataframe() -> pd.DataFrame:
    """전역 DataFrame을 반환합니다."""
    global _global_df
    if _global_df is None:
        raise ValueError("DataFrame이 설정되지 않았습니다. set_dataframe()을 먼저 호출하세요.")
    return _global_df

@tool
def get_sales_volume_by_division(division: str = None, year: int = None) -> str:
    """지정된 사업부와 연도 기준으로 매출수량(M/T)을 집계합니다."""
    df = get_dataframe()
    if division:
        df = df[df["Division"].str.contains(division, na=False)]
    if year:
        df = df[df["Period/Year"].astype(str).str.startswith(str(year))]
    total_volume = df["매출수량(M/T)"].sum()
    return f"{year}년 {division}의 총 매출 수량은 {total_volume:,.0f} 톤입니다."

@tool
def get_total_sales_volume_by_division(division: str) -> str:
    """특정 사업부(Division)에 대한 전체 매출수량(M/T)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{division}의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_total_sales_volume_by_fund(fund_center: str) -> str:
    """특정 펀드센터(Funds Center)에 대한 전체 매출수량(M/T)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["FundsCenter"].str.contains(fund_center, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{fund_center}의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_total_sales_volume_by_year(year: int) -> str:
    """특정 연도(Period/Year)의 전체 매출수량(M/T)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Period/Year"].astype(str).str.contains(str(year))]
    total = filtered["매출수량(M/T)"].sum()
    return f"{year}년 전체 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_operating_profit_by_division(division: str) -> str:
    """특정 사업부(Division)의 전체 영업이익(5.영업이익)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["5.영업이익"].sum()
    return f"{division}의 총 영업이익은 {total:,.0f}원입니다."

@tool
def get_operating_profit_by_year(year: int) -> str:
    """특정 연도(Period/Year)의 전체 영업이익(5.영업이익)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Period/Year"].astype(str).str.contains(str(year))]
    total = filtered["5.영업이익"].sum()
    return f"{year}년의 전체 영업이익은 {total:,.0f}원입니다."

@tool
def get_sales_amount_by_division(division: str) -> str:
    """특정 사업부(Division)의 전체 매출액(1.매출액)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["1.매출액"].sum()
    return f"{division}의 총 매출액은 {total:,.0f}원입니다."

@tool
def get_pre_tax_profit_by_division(division: str) -> str:
    """특정 사업부(Division)의 전체 세전이익(8.세전이익)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Division"].str.contains(division, na=False)]
    total = filtered["8.세전이익"].sum()
    return f"{division}의 총 세전이익은 {total:,.0f}원입니다."

@tool
def get_sales_volume_by_supplier(supplier: str) -> str:
    """특정 공급사(Supplier)의 전체 매출수량(M/T)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Supplier"].str.contains(supplier, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{supplier} 공급사의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_sales_volume_by_country(country: str) -> str:
    """특정 국가(Country)의 전체 매출수량(M/T)을 계산합니다."""
    df = get_dataframe()
    filtered = df[df["Country"].str.contains(country, na=False)]
    total = filtered["매출수량(M/T)"].sum()
    return f"{country}의 총 매출수량은 {total:,.0f} 톤입니다."

@tool
def get_overall_summary() -> str:
    """전체 데이터셋의 총 매출수량, 매출액, 영업이익을 요약하여 반환합니다."""
    df = get_dataframe()
    volume = df["매출수량(M/T)"].sum()
    sales = df["1.매출액"].sum()
    profit = df["5.영업이익"].sum()
    return f"총 매출수량: {volume:,.0f} 톤, 총 매출액: {sales:,.0f}원, 총 영업이익: {profit:,.0f}원입니다."

# === Phase 1: Advanced Multi-Column Tools ===

@tool
def advanced_multi_column_query(
    division: str = None,
    country: str = None, 
    year: str = None,
    period: str = None,
    supplier: str = None,
    funds_center: str = None,
    metric: str = "매출수량(M/T)"
) -> str:
    """복합 조건으로 데이터를 필터링하고 지정된 지표를 계산합니다.
    
    Args:
        division: 사업부/사업실 (예: "스테인리스", "전기강판")
        country: 국가 (예: "한국", "중국", "일본")
        year: 연도 (예: "2023", "2024") 
        period: 기간 (예: "상반기", "하반기", "1분기")
        supplier: 공급사 (예: "POSCO")
        funds_center: 펀드센터/그룹
        metric: 측정할 지표 (예: "매출수량(M/T)", "1.매출액", "5.영업이익")
    """
    df = get_dataframe()
    original_count = len(df)
    filters_applied = []
    
    # 조건별 필터링
    if division:
        df = df[df["Division"].str.contains(division, na=False, case=False)]
        filters_applied.append(f"사업부: {division}")
    
    if country:
        df = df[df["Country"].str.contains(country, na=False, case=False)]
        filters_applied.append(f"국가: {country}")
    
    if year:
        df = df[df["Period/Year"].astype(str).str.contains(str(year), na=False)]
        filters_applied.append(f"연도: {year}")
    
    if period:
        # 상반기, 하반기, 분기 등 처리
        if "상반기" in period:
            df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기", na=False)]
        elif "하반기" in period:
            df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기", na=False)]
        else:
            df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
        filters_applied.append(f"기간: {period}")
    
    if supplier:
        df = df[df["Supplier"].str.contains(supplier, na=False, case=False)]
        filters_applied.append(f"공급사: {supplier}")
    
    if funds_center:
        df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
        filters_applied.append(f"펀드센터: {funds_center}")
    
    # 결과 계산
    if len(df) == 0:
        return f"조건에 맞는 데이터가 없습니다. 적용된 필터: {', '.join(filters_applied)}"
    
    if metric in df.columns:
        total = df[metric].sum()
        filtered_count = len(df)
        
        # 단위 처리
        if metric == "매출수량(M/T)":
            unit = "톤"
        elif "매출액" in metric or "이익" in metric:
            unit = "원" 
        else:
            unit = ""
        
        result = f"{', '.join(filters_applied)} 조건의 {metric}: {total:,.0f}{unit}"
        result += f"\n(총 {filtered_count:,}개 레코드 중에서 집계, 전체 데이터의 {filtered_count/original_count:.1%})"
        
        return result
    else:
        return f"지표 '{metric}'를 찾을 수 없습니다. 사용 가능한 지표를 확인해주세요."

@tool
def comparative_analysis_tool(
    condition1_division: str = None,
    condition1_country: str = None,
    condition1_year: str = None,
    condition2_division: str = None, 
    condition2_country: str = None,
    condition2_year: str = None,
    metric: str = "매출수량(M/T)"
) -> str:
    """두 조건을 비교 분석합니다.
    
    예시: 2023년 한국 vs 2023년 중국 매출 비교
         스테인리스 vs 전기강판 영업이익 비교
    """
    df = get_dataframe()
    
    # 조건1 데이터 필터링
    df1 = df.copy()
    condition1_desc = []
    if condition1_division:
        df1 = df1[df1["Division"].str.contains(condition1_division, na=False, case=False)]
        condition1_desc.append(f"{condition1_division}")
    if condition1_country:
        df1 = df1[df1["Country"].str.contains(condition1_country, na=False, case=False)]
        condition1_desc.append(f"{condition1_country}")
    if condition1_year:
        df1 = df1[df1["Period/Year"].astype(str).str.contains(str(condition1_year), na=False)]
        condition1_desc.append(f"{condition1_year}년")
    
    # 조건2 데이터 필터링
    df2 = df.copy()
    condition2_desc = []
    if condition2_division:
        df2 = df2[df2["Division"].str.contains(condition2_division, na=False, case=False)]
        condition2_desc.append(f"{condition2_division}")
    if condition2_country:
        df2 = df2[df2["Country"].str.contains(condition2_country, na=False, case=False)]
        condition2_desc.append(f"{condition2_country}")
    if condition2_year:
        df2 = df2[df2["Period/Year"].astype(str).str.contains(str(condition2_year), na=False)]
        condition2_desc.append(f"{condition2_year}년")
    
    # 결과 계산
    if metric in df.columns:
        result1 = df1[metric].sum()
        result2 = df2[metric].sum()
        
        # 차이 계산
        diff = result1 - result2
        diff_pct = (diff / result2 * 100) if result2 != 0 else 0
        
        # 단위 설정
        if metric == "매출수량(M/T)":
            unit = "톤"
        elif "매출액" in metric or "이익" in metric:
            unit = "원"
        else:
            unit = ""
        
        condition1_name = " ".join(condition1_desc) if condition1_desc else "조건1"
        condition2_name = " ".join(condition2_desc) if condition2_desc else "조건2"
        
        result = f"📊 비교 분석 결과:\n"
        result += f"• {condition1_name}: {result1:,.0f}{unit}\n"
        result += f"• {condition2_name}: {result2:,.0f}{unit}\n"
        result += f"• 차이: {diff:,.0f}{unit} ({diff_pct:+.1f}%)\n"
        
        if diff > 0:
            result += f"→ {condition1_name}이 {condition2_name}보다 {abs(diff):,.0f}{unit} 많습니다."
        else:
            result += f"→ {condition2_name}이 {condition1_name}보다 {abs(diff):,.0f}{unit} 많습니다."
        
        return result
    else:
        return f"지표 '{metric}'를 찾을 수 없습니다."

@tool
def detect_relevant_columns(question: str) -> str:
    """질문에서 관련 컬럼들을 자동 감지하고 추천합니다."""
    df = get_dataframe()
    
    # 컬럼-키워드 매핑
    column_keywords = {
        "Division": ["사업실", "사업부", "부문", "division", "스테인리스", "전기강판", "열연", "냉연"],
        "Country": ["국가", "나라", "country", "한국", "중국", "일본", "미국", "국내", "해외"],
        "Period/Year": ["년", "년도", "분기", "상반기", "하반기", "2023", "2024", "2022"],
        "Supplier": ["공급사", "공급업체", "supplier", "posco", "포스코"],
        "FundsCenter": ["그룹", "센터", "funds", "펀드"],
        "매출수량(M/T)": ["매출수량", "판매량", "수량", "톤", "volume"],
        "1.매출액": ["매출액", "매출", "sales", "revenue"],
        "5.영업이익": ["영업이익", "이익", "profit", "operating"],
        "8.세전이익": ["세전이익", "세전", "pre-tax"]
    }
    
    detected_columns = []
    detected_metrics = []
    question_lower = question.lower()
    
    for column, keywords in column_keywords.items():
        matches = [kw for kw in keywords if kw in question_lower]
        if matches:
            if column in ["매출수량(M/T)", "1.매출액", "5.영업이익", "8.세전이익"]:
                detected_metrics.append(column)
            else:
                detected_columns.append(column)
    
    result = f"📋 질문 분석 결과:\n"
    
    if detected_columns:
        result += f"• 관련 필터 컬럼: {', '.join(detected_columns)}\n"
    
    if detected_metrics:
        result += f"• 분석 대상 지표: {', '.join(detected_metrics)}\n"
    else:
        result += f"• 분석 대상 지표: 매출수량(M/T) (기본값)\n"
    
    # 추천 도구
    if len(detected_columns) >= 2:
        result += f"• 추천 도구: advanced_multi_column_query 또는 comparative_analysis_tool\n"
    elif len(detected_columns) == 1:
        result += f"• 추천 도구: 기존 단일 컬럼 도구들\n"
    
    return result
