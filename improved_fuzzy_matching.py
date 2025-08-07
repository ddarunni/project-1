#!/usr/bin/env python3
"""
Improved Fuzzy Matching Implementation for LangGraph Agent

This module provides enhanced fuzzy matching capabilities to resolve the data matching
issues identified in the analysis. Key improvements include:

1. Better handling of Korean text patterns
2. Number position normalization (열연수출1그룹 ↔ 열연수출그룹1)
3. Year context inference for periods
4. Multi-level matching strategies with confidence scoring
"""

import re
from difflib import SequenceMatcher
from typing import List, Tuple, Optional, Dict, Any
import pandas as pd


class ImprovedFuzzyMatcher:
    """Enhanced fuzzy matching for Korean business data."""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        
    def normalize_korean_text(self, text: str) -> str:
        """Normalize Korean text for better matching."""
        if not text:
            return ""
            
        text = str(text)
        # Remove spaces and convert to lowercase
        text = re.sub(r'\s+', '', text.lower())
        
        # Handle Korean number positioning variations
        # Pattern 1: Move numbers before 그룹 (1그룹 -> 그룹1)
        text = re.sub(r'(\d+)(그룹)', r'그룹\1', text)
        # Pattern 2: Move numbers after text (그룹1 -> 1그룹)
        text = re.sub(r'([가-힣]+그룹)(\d+)', r'\2\1', text)
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from Korean text."""
        normalized = self.normalize_korean_text(text)
        # Extract Korean text blocks and numbers
        keywords = re.findall(r'[가-힣]+|\d+', normalized)
        return keywords
    
    def fuzzy_match_funds_center(self, user_input: str, actual_values: List[str]) -> Tuple[Optional[str], float, str]:
        """
        Enhanced fuzzy matching for FundsCenter values.
        
        Returns:
            (best_match, confidence_score, match_type)
        """
        if not user_input or not actual_values:
            return None, 0.0, 'no_input'
            
        normalized_input = self.normalize_korean_text(user_input)
        best_matches = []
        
        for value in actual_values:
            normalized_value = self.normalize_korean_text(value)
            
            # Strategy 1: Exact substring match (highest priority)
            if normalized_input in normalized_value or normalized_value in normalized_input:
                best_matches.append((value, 1.0, 'exact_substring'))
                continue
            
            # Strategy 2: Keyword intersection matching
            input_keywords = self.extract_keywords(user_input)
            value_keywords = self.extract_keywords(value)
            
            if input_keywords and value_keywords:
                common_keywords = set(input_keywords) & set(value_keywords)
                if common_keywords:
                    keyword_score = len(common_keywords) / max(len(input_keywords), len(value_keywords))
                    if keyword_score >= self.threshold:
                        best_matches.append((value, keyword_score, 'keyword_match'))
            
            # Strategy 3: Pattern-based matching for group names
            if self._is_group_pattern_match(user_input, value):
                pattern_score = 0.85  # High confidence for pattern matches
                best_matches.append((value, pattern_score, 'pattern_match'))
            
            # Strategy 4: Sequence similarity (lowest priority)
            similarity = SequenceMatcher(None, normalized_input, normalized_value).ratio()
            if similarity >= self.threshold:
                best_matches.append((value, similarity, 'sequence_match'))
        
        # Return best match
        if best_matches:
            best_matches.sort(key=lambda x: x[1], reverse=True)
            return best_matches[0]
        
        return None, 0.0, 'no_match'
    
    def _is_group_pattern_match(self, user_input: str, actual_value: str) -> bool:
        """Check if two group names match common Korean business patterns."""
        # Extract base name and number
        user_pattern = re.search(r'([가-힣]+)(\d*)(그룹)?(\d*)', user_input)
        actual_pattern = re.search(r'([가-힣]+)(\d*)(그룹)?(\d*)', actual_value)
        
        if not (user_pattern and actual_pattern):
            return False
        
        user_base = user_pattern.group(1)
        actual_base = actual_pattern.group(1)
        
        # Check if base names are similar (e.g., 열연수출 matches)
        if user_base in actual_base or actual_base in user_base:
            # Extract all numbers from both strings
            user_numbers = re.findall(r'\d+', user_input)
            actual_numbers = re.findall(r'\d+', actual_value)
            
            # If numbers match, it's likely the same group
            if user_numbers and actual_numbers and user_numbers[0] == actual_numbers[0]:
                return True
        
        return False
    
    def fuzzy_match_period(self, user_input: str, actual_values: List[str], 
                          current_year: str = "2024", context_years: List[str] = None) -> Tuple[Optional[str], float, str]:
        """
        Enhanced fuzzy matching for Period/Year values.
        
        Args:
            user_input: User's period input (e.g., "상반기")
            actual_values: List of actual period values in data
            current_year: Current year to prefer in matching
            context_years: Years mentioned in conversation context
            
        Returns:
            (best_match, confidence_score, match_type)
        """
        if not user_input:
            return None, 0.0, 'no_input'
        
        user_input_lower = user_input.lower()
        matches = []
        
        # Determine preferred years (context > current > any)
        preferred_years = []
        if context_years:
            preferred_years.extend(context_years)
        if current_year:
            preferred_years.append(current_year)
        
        for value in actual_values:
            value_lower = str(value).lower()
            
            # Strategy 1: Direct substring match
            if user_input_lower in value_lower:
                # Boost score if preferred year
                score = 1.0
                match_type = 'direct_match'
                
                if preferred_years and any(year in value_lower for year in preferred_years):
                    score = 1.0
                    match_type = 'direct_match_preferred_year'
                else:
                    score = 0.95
                
                matches.append((value, score, match_type))
                continue
            
            # Strategy 2: Period type matching with year preference
            period_match_score = self._get_period_match_score(user_input_lower, value_lower)
            if period_match_score > 0:
                # Prefer current/context years
                if preferred_years and any(year in value_lower for year in preferred_years):
                    final_score = min(period_match_score + 0.1, 1.0)
                    match_type = 'period_match_preferred_year'
                else:
                    final_score = period_match_score
                    match_type = 'period_match'
                
                matches.append((value, final_score, match_type))
        
        # Return best match
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0]
        
        return None, 0.0, 'no_match'
    
    def _get_period_match_score(self, user_period: str, actual_period: str) -> float:
        """Calculate matching score for period patterns."""
        
        # 상반기/하반기 matching
        if '상반기' in user_period:
            if '상반기' in actual_period:
                return 0.9
            elif '1분기' in actual_period or '2분기' in actual_period:
                return 0.8
        
        elif '하반기' in user_period:
            if '하반기' in actual_period:
                return 0.9
            elif '3분기' in actual_period or '4분기' in actual_period:
                return 0.8
        
        # Specific quarter matching
        elif '분기' in user_period:
            quarter_match = re.search(r'(\d)분기', user_period)
            if quarter_match and quarter_match.group(0) in actual_period:
                return 0.9
        
        # Year matching
        year_match = re.search(r'(20\d{2})', user_period)
        if year_match and year_match.group(0) in actual_period:
            return 0.7
        
        return 0.0


def create_enhanced_advanced_multi_column_query(matcher: ImprovedFuzzyMatcher = None):
    """
    Factory function to create an enhanced version of _advanced_multi_column_query
    with improved fuzzy matching.
    """
    if matcher is None:
        matcher = ImprovedFuzzyMatcher()
    
    def enhanced_advanced_multi_column_query(
        df: pd.DataFrame,
        division: str = None,
        country: str = None, 
        year: str = None,
        period: str = None,
        supplier: str = None,
        funds_center: str = None,
        metric: str = "매출수량(M/T)",
        context_years: List[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced version with improved fuzzy matching.
        
        Returns:
            Dict containing result, debug info, and matching details
        """
        original_count = len(df)
        filters_applied = []
        matching_details = {}
        
        # Enhanced FundsCenter matching
        if funds_center and 'FundsCenter' in df.columns:
            unique_funds = df['FundsCenter'].dropna().unique().tolist()
            best_match, confidence, match_type = matcher.fuzzy_match_funds_center(
                funds_center, unique_funds
            )
            
            matching_details['funds_center'] = {
                'user_input': funds_center,
                'best_match': best_match,
                'confidence': confidence,
                'match_type': match_type,
                'available_options': unique_funds[:10]  # First 10 for debugging
            }
            
            if best_match and confidence >= 0.7:
                df = df[df["FundsCenter"] == best_match]
                filters_applied.append(f"펀드센터: {funds_center} → {best_match} (신뢰도: {confidence:.2f}, 방식: {match_type})")
            else:
                # Fallback to original logic with warning
                df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
                filters_applied.append(f"펀드센터: {funds_center} (기본매칭, 정확한 매칭 없음)")
        
        # Enhanced Period matching
        if period and 'Period/Year' in df.columns:
            unique_periods = df['Period/Year'].dropna().unique().tolist()
            best_match, confidence, match_type = matcher.fuzzy_match_period(
                period, unique_periods, context_years=context_years
            )
            
            matching_details['period'] = {
                'user_input': period,
                'best_match': best_match,
                'confidence': confidence,
                'match_type': match_type,
                'available_options': unique_periods[:10]
            }
            
            if best_match and confidence >= 0.7:
                if match_type in ['direct_match', 'direct_match_preferred_year']:
                    df = df[df["Period/Year"] == best_match]
                else:
                    # For period matches, might need to match multiple values
                    matching_periods = [p for p in unique_periods if 
                                      matcher._get_period_match_score(period.lower(), str(p).lower()) > 0.7]
                    if matching_periods:
                        df = df[df["Period/Year"].isin(matching_periods)]
                        best_match = f"{len(matching_periods)} periods"
                
                filters_applied.append(f"기간: {period} → {best_match} (신뢰도: {confidence:.2f}, 방식: {match_type})")
            else:
                # Fallback logic
                if "상반기" in period:
                    df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기", na=False)]
                elif "하반기" in period:
                    df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기", na=False)]
                else:
                    df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
                filters_applied.append(f"기간: {period} (기본매칭)")
        
        # Apply other filters (unchanged)
        if division:
            df = df[df["Division"].str.contains(division, na=False, case=False)]
            filters_applied.append(f"사업부: {division}")
        
        if country:
            df = df[df["Country"].str.contains(country, na=False, case=False)]
            filters_applied.append(f"국가: {country}")
        
        if year:
            df = df[df["Period/Year"].astype(str).str.contains(str(year), na=False)]
            filters_applied.append(f"연도: {year}")
        
        if supplier:
            df = df[df["Supplier"].str.contains(supplier, na=False, case=False)]
            filters_applied.append(f"공급사: {supplier}")
        
        # Calculate result
        result_data = {
            'filtered_df': df,
            'original_count': original_count,
            'filtered_count': len(df),
            'filters_applied': filters_applied,
            'matching_details': matching_details,
            'success': len(df) > 0
        }
        
        if len(df) == 0:
            result_data['message'] = f"조건에 맞는 데이터가 없습니다. 적용된 필터: {', '.join(filters_applied)}"
            return result_data
        
        if metric in df.columns:
            total = df[metric].sum()
            filtered_count = len(df)
            
            # Unit handling
            if metric == "매출수량(M/T)":
                unit = "톤"
            elif "매출액" in metric or "이익" in metric:
                unit = "억원" 
            else:
                unit = ""
            
            message = f"{', '.join(filters_applied)} 조건의 {metric}: {total:,.0f}{unit}"
            message += f"\n(총 {filtered_count:,}개 레코드 중에서 집계, 전체 데이터의 {filtered_count/original_count:.1%})"
            
            result_data.update({
                'message': message,
                'total': total,
                'unit': unit,
                'metric': metric
            })
        else:
            result_data['message'] = f"지표 '{metric}'를 찾을 수 없습니다."
            result_data['success'] = False
        
        return result_data
    
    return enhanced_advanced_multi_column_query


# Example usage and testing
if __name__ == "__main__":
    # Test the fuzzy matcher
    matcher = ImprovedFuzzyMatcher()
    
    # Test FundsCenter matching
    funds_centers = [
        '열연수출그룹1', '열연수출그룹2', '냉연내수그룹1', '냉연내수그룹2',
        '스테인리스그룹1', '스테인리스그룹2', '후판그룹1', '후판그룹2',
        '열연수출1그룹', '열연수출2그룹', '냉연내수1그룹', '냉연내수2그룹'
    ]
    
    test_input = "열연수출1그룹"
    result, confidence, match_type = matcher.fuzzy_match_funds_center(test_input, funds_centers)
    print(f"FundsCenter Test:")
    print(f"Input: {test_input}")
    print(f"Match: {result} (confidence: {confidence:.2f}, type: {match_type})")
    
    # Test Period matching
    periods = [
        '2023년상반기', '2023년하반기', '2023년1분기', '2023년2분기',
        '2024년상반기', '2024년하반기', '2024년1분기', '2024년2분기'
    ]
    
    test_period = "상반기"
    result, confidence, match_type = matcher.fuzzy_match_period(test_period, periods, current_year="2024")
    print(f"\nPeriod Test:")
    print(f"Input: {test_period}")
    print(f"Match: {result} (confidence: {confidence:.2f}, type: {match_type})")