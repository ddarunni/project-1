#!/usr/bin/env python3
"""
Test script to analyze the data matching issues with the smart_query_processor.

This script demonstrates the tools for analyzing FundsCenter and Period/Year data
and provides recommendations for improving fuzzy matching.
"""

import pandas as pd
import sys
import os
sys.path.append('.')

from agent.tools import (
    set_dataframe, 
    get_unique_values, 
    get_column_info,
    smart_query_processor,
    _extract_complex_entities,
    _advanced_multi_column_query
)

# Create sample data similar to the real dataset based on the code analysis
def create_sample_data():
    """Create sample data that matches the expected structure."""
    
    # Create 800 rows of data
    num_rows = 800
    
    funds_centers = [
        '열연수출그룹1', '열연수출그룹2', '냉연내수그룹1', '냉연내수그룹2',
        '스테인리스그룹1', '스테인리스그룹2', '후판그룹1', '후판그룹2',
        '열연수출1그룹', '열연수출2그룹', '냉연내수1그룹', '냉연내수2그룹',
        '모빌리티그룹1', '모빌리티그룹2', '에너지인프라그룹1', '에너지인프라그룹2'
    ]
    
    divisions = [
        '스테인리스사업실', '모빌리티사업실', '열연조강사업실', '냉연사업실',
        '후판선재사업실', '에너지인프라강재사업실', '자동차소재사업실'
    ]
    
    periods = [
        '2023년상반기', '2023년하반기', '2023년1분기', '2023년2분기', 
        '2023년3분기', '2023년4분기', '2024년상반기', '2024년하반기',
        '2024년1분기', '2024년2분기', '2024년3분기', '2024년4분기'
    ]
    
    countries = ['한국', '중국', '일본', '미국', '독일', '인도']
    suppliers = ['POSCO', '현대제철', '동국제강', '세아제강']
    
    # Create data with proper cycling
    data = {
        'FundsCenter': [funds_centers[i % len(funds_centers)] for i in range(num_rows)],
        'Division': [divisions[i % len(divisions)] for i in range(num_rows)],
        'Period/Year': [periods[i % len(periods)] for i in range(num_rows)],
        'Country': [countries[i % len(countries)] for i in range(num_rows)],
        'Supplier': [suppliers[i % len(suppliers)] for i in range(num_rows)],
        
        # Metrics
        '매출수량(M/T)': [1000 + i * 10 for i in range(num_rows)],
        '1.매출액': [50000 + i * 1000 for i in range(num_rows)],
        '5.영업이익': [5000 + i * 100 for i in range(num_rows)],
        '8.세전이익': [4000 + i * 80 for i in range(num_rows)],
    }
    
    return pd.DataFrame(data)

def analyze_fuzzy_matching_issues():
    """Analyze the fuzzy matching issues and provide recommendations."""
    
    print("=" * 80)
    print("🔍 FUZZY MATCHING ANALYSIS FOR LANGGRAPH AGENT")
    print("=" * 80)
    
    # Create and set sample data
    df = create_sample_data()
    set_dataframe(df)
    
    print(f"✅ Created sample dataset with {len(df)} rows and {len(df.columns)} columns")
    
    # Test the problematic query
    test_query = "열연수출1그룹의 상반기 영업이익"
    print(f"\n🎯 Testing problematic query: '{test_query}'")
    
    # 1. Extract entities
    entities = _extract_complex_entities(test_query)
    print(f"\n📋 Entity extraction results:")
    for key, value in entities.items():
        if value:
            print(f"  • {key}: {value}")
    
    # 2. Get unique values for FundsCenter
    print(f"\n📊 Analysis 1: FundsCenter unique values")
    print("=" * 50)
    funds_center_info = get_unique_values.invoke({"column_name": "FundsCenter", "limit": 20})
    print(funds_center_info)
    
    # 3. Get unique values for Period/Year  
    print(f"\n📊 Analysis 2: Period/Year unique values")
    print("=" * 50)
    period_info = get_unique_values.invoke({"column_name": "Period/Year", "limit": 20})
    print(period_info)
    
    # 4. Get column info for FundsCenter
    print(f"\n📊 Analysis 3: FundsCenter column details")
    print("=" * 50)
    funds_column_info = get_column_info.invoke({"column_name": "FundsCenter"})
    print(funds_column_info)
    
    # 5. Get column info for Period/Year
    print(f"\n📊 Analysis 4: Period/Year column details")
    print("=" * 50)
    period_column_info = get_column_info.invoke({"column_name": "Period/Year"})
    print(period_column_info)
    
    # 6. Test the smart query processor
    print(f"\n🤖 Analysis 5: Smart Query Processor Result")
    print("=" * 50)
    result = smart_query_processor.invoke({"question": test_query})
    print(result)
    
    return df, entities

def analyze_matching_gaps(df, entities):
    """Analyze the gaps between user input and actual data."""
    
    print(f"\n🔍 GAP ANALYSIS")
    print("=" * 50)
    
    user_funds_center = entities.get('funds_center', '')
    user_period = entities.get('period', '')
    
    print(f"User input - FundsCenter: '{user_funds_center}'")
    print(f"User input - Period: '{user_period}'")
    
    # Check exact matches
    actual_funds_centers = df['FundsCenter'].unique()
    actual_periods = df['Period/Year'].unique()
    
    # Find closest matches for FundsCenter
    print(f"\n🎯 FundsCenter matching analysis:")
    exact_match = any(user_funds_center in center for center in actual_funds_centers)
    print(f"  • Exact substring match found: {exact_match}")
    
    # Find partial matches
    partial_matches = []
    if user_funds_center:
        for center in actual_funds_centers:
            if '열연수출' in center and '1' in center:
                partial_matches.append(center)
    
    print(f"  • Potential matches: {partial_matches}")
    
    # Find closest matches for Period
    print(f"\n📅 Period matching analysis:")
    period_matches = []
    if user_period == '상반기':
        for period in actual_periods:
            if '상반기' in period:
                period_matches.append(period)
    
    print(f"  • Period matches for '{user_period}': {period_matches}")

def provide_recommendations():
    """Provide specific recommendations for improving fuzzy matching."""
    
    print(f"\n💡 RECOMMENDATIONS FOR IMPROVED FUZZY MATCHING")
    print("=" * 60)
    
    recommendations = [
        {
            "issue": "FundsCenter Pattern Mismatch",
            "problem": "User inputs '열연수출1그룹' but data contains '열연수출그룹1' or '열연수출1그룹'",
            "solutions": [
                "1. Normalize group names by removing/adding numbers at different positions",
                "2. Use regex patterns to match '열연수출[그룹]?[0-9]+' formats",
                "3. Implement Levenshtein distance for similarity matching",
                "4. Create a mapping dictionary for common group name variations"
            ]
        },
        {
            "issue": "Period Format Variations", 
            "problem": "User inputs '상반기' but data contains '2023년상반기', '2024년상반기'",
            "solutions": [
                "1. Extract year context from conversation or default to current year",
                "2. Match partial period strings within full period formats",
                "3. Implement period alias mapping ('상반기' -> ['상반기', '1분기', '2분기'])",
                "4. Use fuzzy year inference based on data availability"
            ]
        },
        {
            "issue": "Case Sensitivity and Spacing",
            "problem": "Variations in spacing, case, and character encoding",
            "solutions": [
                "1. Normalize all text to lowercase and remove spaces",
                "2. Handle Korean character encoding variations",
                "3. Implement text preprocessing pipeline",
                "4. Use phonetic matching for Korean text"
            ]
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['issue']}")
        print(f"   Problem: {rec['problem']}")
        print(f"   Solutions:")
        for solution in rec['solutions']:
            print(f"     {solution}")

def generate_improved_fuzzy_matching_code():
    """Generate improved fuzzy matching code."""
    
    print(f"\n💻 IMPROVED FUZZY MATCHING CODE")
    print("=" * 50)
    
    improved_code = '''
def improved_fuzzy_match_funds_center(user_input, actual_values, threshold=0.7):
    """
    Improved fuzzy matching for FundsCenter values.
    """
    import re
    from difflib import SequenceMatcher
    
    def normalize_text(text):
        """Normalize Korean text for better matching."""
        if not text:
            return ""
        # Remove spaces and convert to lowercase
        text = re.sub(r'\\s+', '', str(text).lower())
        # Handle number positioning variations
        text = re.sub(r'(\\d+)(그룹)', r'그룹\\1', text)  # 1그룹 -> 그룹1
        text = re.sub(r'그룹(\\d+)', r'\\1그룹', text)    # 그룹1 -> 1그룹
        return text
    
    normalized_input = normalize_text(user_input)
    best_matches = []
    
    for value in actual_values:
        normalized_value = normalize_text(value)
        
        # Exact substring match (highest priority)
        if normalized_input in normalized_value or normalized_value in normalized_input:
            best_matches.append((value, 1.0, 'exact_substring'))
            continue
        
        # Extract keywords for partial matching
        input_keywords = re.findall(r'[가-힣]+|\\d+', normalized_input)
        value_keywords = re.findall(r'[가-힣]+|\\d+', normalized_value)
        
        # Keyword intersection score
        common_keywords = set(input_keywords) & set(value_keywords)
        if common_keywords and input_keywords:
            keyword_score = len(common_keywords) / len(input_keywords)
            if keyword_score >= threshold:
                best_matches.append((value, keyword_score, 'keyword_match'))
        
        # Sequence similarity
        similarity = SequenceMatcher(None, normalized_input, normalized_value).ratio()
        if similarity >= threshold:
            best_matches.append((value, similarity, 'sequence_match'))
    
    # Sort by score (descending) and return best match
    if best_matches:
        best_matches.sort(key=lambda x: x[1], reverse=True)
        return best_matches[0][0], best_matches[0][1], best_matches[0][2]
    
    return None, 0.0, 'no_match'

def improved_fuzzy_match_period(user_input, actual_values, current_year="2024"):
    """
    Improved fuzzy matching for Period/Year values.
    """
    if not user_input:
        return None, 0.0, 'no_input'
    
    user_input_lower = user_input.lower()
    matches = []
    
    for value in actual_values:
        value_lower = str(value).lower()
        
        # Direct substring match
        if user_input_lower in value_lower:
            matches.append((value, 1.0, 'direct_match'))
            continue
        
        # Period type matching
        if '상반기' in user_input_lower:
            if '상반기' in value_lower or '1분기' in value_lower or '2분기' in value_lower:
                # Prefer current year or most recent year
                if current_year in value_lower:
                    matches.append((value, 0.9, 'period_with_preferred_year'))
                else:
                    matches.append((value, 0.7, 'period_match'))
        
        elif '하반기' in user_input_lower:
            if '하반기' in value_lower or '3분기' in value_lower or '4분기' in value_lower:
                if current_year in value_lower:
                    matches.append((value, 0.9, 'period_with_preferred_year'))
                else:
                    matches.append((value, 0.7, 'period_match'))
        
        elif '분기' in user_input_lower:
            quarter_match = re.search(r'(\\d)분기', user_input_lower)
            if quarter_match and quarter_match.group(0) in value_lower:
                matches.append((value, 0.8, 'quarter_match'))
    
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[0][0], matches[0][1], matches[0][2]
    
    return None, 0.0, 'no_match'
'''
    
    print(improved_code)

if __name__ == "__main__":
    # Run the complete analysis
    df, entities = analyze_fuzzy_matching_issues()
    analyze_matching_gaps(df, entities)
    provide_recommendations()
    generate_improved_fuzzy_matching_code()
    
    print(f"\n✅ Analysis completed!")
    print(f"\n📋 Summary:")
    print(f"   • Created sample dataset with realistic data patterns")
    print(f"   • Identified key matching issues in FundsCenter and Period/Year")
    print(f"   • Provided specific recommendations for improvement")
    print(f"   • Generated improved fuzzy matching code")
    print(f"\n🎯 Key findings:")
    print(f"   • FundsCenter: Need to handle number position variations")
    print(f"   • Period/Year: Need to infer year context and match partial periods")
    print(f"   • General: Implement text normalization and similarity scoring")