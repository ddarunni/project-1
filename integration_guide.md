# Integration Guide: Improved Fuzzy Matching for LangGraph Agent

## Problem Analysis Summary

Based on the analysis of your query "열연수출1그룹의 상반기 영업이익", I identified the following issues:

### 🔍 Key Findings

1. **FundsCenter Matching Issues**:
   - User input: `열연수출1그룹`
   - Actual data contains: `열연수출그룹1` and `열연수출1그룹`
   - Issue: Number position variations (숫자그룹 vs 그룹숫자)

2. **Period/Year Matching Issues**:
   - User input: `상반기` 
   - Actual data contains: `2023년상반기`, `2024년상반기`
   - Issue: Missing year context inference

3. **Current Fuzzy Matching Limitations**:
   - Basic substring matching in lines 192-216 of `tools.py`
   - No text normalization for Korean patterns
   - No confidence scoring
   - Limited fallback strategies

## 🚀 Recommended Integration Steps

### Step 1: Add the ImprovedFuzzyMatcher Class

Add this import and class to the top of your `agent/tools.py` file:

```python
# Add after existing imports
import re
from difflib import SequenceMatcher
from typing import List, Tuple, Optional, Dict, Any

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
        text = re.sub(r'(\d+)(그룹)', r'그룹\1', text)  # 1그룹 -> 그룹1
        text = re.sub(r'([가-힣]+그룹)(\d+)', r'\2\1', text)  # 그룹1 -> 1그룹
        
        return text
    
    def fuzzy_match_funds_center(self, user_input: str, actual_values: List[str]) -> Tuple[Optional[str], float, str]:
        """Enhanced fuzzy matching for FundsCenter values."""
        if not user_input or not actual_values:
            return None, 0.0, 'no_input'
            
        normalized_input = self.normalize_korean_text(user_input)
        best_matches = []
        
        for value in actual_values:
            normalized_value = self.normalize_korean_text(value)
            
            # Exact substring match (highest priority)
            if normalized_input in normalized_value or normalized_value in normalized_input:
                best_matches.append((value, 1.0, 'exact_substring'))
                continue
            
            # Keyword intersection matching
            input_keywords = re.findall(r'[가-힣]+|\d+', normalized_input)
            value_keywords = re.findall(r'[가-힣]+|\d+', normalized_value)
            
            if input_keywords and value_keywords:
                common_keywords = set(input_keywords) & set(value_keywords)
                if common_keywords:
                    keyword_score = len(common_keywords) / max(len(input_keywords), len(value_keywords))
                    if keyword_score >= self.threshold:
                        best_matches.append((value, keyword_score, 'keyword_match'))
            
            # Sequence similarity (fallback)
            similarity = SequenceMatcher(None, normalized_input, normalized_value).ratio()
            if similarity >= self.threshold:
                best_matches.append((value, similarity, 'sequence_match'))
        
        if best_matches:
            best_matches.sort(key=lambda x: x[1], reverse=True)
            return best_matches[0]
        
        return None, 0.0, 'no_match'
    
    def fuzzy_match_period(self, user_input: str, actual_values: List[str], 
                          current_year: str = "2024") -> Tuple[Optional[str], float, str]:
        """Enhanced fuzzy matching for Period/Year values."""
        if not user_input:
            return None, 0.0, 'no_input'
        
        user_input_lower = user_input.lower()
        matches = []
        
        for value in actual_values:
            value_lower = str(value).lower()
            
            # Direct substring match
            if user_input_lower in value_lower:
                score = 1.0 if current_year in value_lower else 0.95
                match_type = 'direct_match_preferred_year' if current_year in value_lower else 'direct_match'
                matches.append((value, score, match_type))
                continue
            
            # Period type matching
            if '상반기' in user_input_lower and ('상반기' in value_lower or '1분기' in value_lower or '2분기' in value_lower):
                score = 0.9 if current_year in value_lower else 0.7
                matches.append((value, score, 'period_match'))
            elif '하반기' in user_input_lower and ('하반기' in value_lower or '3분기' in value_lower or '4분기' in value_lower):
                score = 0.9 if current_year in value_lower else 0.7
                matches.append((value, score, 'period_match'))
        
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0]
        
        return None, 0.0, 'no_match'

# Create global fuzzy matcher instance
_fuzzy_matcher = ImprovedFuzzyMatcher()
```

### Step 2: Replace the FundsCenter Matching Logic

Replace lines 190-216 in your `_advanced_multi_column_query` function:

```python
# REPLACE THIS SECTION (lines 190-216):
if funds_center:
    # 향상된 그룹 매칭 (퍼지 매칭 포함)
    exact_match = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
    
    if len(exact_match) == 0:
        # 퍼지 매칭 시도 - 부분 문자열 매칭
        partial_matches = []
        if 'FundsCenter' in df.columns:
            unique_groups = df['FundsCenter'].dropna().unique()
            for group in unique_groups:
                # 그룹명에서 핵심 키워드가 있는지 확인
                if any(keyword in str(group).lower() for keyword in [funds_center[:2], funds_center[-2:]] if keyword):
                    partial_matches.append(group)
            
            if partial_matches:
                df = df[df["FundsCenter"].isin(partial_matches)]
                filters_applied.append(f"펀드센터: {funds_center} (유사매칭: {', '.join(partial_matches)})")
            else:
                # 매칭 실패 시 원본 조건 유지하되 경고
                df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
                filters_applied.append(f"펀드센터: {funds_center} (정확매칭 없음)")
        else:
            df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
            filters_applied.append(f"펀드센터: {funds_center}")
    else:
        df = exact_match
        filters_applied.append(f"펀드센터: {funds_center}")

# WITH THIS IMPROVED VERSION:
if funds_center:
    # Enhanced FundsCenter matching using fuzzy matcher
    if 'FundsCenter' in df.columns:
        unique_funds = df['FundsCenter'].dropna().unique().tolist()
        best_match, confidence, match_type = _fuzzy_matcher.fuzzy_match_funds_center(
            funds_center, unique_funds
        )
        
        if best_match and confidence >= 0.7:
            df = df[df["FundsCenter"] == best_match]
            filters_applied.append(f"펀드센터: {funds_center} → {best_match} (신뢰도: {confidence:.2f}, 방식: {match_type})")
        else:
            # Fallback to original logic with detailed warning
            df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
            available_options = ", ".join(unique_funds[:5])
            filters_applied.append(f"펀드센터: {funds_center} (정확매칭 없음, 사용가능: {available_options}...)")
    else:
        df = df[df["FundsCenter"].str.contains(funds_center, na=False, case=False)]
        filters_applied.append(f"펀드센터: {funds_center} (컬럼 없음)")
```

### Step 3: Improve Period Matching Logic

Replace lines 176-184 in your period matching section:

```python
# REPLACE THIS SECTION (lines 176-184):
if period:
    # 상반기, 하반기, 분기 등 처리
    if "상반기" in period:
        df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기", na=False)]
    elif "하반기" in period:
        df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기", na=False)]
    else:
        df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
    filters_applied.append(f"기간: {period}")

# WITH THIS IMPROVED VERSION:
if period:
    # Enhanced Period matching using fuzzy matcher
    if 'Period/Year' in df.columns:
        unique_periods = df['Period/Year'].dropna().unique().tolist()
        best_match, confidence, match_type = _fuzzy_matcher.fuzzy_match_period(
            period, unique_periods, current_year="2024"  # or extract from context
        )
        
        if best_match and confidence >= 0.8:
            if 'direct_match' in match_type:
                df = df[df["Period/Year"] == best_match]
                filters_applied.append(f"기간: {period} → {best_match} (신뢰도: {confidence:.2f})")
            else:
                # For period matches, include related periods
                if "상반기" in period:
                    df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기", na=False)]
                    # Prefer current year
                    current_year_data = df[df["Period/Year"].astype(str).str.contains("2024", na=False)]
                    if not current_year_data.empty:
                        df = current_year_data
                        filters_applied.append(f"기간: {period} → 2024년 상반기 관련 (자동추론)")
                    else:
                        filters_applied.append(f"기간: {period} → 상반기 관련 (전체연도)")
                elif "하반기" in period:
                    df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기", na=False)]
                    filters_applied.append(f"기간: {period} → 하반기 관련")
                else:
                    df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
                    filters_applied.append(f"기간: {period} (기본매칭)")
        else:
            # Fallback to original logic
            if "상반기" in period:
                df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기", na=False)]
            elif "하반기" in period:
                df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기", na=False)]
            else:
                df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
            
            available_periods = ", ".join(unique_periods[:5])
            filters_applied.append(f"기간: {period} (기본매칭, 사용가능: {available_periods}...)")
    else:
        # Original fallback
        if "상반기" in period:
            df = df[df["Period/Year"].astype(str).str.contains("상반기|1분기|2분기", na=False)]
        elif "하반기" in period:
            df = df[df["Period/Year"].astype(str).str.contains("하반기|3분기|4분기", na=False)]
        else:
            df = df[df["Period/Year"].astype(str).str.contains(period, na=False)]
        filters_applied.append(f"기간: {period}")
```

## 📊 Expected Results After Integration

After implementing these changes, the query "열연수출1그룹의 상반기 영업이익" should:

1. **Better FundsCenter Matching**:
   - Successfully match `열연수출1그룹` to `열연수출1그룹` (exact)
   - Or match to `열연수출그룹1` with high confidence
   - Show confidence scores and match types in results

2. **Improved Period Matching**:
   - Match `상반기` to `2024년상반기` (preferred current year)
   - Fall back to all `상반기` periods if current year not available
   - Provide clear feedback on which periods were matched

3. **Enhanced Error Messages**:
   - Show available options when matches fail
   - Display confidence scores and matching strategies
   - Provide better debugging information

## 🧪 Testing Your Implementation

Create a test script to verify the improvements:

```python
# Test script (save as test_improved_matching.py)
from agent.tools import set_dataframe, smart_query_processor
import pandas as pd

# Create test data
test_data = {
    'FundsCenter': ['열연수출1그룹', '열연수출그룹1', '냉연내수그룹1'] * 100,
    'Period/Year': ['2023년상반기', '2024년상반기', '2024년하반기'] * 100,
    '5.영업이익': [1000, 2000, 3000] * 100
}
df = pd.DataFrame(test_data)
set_dataframe(df)

# Test the problematic query
result = smart_query_processor.invoke({"question": "열연수출1그룹의 상반기 영업이익"})
print("Result:", result)
```

## 🎯 Additional Recommendations

1. **Add Logging**: Log matching decisions for debugging
2. **Context Awareness**: Extract years from conversation history
3. **User Feedback**: Ask users to confirm fuzzy matches when confidence is low
4. **Data Preprocessing**: Standardize data formats during upload
5. **Performance**: Cache fuzzy matching results for repeated queries

## 🔄 Rollback Plan

If issues arise, you can quickly rollback by:
1. Keep a backup of the original `tools.py`
2. Remove the `ImprovedFuzzyMatcher` class
3. Restore the original matching logic in lines 176-184 and 190-216

This implementation provides a solid foundation for handling Korean text variations while maintaining backward compatibility with your existing system.