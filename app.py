# app.py
import streamlit as st
import pandas as pd
from agent.graph_flow import graph_executor
from agent.tools import *
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from agent import tools
tools.df = pd.read_excel("path_to_your_file.xlsx")

import re
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


st.set_page_config(page_title="📊 철강 데이터 분석 Q&A", layout="wide")
st.title("📊 철강 실적 데이터 분석 (LangGraph 기반)")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
if uploaded_file:
    # 시트 목록 확인
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("시트 선택", xls.sheet_names)
    df = xls.parse(sheet_name)

    # 컬럼 정제
    df.columns = df.columns.str.strip().str.replace(" ", "").str.replace("\t", "")
    st.dataframe(df.head(), use_container_width=True)

    # 사용자 질문 입력
    question = st.text_input("궁금한 점을 자연어로 입력하세요:")

    if st.button("질문 실행") and question:
        with st.spinner("LangGraph 에이전트가 분석 중입니다..."):
            # 🧠 Agent에 질문과 df를 넣어 응답 생성 (임시 df 저장)
            # 함수형 도구들이 df를 참조할 수 있도록 전역 설정
            for func in [
                get_total_sales_volume_by_division,
                get_total_sales_volume_by_fund,
                get_total_sales_volume_by_year,
                get_operating_profit_by_division,
                get_operating_profit_by_year,
                get_sales_amount_by_division,
                get_pre_tax_profit_by_division,
                get_sales_volume_by_supplier,
                get_sales_volume_by_country,
                get_overall_summary
            ]:
                func.__globals__["df"] = df  # 각 함수가 df 접근 가능하도록 함

            # LangGraph 실행
            result = graph_executor.invoke({"input": question})
            st.success("✅ 분석 완료")
            st.markdown(f"### 💬 답변:\n{result['output']}")