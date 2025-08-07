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

# DEPRECATED: get_sales_volume_by_division - replaced by smart_query_processor
# Use smart_query_processor for questions like "2023년 스테인리스의 매출수량"

# DEPRECATED: get_total_sales_volume_by_division - replaced by smart_query_processor for specific divisions
# For "전체" queries, use get_overall_summary() instead
# For specific divisions, use smart_query_processor("스테인리스의 매출수량")

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

# DEPRECATED: get_operating_profit_by_division - replaced by smart_query_processor
# Use smart_query_processor for questions like "스테인리스의 영업이익"

# @tool
# def get_operating_profit_by_year(year: int) -> str:
#     """특정 연도(Period/Year)의 전체 영업이익(5.영업이익)을 계산합니다."""
#     df = get_dataframe()
#     filtered = df[df["Period/Year"].astype(str).str.contains(str(year))]
#     total = filtered["5.영업이익"].sum()
#     return f"{year}년의 전체 영업이익은 {total:,.0f}원입니다."

# DEPRECATED: get_sales_amount_by_division - replaced by smart_query_processor
# Use smart_query_processor for questions like "스테인리스의 매출액"

# DEPRECATED: get_pre_tax_profit_by_division - replaced by smart_query_processor
# Use smart_query_processor for questions like "스테인리스의 세전이익"

# DEPRECATED: get_sales_volume_by_supplier - replaced by smart_query_processor
# Use smart_query_processor for questions like "POSCO 공급사의 매출수량"

# DEPRECATED: get_sales_volume_by_country - replaced by smart_query_processor
# Use smart_query_processor for questions like "한국의 매출수량"

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
def smart_query_processor(question: str) -> str:
    """복합 질문을 자동으로 파싱하고 advanced_multi_column_query를 실행합니다."""
    # 1. 엔티티 추출
    entities = _extract_complex_entities(question)
    
    # 2. 추출된 정보로 advanced_multi_column_query 호출
    result = _advanced_multi_column_query(
        division=entities.get('division'),
        country=entities.get('country'),
        year=entities.get('year'),
        period=entities.get('period'),
        supplier=entities.get('supplier'),
        funds_center=entities.get('funds_center'),
        metric=entities.get('metric', '매출수량(M/T)')
    )
    
    # 3. 추출 정보 포함하여 결과 반환
    extraction_info = f"📋 추출된 정보:\n"
    for key, value in entities.items():
        if value:
            extraction_info += f"• {key}: {value}\n"
    
    return f"{extraction_info}\n{result}"

def _advanced_multi_column_query(
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
        period: 기간 (예: "2022년", "상반기", "하반기", "1분기")
        supplier: 공급사 (예: "POSCO")
        funds_center: 그룹 (예: "열연수출1그룹", "냉연내수2그룹")
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
        # 강화된 연도 매칭 - 파싱 기능 사용
        year_matched_rows = []
        for idx, row in df.iterrows():
            parsed_info = _parse_period_year(row['Period/Year'])
            if 'year' in parsed_info and str(parsed_info['year']) == str(year):
                year_matched_rows.append(idx)
        
        if year_matched_rows:
            df = df.loc[year_matched_rows]
            filters_applied.append(f"연도: {year} (스마트매칭, {len(year_matched_rows)}개 레코드)")
        else:
            # Fallback: 기존 패턴 매칭
            df = df[df["Period/Year"].astype(str).str.contains(str(year), na=False)]
            filters_applied.append(f"연도: {year} (패턴매칭)")
    
    if period:
        # 강화된 Period 매칭 - 새로운 파싱 기능 사용
        if 'Period/Year' in df.columns:
            # 연도 컨텍스트 추론
            period_with_year = _infer_year_context(period)
            unique_periods = df['Period/Year'].dropna().astype(str).unique().tolist()
            
            # 먼저 직접 매칭 시도
            best_match, confidence = _find_best_match(period_with_year, unique_periods)
            
            if best_match and confidence >= 0.8:
                df = df[df["Period/Year"].astype(str) == best_match]
                match_info = f"연도추론" if period != period_with_year else "직접매칭"
                filters_applied.append(f"기간: {period} → {best_match} (신뢰도: {confidence:.2f}, {match_info})")
            else:
                # 새로운 스마트 매칭: 파싱된 정보로 필터링
                matched_rows = []
                for idx, row in df.iterrows():
                    parsed_info = _parse_period_year(row['Period/Year'])
                    
                    # AND 조건: 연도와 기간 둘 다 만족해야 함
                    year_match = True
                    period_match = True
                    
                    # 연도 조건 검사
                    if year:
                        if 'year' not in parsed_info or str(year) != str(parsed_info['year']):
                            year_match = False
                    
                    # 기간 조건 검사
                    if "상반기" in period:
                        if parsed_info.get('half_year') != '상반기':
                            period_match = False
                    elif "하반기" in period:
                        if parsed_info.get('half_year') != '하반기':
                            period_match = False
                    elif re.search(r'(\d)분기', period):
                        quarter_match = re.search(r'(\d)분기', period)
                        if quarter_match and parsed_info.get('quarter') != f"{quarter_match.group(1)}분기":
                            period_match = False
                    # 월 범위 조건 처리
                    elif re.search(r'(\d+)월부터\s*(\d+)월|(\d+)월-(\d+)월', period):
                        # 월 범위 추출
                        range_match = re.search(r'(\d+)월부터\s*(\d+)월', period) or re.search(r'(\d+)월-(\d+)월', period)
                        if range_match:
                            start_month = int(range_match.group(1))
                            end_month = int(range_match.group(2))
                            # 데이터의 월이 범위 안에 있는지 확인
                            data_month = parsed_info.get('month_number')
                            if data_month is None or not (start_month <= data_month <= end_month):
                                period_match = False
                    
                    # 둘 다 만족하는 경우만 추가
                    if year_match and period_match:
                        matched_rows.append(idx)
                
                if matched_rows:
                    df = df.loc[matched_rows]
                    filters_applied.append(f"기간: {period} (스마트매칭, {len(matched_rows)}개 레코드)")
                else:
                    # Fallback: 기존 패턴 매칭
                    print(f"스마트매칭 실패, Fallback 사용. 기간: {period}")
                    if "상반기" in period:
                        df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기|January|February|March|April|May|June", na=False)]
                        filters_applied.append(f"기간: {period} (Fallback-상반기, {len(df)}개 레코드)")
                    elif "하반기" in period:
                        df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기|July|August|September|October|November|December", na=False)]
                        filters_applied.append(f"기간: {period} (Fallback-하반기, {len(df)}개 레코드)")
                    elif re.search(r'(\d+)월부터\s*(\d+)월|(\d+)월-(\d+)월', period):
                        # 월 범위 Fallback
                        range_match = re.search(r'(\d+)월부터\s*(\d+)월', period) or re.search(r'(\d+)월-(\d+)월', period)
                        if range_match:
                            start_month = int(range_match.group(1))
                            end_month = int(range_match.group(2))
                            # 영어 월명과 한글 월명 모두 지원
                            month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                                          'July', 'August', 'September', 'October', 'November', 'December']
                            target_months = month_names[start_month-1:end_month]
                            korean_months = [f"{i}월" for i in range(start_month, end_month+1)]
                            pattern = '|'.join(target_months + korean_months)
                            df = df[df["Period/Year"].astype(str).str.contains(pattern, na=False)]
                            filters_applied.append(f"기간: {period} (Fallback-월범위, {len(df)}개 레코드)")
                    else:
                        df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
                        available_periods = ", ".join(unique_periods[:3])
                        filters_applied.append(f"기간: {period} (패턴매칭, 사용가능: {available_periods}...)")
        else:
            filters_applied.append(f"기간: {period} (Period/Year 컬럼 없음)")
    
    if supplier:
        df = df[df["Supplier"].str.contains(supplier, na=False, case=False)]
        filters_applied.append(f"공급사: {supplier}")
    
    if funds_center:
        # 강화된 FundsCenter 매칭
        if 'FundsCenter' in df.columns:
            unique_funds = df['FundsCenter'].dropna().unique().tolist()
            best_match, confidence = _find_best_match(funds_center, unique_funds)
            
            if best_match and confidence >= 0.7:
                df = df[df["FundsCenter"] == best_match]
                match_type = "정확매칭" if confidence == 1.0 else "유사매칭"
                filters_applied.append(f"펀드센터: {funds_center} → {best_match} (신뢰도: {confidence:.2f}, {match_type})")
            else:
                # 매칭 실패시 사용 가능한 옵션 제안
                df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
                available_options = ", ".join(unique_funds[:5])
                filters_applied.append(f"펀드센터: {funds_center} (매칭실패, 사용가능: {available_options}...)")
        else:
            filters_applied.append(f"펀드센터: {funds_center} (FundsCenter 컬럼 없음)")
    
    # 결과 계산
    if len(df) == 0:
        return f"조건에 맞는 데이터가 없습니다. 적용된 필터: {', '.join(filters_applied)}"
    
    if metric in df.columns:
        total = df[metric].sum()
        filtered_count = len(df)
        
        # 단위 처리 및 값 변환
        if metric == "매출수량(M/T)":
            unit = "톤"
            display_value = f"{total:,.0f}{unit}"
        elif "매출액" in metric or "이익" in metric:
            # 원 단위 데이터를 억원 단위로 변환
            billion_value = total / 100000000  # 1억 = 100,000,000
            if billion_value >= 1:
                display_value = f"{billion_value:,.0f}억원"
            else:
                display_value = f"{total:,.0f}원"
        else:
            display_value = f"{total:,.0f}"
        
        result = f"{', '.join(filters_applied)} 조건의 {metric}: {display_value}"
        result += f"\n(총 {filtered_count:,}개 레코드 중에서 집계, 전체 데이터의 {filtered_count/original_count:.1%})"
        
        return result
    else:
        return f"지표 '{metric}'를 찾을 수 없습니다. 사용 가능한 지표를 확인해주세요."

# DEPRECATED: advanced_multi_column_query 제거됨
# smart_query_processor 사용 권장

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
            unit = "억원"
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

import re
from datetime import datetime
from difflib import SequenceMatcher

def _normalize_korean_text(text: str) -> str:
    """한국어 텍스트를 정규화합니다."""
    if not text:
        return ""
    
    text = str(text).strip()
    
    # 숫자 위치 정규화: "그룹1" <-> "1그룹"
    # "열연수출그룹1" -> "열연수출1그룹" 형태로 통일
    text = re.sub(r'([가-힣]+)그룹(\d+)', r'\1\2그룹', text)
    
    # 공백 제거
    text = re.sub(r'\s+', '', text)
    
    return text

def _find_best_match(target: str, candidates: list, min_similarity: float = 0.7) -> tuple:
    """최적 매칭을 찾습니다. (매칭값, 신뢰도) 반환"""
    if not target or not candidates:
        return None, 0.0
    
    target_normalized = _normalize_korean_text(target)
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        candidate_str = str(candidate)
        candidate_normalized = _normalize_korean_text(candidate_str)
        
        # 1. 정확 매칭 (정규화 후)
        if target_normalized == candidate_normalized:
            return candidate_str, 1.0
        
        # 2. 부분 매칭 (양방향)
        if target_normalized in candidate_normalized or candidate_normalized in target_normalized:
            score = 0.9
            if score > best_score:
                best_match = candidate_str
                best_score = score
        
        # 3. 유사도 매칭
        similarity = SequenceMatcher(None, target_normalized, candidate_normalized).ratio()
        if similarity > best_score and similarity >= min_similarity:
            best_match = candidate_str
            best_score = similarity
        
        # 4. 키워드 매칭 (그룹명 특화)
        if '그룹' in target_normalized and '그룹' in candidate_normalized:
            # 핵심 키워드 추출 ("열연수출" 등)
            target_base = re.sub(r'\d*그룹.*', '', target_normalized)
            candidate_base = re.sub(r'\d*그룹.*', '', candidate_normalized)
            
            if target_base and candidate_base and target_base in candidate_base:
                score = 0.8
                if score > best_score:
                    best_match = candidate_str
                    best_score = score
    
    return best_match, best_score

def _infer_year_context(period: str) -> str:
    """기간에서 연도 컨텍스트를 추론합니다."""
    if not period:
        return period
    
    # 이미 연도가 포함된 경우
    if re.search(r'20\d{2}', period):
        return period
    
    # 현재 연도 추가
    current_year = datetime.now().year
    
    if '상반기' in period:
        return f"{current_year}년상반기"
    elif '하반기' in period:
        return f"{current_year}년하반기"
    elif re.search(r'\d+분기', period):
        return f"{current_year}년{period}"
    
    return period

def _parse_period_year(period_value: str) -> dict:
    """Period/Year 컬럼의 다양한 형식을 파싱합니다.
    
    지원 형식:
    - '2023.001 January 2023'
    - '2023년 1월'
    - '2023년 상반기'
    - '2023 Q1'
    """
    if not period_value or pd.isna(period_value):
        return {}
    
    period_str = str(period_value).strip()
    parsed_info = {}
    
    # 패턴 1: "2023.001 January 2023" 형식
    match = re.match(r'(\d{4})\.(\d{3})\s+(\w+)\s+(\d{4})', period_str)
    if match:
        year = match.group(1)
        period_code = match.group(2)
        month_name = match.group(3)
        year2 = match.group(4)
        
        parsed_info.update({
            'year': year,
            'period_code': period_code,
            'month_name': month_name,
            'month_number': _month_name_to_number(month_name),
            'quarter': _month_to_quarter(_month_name_to_number(month_name)),
            'half_year': '상반기' if _month_name_to_number(month_name) <= 6 else '하반기'
        })
        return parsed_info
    
    # 패턴 2: "2023년 1월" 형식
    match = re.match(r'(\d{4})년\s*(\d{1,2})월', period_str)
    if match:
        year = match.group(1)
        month = int(match.group(2))
        
        parsed_info.update({
            'year': year,
            'month_number': month,
            'quarter': _month_to_quarter(month),
            'half_year': '상반기' if month <= 6 else '하반기'
        })
        return parsed_info
    
    # 패턴 3: "2023년 상반기/하반기" 형식
    match = re.match(r'(\d{4})년\s*(상반기|하반기)', period_str)
    if match:
        year = match.group(1)
        half = match.group(2)
        
        parsed_info.update({
            'year': year,
            'half_year': half
        })
        return parsed_info
    
    # 패턴 4: 연도만 추출
    year_match = re.search(r'(\d{4})', period_str)
    if year_match:
        parsed_info['year'] = year_match.group(1)
    
    return parsed_info

def _month_name_to_number(month_name: str) -> int:
    """영문 월명을 숫자로 변환"""
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return month_mapping.get(month_name, 0)

def _month_to_quarter(month: int) -> str:
    """월을 분기로 변환"""
    if month in [1, 2, 3]:
        return '1분기'
    elif month in [4, 5, 6]:
        return '2분기'
    elif month in [7, 8, 9]:
        return '3분기'
    elif month in [10, 11, 12]:
        return '4분기'
    return ''

def _extract_complex_entities(question: str) -> dict:
    """복합 질문에서 엔티티를 정교하게 추출합니다."""
    entities = {
        'funds_center': None,
        'division': None,
        'country': None,
        'period': None,
        'year': None,
        'supplier': None,
        'metric': None
    }
    
    # 그룹명 패턴 (숫자 포함)
    group_patterns = [
        r'([가-힣]+(?:수출|내수)?\d*그룹)',  # 열연수출1그룹, 냉연내수2그룹
        r'([가-힣]+\d+그룹)',              # 스테인리스1그룹
        r'(\w+그룹\d*)',                    # 영문그룹
    ]
    
    for pattern in group_patterns:
        match = re.search(pattern, question)
        if match:
            entities['funds_center'] = match.group(1)
            break
    
    # 사업부/Division 패턴
    division_patterns = ['스테인리스', '모빌리티', '열연조강', '냉연', '후판선재', '스테인레스', '에너지인프라강재', '자동차소재']
    for div in division_patterns:
        if div in question:
            entities['division'] = div
            break
    
    # 기간 패턴 - 월 범위 조건 추가
    if '상반기' in question:
        entities['period'] = '상반기'
    elif '하반기' in question:
        entities['period'] = '하반기'
    elif re.search(r'(\d+)분기', question):
        quarter_match = re.search(r'(\d+)분기', question)
        entities['period'] = f"{quarter_match.group(1)}분기"
    # 월 범위 패턴: "7월부터 12월", "1월-6월" 등
    elif re.search(r'(\d+)월부터\s*(\d+)월', question):
        month_range_match = re.search(r'(\d+)월부터\s*(\d+)월', question)
        start_month = int(month_range_match.group(1))
        end_month = int(month_range_match.group(2))
        entities['period'] = f"{start_month}월부터{end_month}월"
        entities['month_range'] = (start_month, end_month)
    elif re.search(r'(\d+)월-(\d+)월', question):
        month_range_match = re.search(r'(\d+)월-(\d+)월', question)
        start_month = int(month_range_match.group(1))
        end_month = int(month_range_match.group(2))
        entities['period'] = f"{start_month}월-{end_month}월"
        entities['month_range'] = (start_month, end_month)
    
    # 연도 패턴
    year_match = re.search(r'(20\d{2})', question)
    if year_match:
        entities['year'] = year_match.group(1)
    
    
    # 국가 패턴
    countries = ['한국', '중국', '일본', '미국', '독일', '인도', '베트남', '태국' ]
    for country in countries:
        if country in question:
            entities['country'] = country
            break
    
    # 메트릭 패턴
    if '영업이익' in question:
        entities['metric'] = '5.영업이익'
    elif '매출액' in question:
        entities['metric'] = '1.매출액'
    elif '세전이익' in question:
        entities['metric'] = '8.세전이익'
    elif '매출수량' in question or '판매량' in question or '수량' in question:
        entities['metric'] = '매출수량(M/T)'
    else:
        entities['metric'] = '매출수량(M/T)'  # 기본값
    
    return entities

# extract_complex_entities removed - now integrated into smart_query_processor

# detect_relevant_columns simplified - most functionality now in smart_query_processor
# Keeping only basic column detection for backward compatibility

# === Phase 1.2: Data Exploration Tools ===

@tool
def get_unique_values(column_name: str, limit: int = 50) -> str:
    """지정된 컬럼의 고유값들을 반환합니다."""
    df = get_dataframe()
    
    if column_name not in df.columns:
        available_columns = ", ".join(df.columns[:10])
        return f"❌ '{column_name}' 컬럼을 찾을 수 없습니다.\n사용 가능한 컬럼: {available_columns}..."
    
    unique_values = df[column_name].dropna().unique()
    total_count = len(unique_values)
    
    # 결과 정렬 (가능한 경우)
    try:
        unique_values = sorted(unique_values)
    except:
        pass  # 정렬 불가능한 타입인 경우 원본 순서 유지
    
    # limit 적용
    display_values = unique_values[:limit]
    
    result = f"📋 {column_name} 컬럼의 고유값 목록:\n"
    result += f"📊 총 {total_count}개의 고유값\n\n"
    
    for i, value in enumerate(display_values, 1):
        result += f"{i:2d}. {value}\n"
    
    if total_count > limit:
        result += f"\n... 및 {total_count - limit}개 추가 값"
    
    return result

@tool
def get_column_info(column_name: str) -> str:
    """지정된 컬럼의 상세 정보를 반환합니다."""
    df = get_dataframe()
    
    if column_name not in df.columns:
        available_columns = ", ".join(df.columns[:10])
        return f"❌ '{column_name}' 컬럼을 찾을 수 없습니다.\n사용 가능한 컬럼: {available_columns}..."
    
    column_data = df[column_name]
    
    result = f"📊 {column_name} 컬럼 정보:\n"
    result += f"• 데이터 타입: {column_data.dtype}\n"
    result += f"• 총 행 수: {len(column_data):,}\n"
    result += f"• 결측값: {column_data.isnull().sum():,}개\n"
    result += f"• 고유값 수: {column_data.nunique():,}개\n"
    
    # 데이터 타입별 상세 정보
    if column_data.dtype in ['object', 'string']:
        result += f"\n📝 텍스트 컬럼 상세:\n"
        
        # 가장 많이 나타나는 상위 10개 값
        top_values = column_data.value_counts().head(10)
        result += f"• 최빈값 TOP 10:\n"
        for idx, (value, count) in enumerate(top_values.items(), 1):
            percentage = (count / len(column_data)) * 100
            result += f"  {idx:2d}. {value} ({count:,}개, {percentage:.1f}%)\n"
            
    elif column_data.dtype in ['int64', 'float64']:
        result += f"\n📈 숫자 컬럼 상세:\n"
        result += f"• 최솟값: {column_data.min():,.0f}\n"
        result += f"• 최댓값: {column_data.max():,.0f}\n"
        result += f"• 평균값: {column_data.mean():,.0f}\n"
        result += f"• 중앙값: {column_data.median():,.0f}\n"
    
    return result

@tool
def explore_dataset() -> str:
    """데이터셋의 전체 구조와 기본 정보를 제공합니다."""
    df = get_dataframe()
    
    result = f"📊 데이터셋 전체 개요:\n"
    result += f"• 총 행 수: {len(df):,}\n"
    result += f"• 총 컬럼 수: {len(df.columns)}\n"
    result += f"• 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB\n\n"
    
    result += f"📋 컬럼 목록 및 기본 정보:\n"
    for i, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        
        result += f"{i:2d}. {col}\n"
        result += f"    - 타입: {dtype}\n"
        result += f"    - 고유값: {unique_count:,}개\n"
        result += f"    - 결측값: {null_count:,}개\n"
        
        # 샘플 값 표시 (텍스트 컬럼의 경우)
        if dtype == 'object' and unique_count <= 20:
            sample_values = df[col].dropna().unique()[:5]
            sample_str = ", ".join([str(v) for v in sample_values])
            if len(sample_str) > 50:
                sample_str = sample_str[:47] + "..."
            result += f"    - 샘플: {sample_str}\n"
        result += "\n"
    
    return result

@tool
def test_period_recognition(sample_limit: int = 10) -> str:
    """Period/Year 컬럼의 인식 능력을 테스트합니다."""
    df = get_dataframe()
    
    if 'Period/Year' not in df.columns:
        return "❌ Period/Year 컬럼이 없습니다."
    
    result = f"🧪 Period/Year 인식 테스트:\n\n"
    
    # 샘플 데이터 분석
    sample_periods = df['Period/Year'].dropna().unique()[:sample_limit]
    
    for period_value in sample_periods:
        parsed = _parse_period_year(period_value)
        
        result += f"원본: '{period_value}'\n"
        if parsed:
            result += f"  ✅ 파싱 성공:\n"
            for key, value in parsed.items():
                result += f"     • {key}: {value}\n"
        else:
            result += f"  ❌ 파싱 실패\n"
        result += "\n"
    
    return result
import pandas as pd
from langchain_core.tools import tool

# 전역 변수로 여러 데이터셋 관리
_global_datasets = {}

def set_datasets(datasets_dict: dict):
    """여러 데이터셋을 설정합니다."""
    global _global_datasets
    _global_datasets = datasets_dict

def get_datasets() -> dict:
    """모든 데이터셋을 반환합니다."""
    global _global_datasets
    return _global_datasets

@tool
def compare_datasets_summary() -> str:
    """업로드된 모든 데이터셋의 기본 정보를 비교합니다."""
    datasets = get_datasets()
    
    if len(datasets) < 2:
        return "❌ 비교하려면 최소 2개의 데이터셋이 필요합니다."
    
    result = "📊 데이터셋 기본 정보 비교:\n\n"
    
    for name, df in datasets.items():
        result += f"🗂️ **{name}**\n"
        result += f"  • 행 수: {len(df):,}개\n"
        result += f"  • 열 수: {len(df.columns)}개\n"
        result += f"  • 메모리: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB\n"
        result += f"  • 결측값: {df.isnull().sum().sum():,}개\n"
        
        # 주요 수치형 컬럼 요약
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            result += f"  • 수치형 컬럼: {len(numeric_cols)}개\n"
        result += "\n"
    
    return result

@tool  
def compare_datasets_metrics(metric: str = "매출수량(M/T)") -> str:
    """여러 데이터셋 간의 특정 지표를 비교합니다."""
    datasets = get_datasets()
    
    if len(datasets) < 2:
        return "❌ 비교하려면 최소 2개의 데이터셋이 필요합니다."
    
    result = f"📈 {metric} 비교 분석:\n\n"
    metric_results = {}
    
    for name, df in datasets.items():
        if metric in df.columns:
            total = df[metric].sum()
            mean = df[metric].mean()
            count = len(df[df[metric].notna()])
            
            metric_results[name] = {
                'total': total,
                'mean': mean, 
                'count': count
            }
            
            # 단위 처리
            if metric == "매출수량(M/T)":
                unit = "톤"
            elif "매출액" in metric or "이익" in metric:
                unit = "억원"
            else:
                unit = ""
            
            result += f"🗂️ **{name}**\n"
            result += f"  • 총합: {total:,.0f}{unit}\n"
            result += f"  • 평균: {mean:,.0f}{unit}\n"
            result += f"  • 레코드 수: {count:,}개\n\n"
        else:
            result += f"🗂️ **{name}**: ❌ '{metric}' 컬럼 없음\n\n"
    
    # 순위 및 차이 분석
    if len(metric_results) >= 2:
        sorted_results = sorted(metric_results.items(), key=lambda x: x[1]['total'], reverse=True)
        
        result += "🏆 **순위 및 차이 분석:**\n"
        for i, (name, data) in enumerate(sorted_results, 1):
            unit = "톤" if metric == "매출수량(M/T)" else "억원" if "매출액" in metric or "이익" in metric else ""
            result += f"  {i}. {name}: {data['total']:,.0f}{unit}\n"
        
        if len(sorted_results) >= 2:
            top_name, top_data = sorted_results[0]
            second_name, second_data = sorted_results[1]
            diff = top_data['total'] - second_data['total']
            diff_pct = (diff / second_data['total'] * 100) if second_data['total'] != 0 else 0
            
            result += f"\n📊 **{top_name}**이 **{second_name}**보다 {diff:,.0f}{unit} 많음 (+{diff_pct:.1f}%)\n"
    
    return result

@tool
def compare_datasets_by_division(division: str = None) -> str:
    """여러 데이터셋에서 특정 사업부별 데이터를 비교합니다."""
    datasets = get_datasets()
    
    if len(datasets) < 2:
        return "❌ 비교하려면 최소 2개의 데이터셋이 필요합니다."
    
    result = f"🏢 사업부별 비교 분석"
    if division:
        result += f" - {division}"
    result += ":\n\n"
    
    for name, df in datasets.items():
        filtered_df = df
        
        if division and 'Division' in df.columns:
            filtered_df = df[df["Division"].str.contains(division, na=False, case=False)]
        
        result += f"🗂️ **{name}**\n"
        
        if 'Division' in df.columns:
            if division:
                result += f"  📋 {division} 관련 데이터:\n"
            else:
                result += f"  📋 전체 사업부 현황:\n"
            
            # 매출수량 집계
            if "매출수량(M/T)" in filtered_df.columns:
                volume = filtered_df["매출수량(M/T)"].sum()
                result += f"    • 매출수량: {volume:,.0f} 톤\n"
            
            # 매출액 집계  
            if "1.매출액" in filtered_df.columns:
                sales = filtered_df["1.매출액"].sum()
                result += f"    • 매출액: {sales:,.0f} 억원\n"
            
            # 영업이익 집계
            if "5.영업이익" in filtered_df.columns:
                profit = filtered_df["5.영업이익"].sum()
                result += f"    • 영업이익: {profit:,.0f} 억원\n"
            
            result += f"    • 레코드 수: {len(filtered_df):,}개\n"
            
            # 사업부별 상세 (전체 조회시)
            if not division and "매출수량(M/T)" in filtered_df.columns:
                division_summary = filtered_df.groupby('Division')['매출수량(M/T)'].sum().reset_index()
                division_summary = division_summary.sort_values('매출수량(M/T)', ascending=False)
                
                if len(division_summary) > 0:
                    result += f"    📊 상위 3개 사업부:\n"
                    for idx, row in division_summary.head(3).iterrows():
                        result += f"      {idx+1}. {row['Division']}: {row['매출수량(M/T)']:,.0f} 톤\n"
        else:
            result += f"  ❌ Division 컬럼 없음\n"
        
        result += "\n"
    
    return result

@tool
def integrated_dataset_analysis(metric: str = "매출수량(M/T)", group_by: str = "Division") -> str:
    """모든 데이터셋을 통합하여 분석합니다."""
    datasets = get_datasets()
    
    if len(datasets) < 2:
        return "❌ 통합 분석하려면 최소 2개의 데이터셋이 필요합니다."
    
    # 모든 데이터셋 통합
    combined_data = []
    for name, df in datasets.items():
        df_copy = df.copy()
        df_copy['데이터셋'] = name
        combined_data.append(df_copy)
    
    integrated_df = pd.concat(combined_data, ignore_index=True)
    
    result = f"📊 통합 데이터셋 분석 ({metric} 기준):\n\n"
    result += f"🔗 **통합 정보:**\n"
    result += f"  • 총 행 수: {len(integrated_df):,}개\n"
    result += f"  • 데이터셋 수: {len(datasets)}개\n"
    result += f"  • 통합 후 메모리: {integrated_df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB\n\n"
    
    if metric in integrated_df.columns and group_by in integrated_df.columns:
        # 그룹별 통합 분석
        grouped = integrated_df.groupby(group_by)[metric].agg(['sum', 'mean', 'count']).reset_index()
        grouped = grouped.sort_values('sum', ascending=False)
        
        result += f"📈 **{group_by}별 {metric} 통합 순위:**\n"
        
        # 단위 처리
        if metric == "매출수량(M/T)":
            unit = "톤"
        elif "매출액" in metric or "이익" in metric:
            unit = "억원"
        else:
            unit = ""
        
        for idx, row in grouped.head(10).iterrows():
            result += f"  {idx+1}. {row[group_by]}: {row['sum']:,.0f}{unit} (평균: {row['mean']:,.0f}{unit})\n"
        
        # 데이터셋별 기여도 분석
        result += f"\n🎯 **데이터셋별 기여도 분석:**\n"
        dataset_contribution = integrated_df.groupby('데이터셋')[metric].sum().reset_index()
        dataset_contribution = dataset_contribution.sort_values(metric, ascending=False)
        
        total_sum = dataset_contribution[metric].sum()
        
        for idx, row in dataset_contribution.iterrows():
            contribution_pct = (row[metric] / total_sum * 100) if total_sum > 0 else 0
            result += f"  • {row['데이터셋']}: {row[metric]:,.0f}{unit} ({contribution_pct:.1f}%)\n"
        
    else:
        result += f"❌ '{metric}' 또는 '{group_by}' 컬럼을 찾을 수 없습니다.\n"
    
    return result