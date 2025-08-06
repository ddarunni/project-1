# app.py
import streamlit as st
import pandas as pd
from agent.graph_flow import graph_executor
from agent.tools import *
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# from agent import tools
# tools.df = pd.read_excel("path_to_your_file.xlsx")

import re
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


st.set_page_config(page_title="📊 철강 데이터 분석 Q&A", layout="wide")
st.title("📊 철강 실적 데이터 분석 (LangGraph 기반)")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "csv"])
if uploaded_file:
    # 시트 목록 확인
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("시트 선택", xls.sheet_names)
    df = xls.parse(sheet_name)

    # 컬럼 정제
    df.columns = df.columns.str.strip().str.replace(" ", "").str.replace("\t", "")
    st.dataframe(df, use_container_width=True)

    # 질문 예시 스타터
    st.markdown("### 💡 질문 예시 (클릭하여 바로 사용하기)")
    
    starter_examples = [
        "전체 사업실의 총 매출 수량은 얼마인가요?",
        "스테인리스 사업실의 매출 수량과 영업이익을 알려주세요",
        "전기강판판매그룹의 총 매출 수량을 알려주세요",
        "매출 수량이 가장 많은 상위 5개 그룹을 알려주세요",
        "영업이익이 가장 높은 사업실은 어디인가요?"
        "'열연수출1그룹' 중에서 'POSCO' 공급사의 총 매출수량은 얼마인가요?",
        "2023년 1분기 전체 매출 수량은 얼마인가요?",
        "2022년의 영업이익은 얼마인가요?",
    ]
    
    # 질문 예시를 버튼으로 표시
    cols = st.columns(2)
    for i, example in enumerate(starter_examples):
        col = cols[i % 2]
        if col.button(f"📝 {example}", key=f"example_{i}", use_container_width=True):
            with st.spinner("LangGraph 에이전트가 분석 중입니다..."):
                # LangGraph 실행 - df를 context로 전달
                result = graph_executor.invoke({"input": example, "df": df})
                st.success("✅ 분석 완료")
                st.markdown(f"### 💬 답변:\n{result['output']}")
    
    # 사용자 질문 입력
    question = st.text_input("또는 궁금한 점을 직접 입력하세요:")

    if st.button("질문 실행") and question:
        with st.spinner("LangGraph 에이전트가 분석 중입니다..."):
            # LangGraph 실행 - df를 context로 전달
            result = graph_executor.invoke({"input": question, "df": df})
            st.success("✅ 분석 완료")
            st.markdown(f"### 💬 답변:\n{result['output']}")