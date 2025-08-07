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

    # 채팅 기록 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "df_for_chat" not in st.session_state:
        st.session_state.df_for_chat = None
    
    # 현재 데이터프레임을 세션에 저장
    st.session_state.df_for_chat = df
    
    # 질문 예시 스타터 (채팅 기록이 없을 때만 표시)
    if not st.session_state.chat_history:
        st.markdown("### 💡 질문 예시 (클릭하여 바로 사용하기)")
        
        # 키워드 안내 문구
        st.info("📌 **효과적인 질문을 위한 키워드 안내**  \n"
                "다음 키워드를 포함하여 질문하시면 더 정확한 답변을 받을 수 있습니다:  \n"
                "**사업실**, **그룹**, **판매량**, **매출액**, **영업이익**, **세전이익**, **공급사**, **고객사**, **국가**, **판매유형**")
        
        
        starter_examples = [
            "전체 사업실의 총 매출 수량은 얼마인가요?",
            "전체 사업실의 판매량과 영업이익을 알려주세요",
            "전체 사업실의 총 매출액을 알려주세요",
            "매출 수량이 가장 많은 상위 5개 그룹을 알려주세요",
            "영업이익이 가장 높은 사업실은 어디인가요?",
            "전체사업실 중에서 'POSCO' 공급사의 총 매출수량은 얼마인가요?",
            "2023년 상반기 전체 매출 수량은 얼마인가요?",
            "2023년의 영업이익은 얼마인가요?",
        ]
        
        # 질문 예시를 버튼으로 표시
        cols = st.columns(2)
        for i, example in enumerate(starter_examples):
            col = cols[i % 2]
            if col.button(f"📝 {example}", key=f"example_{i}", use_container_width=True):
                st.session_state.selected_question = example
    
    # 채팅 기록 표시
    if st.session_state.chat_history:
        st.markdown("### 💬 대화 기록")
        for i, chat in enumerate(st.session_state.chat_history):
            with st.container():
                # 사용자 질문
                with st.chat_message("user"):
                    st.markdown(chat["question"])
                
                # AI 답변
                with st.chat_message("assistant"):
                    st.markdown(chat["answer"])
                    
                    # 상세 정보 (접을 수 있는 형태)
                    with st.expander(f"📊 상세 정보 #{i+1}", expanded=False):
                        # 새로운 노드들의 처리 과정 표시
                        if chat.get("context_used", False):
                            st.markdown("#### 🔄 Context Aware 처리:")
                            st.success(f"✅ 컨텍스트 활용: {chat.get('enhanced_input', '정보 없음')}")
                        
                        intent_info = chat.get("intent_info", {})
                        query_plan = chat.get("query_plan", {})
                        
                        if intent_info:
                            st.markdown("#### 🎯 Intent Classification 결과:")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("감지된 의도", intent_info.get("intent", "general"))
                            with col2:
                                st.metric("복잡도", intent_info.get("complexity", "medium"))
                            with col3:
                                confidence = intent_info.get("confidence", 0)
                                st.metric("신뢰도", f"{confidence:.1%}")
                            
                            if intent_info.get("predicted_tools"):
                                st.markdown("**예측된 도구들:**")
                                tools_text = ", ".join(intent_info["predicted_tools"][:3])
                                st.text(tools_text)
                        
                        if query_plan:
                            st.markdown("#### 🗂️ Query Planning 결과:")
                            execution_plan = query_plan.get("execution_plan", {})
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("분석 전략", execution_plan.get("strategy", "unknown"))
                            with col2:
                                confidence = query_plan.get("confidence", 0)
                                st.metric("계획 신뢰도", f"{confidence:.1%}")
                            
                            if query_plan.get("required_columns"):
                                st.markdown("**감지된 컬럼들:**")
                                st.text(", ".join(query_plan["required_columns"]))
                            
                            if query_plan.get("detected_metrics"):
                                st.markdown("**분석 지표:**")
                                st.text(", ".join(query_plan["detected_metrics"]))
                        
                        # 데이터 출처
                        st.markdown("#### 📋 데이터 출처:")
                        st.info(chat.get("source_info", "업로드된 엑셀 파일"))
                        
                        # 계산 과정
                        if chat.get("intermediate_steps"):
                            st.markdown("#### 🔄 계산 과정:")
                            for j, step in enumerate(chat["intermediate_steps"], 1):
                                if isinstance(step, tuple) and len(step) >= 2:
                                    action, observation = step[0], step[1]
                                    st.markdown(f"**단계 {j}:** {action}")
                                    if observation:
                                        st.code(str(observation)[:300] + "..." if len(str(observation)) > 300 else str(observation))
                                else:
                                    st.markdown(f"**단계 {j}:** {str(step)}")
                        else:
                            st.markdown("#### 🔄 계산 과정:")
                            st.info("기본 집계 함수를 사용하여 계산되었습니다.")
                        
                        # 데이터 요약 정보
                        st.markdown("#### 📈 참고한 데이터 정보:")
                        
                        # 기본 정보
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("총 행 수", f"{len(df):,}개")
                        with col2:
                            st.metric("총 컬럼 수", f"{len(df.columns)}개")
                        with col3:
                            st.metric("참고 시트", sheet_name)
                        
                        # 컬럼 정보
                        st.markdown("**📋 활용한 주요 컬럼:**")
                        columns_info = []
                        for col in df.columns[:10]:  # 처음 10개 컬럼만 표시
                            col_type = str(df[col].dtype)
                            if df[col].dtype in ['object']:
                                unique_count = df[col].nunique()
                                columns_info.append(f"• **{col}** (텍스트, {unique_count}개 고유값)")
                            elif df[col].dtype in ['int64', 'float64']:
                                columns_info.append(f"• **{col}** (숫자)")
                            else:
                                columns_info.append(f"• **{col}** ({col_type})")
                        
                        st.markdown("\n".join(columns_info))
                        
                        if len(df.columns) > 10:
                            st.markdown(f"*...및 {len(df.columns) - 10}개 추가 컬럼*")
    
    # 새로운 질문 입력 영역
    st.markdown("---")
    
    # 채팅 인터페이스
    with st.container():
        # CSS to align button height with text input
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:nth-child(2) > div > div > div > button {
            height: 2.5rem;
            margin-top: 1.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            question = st.text_input(
                "질문을 입력하세요:",
                value=st.session_state.get('selected_question', ''),
                key="new_question_input",
                placeholder="예: 이전 답변에서 스테인리스 사업실에 대해 더 자세히 알려줘"
            )
        
        with col2:
            # Add some vertical spacing to align with label
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            send_button = st.button("💬 전송", type="primary", use_container_width=True)
        
        # 대화 초기화 버튼
        if st.session_state.chat_history:
            if st.button("🗑️ 대화 기록 초기화", type="secondary"):
                st.session_state.chat_history = []
                st.session_state.selected_question = ""
                st.rerun()

    # 질문 처리
    if (send_button and question) or (question and st.session_state.get('selected_question')):
        with st.spinner("LangGraph 에이전트가 분석 중입니다..."):
            try:
                # 이전 대화 컨텍스트 준비 (Context Aware Node에서 사용)
                chat_context = []
                for chat in st.session_state.chat_history[-3:]:  # 최근 3개 대화만 컨텍스트로 사용
                    chat_context.append(f"Q: {chat['question']}")
                    chat_context.append(f"A: {chat['answer']}")
                
                # LangGraph 실행
                result = graph_executor.invoke({
                    "input": question, 
                    "df": st.session_state.df_for_chat,
                    "chat_history": chat_context
                })
                
                # 채팅 기록에 추가 (Phase 1 노드 정보 포함)
                chat_entry = {
                    "question": question,
                    "answer": result['output'],
                    "source_info": result.get('source_info', '업로드된 엑셀 파일'),
                    "intermediate_steps": result.get('intermediate_steps', []),
                    # Phase 1 노드 정보
                    "enhanced_input": result.get('enhanced_input', question),
                    "context_used": result.get('context_used', False),
                    "intent_info": result.get('intent_info', {}),
                    "query_plan": result.get('query_plan', {}),
                    "processing_path": result.get('processing_path', 'agent_node')
                }
                st.session_state.chat_history.append(chat_entry)
                
                # 선택된 질문 초기화
                st.session_state.selected_question = ""
                
                # 페이지 새로고침
                st.rerun()
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.error("다시 시도해 주세요.")