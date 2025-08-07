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

# 다중 파일 업로드
uploaded_files = st.file_uploader(
    "엑셀 파일 업로드 (여러 파일 선택 가능)", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)

# 세션 상태 초기화
if "uploaded_datasets" not in st.session_state:
    st.session_state.uploaded_datasets = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_dataset" not in st.session_state:
    st.session_state.active_dataset = None

if uploaded_files:
    # 업로드된 파일들 처리
    for uploaded_file in uploaded_files:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # 이미 처리된 파일인지 확인
        if file_key not in st.session_state.uploaded_datasets:
            try:
                # 엑셀 파일 처리
                if uploaded_file.name.endswith('.xlsx'):
                    xls = pd.ExcelFile(uploaded_file)
                    sheets_data = {}
                    
                    for sheet_name in xls.sheet_names:
                        df = xls.parse(sheet_name)
                        df.columns = df.columns.str.strip().str.replace(" ", "").str.replace("\t", "")
                        sheets_data[sheet_name] = df
                    
                    st.session_state.uploaded_datasets[file_key] = {
                        'name': uploaded_file.name,
                        'sheets': sheets_data,
                        'file_type': 'excel'
                    }
                    
                # CSV 파일 처리  
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    df.columns = df.columns.str.strip().str.replace(" ", "").str.replace("\t", "")
                    
                    st.session_state.uploaded_datasets[file_key] = {
                        'name': uploaded_file.name,
                        'sheets': {'Sheet1': df},
                        'file_type': 'csv'
                    }
                    
            except Exception as e:
                st.error(f"파일 '{uploaded_file.name}' 처리 중 오류: {str(e)}")
    
    # 업로드된 파일 목록 표시
    if st.session_state.uploaded_datasets:
        st.markdown("### 📁 업로드된 파일 목록")
        
        # 파일 선택 UI
        file_options = []
        file_keys = []
        for key, dataset in st.session_state.uploaded_datasets.items():
            for sheet_name in dataset['sheets'].keys():
                display_name = f"{dataset['name']} - {sheet_name}"
                file_options.append(display_name)
                file_keys.append((key, sheet_name))
        
        selected_idx = st.selectbox(
            "🎯 분석할 데이터셋 선택:", 
            range(len(file_options)),
            format_func=lambda x: file_options[x]
        )
        
        if selected_idx is not None:
            selected_key, selected_sheet = file_keys[selected_idx]
            selected_dataset = st.session_state.uploaded_datasets[selected_key]
            df = selected_dataset['sheets'][selected_sheet]
            
            # 활성 데이터셋 저장
            st.session_state.active_dataset = {
                'df': df,
                'name': f"{selected_dataset['name']} - {selected_sheet}",
                'file_key': selected_key,
                'sheet_name': selected_sheet
            }
            
            # 데이터 미리보기
            with st.expander(f"📊 데이터 미리보기: {selected_dataset['name']} - {selected_sheet}", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("행 수", f"{len(df):,}")
                with col2:
                    st.metric("열 수", f"{len(df.columns)}")
                with col3:
                    st.metric("메모리", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
                with col4:
                    st.metric("결측값", f"{df.isnull().sum().sum():,}")
                
                st.dataframe(df.head(100), use_container_width=True)
        
        # 파일 비교 섹션
        if len(st.session_state.uploaded_datasets) >= 2:
            st.markdown("### 🔍 파일 간 비교 분석")
            
            col1, col2 = st.columns(2)
            
            with col1:
                compare_idx1 = st.selectbox(
                    "비교 대상 1:",
                    range(len(file_options)),
                    format_func=lambda x: file_options[x],
                    key="compare1"
                )
            
            with col2:
                compare_idx2 = st.selectbox(
                    "비교 대상 2:",
                    range(len(file_options)),
                    format_func=lambda x: file_options[x],
                    key="compare2"
                )
            
            if compare_idx1 != compare_idx2:
                if st.button("📈 비교 분석 시작"):
                    key1, sheet1 = file_keys[compare_idx1]
                    key2, sheet2 = file_keys[compare_idx2]
                    
                    df1 = st.session_state.uploaded_datasets[key1]['sheets'][sheet1]
                    df2 = st.session_state.uploaded_datasets[key2]['sheets'][sheet2]
                    
                    # 기본 비교 정보
                    st.markdown("#### 📋 기본 정보 비교")
                    
                    comparison_data = pd.DataFrame({
                        file_options[compare_idx1]: [
                            len(df1),
                            len(df1.columns),
                            f"{df1.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB",
                            df1.isnull().sum().sum()
                        ],
                        file_options[compare_idx2]: [
                            len(df2),
                            len(df2.columns), 
                            f"{df2.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB",
                            df2.isnull().sum().sum()
                        ]
                    }, index=['행 수', '열 수', '메모리 사용량', '결측값 수'])
                    
                    st.dataframe(comparison_data)
                    
                    # 공통 컬럼 확인
                    common_cols = set(df1.columns) & set(df2.columns)
                    if common_cols:
                        st.markdown(f"#### 🔗 공통 컬럼 ({len(common_cols)}개)")
                        st.write(", ".join(sorted(common_cols)))
                    
                    # 차이점 컬럼
                    diff_cols1 = set(df1.columns) - set(df2.columns)
                    diff_cols2 = set(df2.columns) - set(df1.columns)
                    
                    if diff_cols1:
                        st.markdown(f"#### 🔸 {file_options[compare_idx1]} 고유 컬럼")
                        st.write(", ".join(sorted(diff_cols1)))
                    
                    if diff_cols2:
                        st.markdown(f"#### 🔸 {file_options[compare_idx2]} 고유 컬럼")
                        st.write(", ".join(sorted(diff_cols2)))
    
    # 질문 예시 스타터 (채팅 기록이 없을 때만 표시)
    if not st.session_state.chat_history:
        st.markdown("### 💡 질문 예시 (클릭하여 바로 사용하기)")
        
        # 키워드 안내 문구
        st.info("📌 **효과적인 질문을 위한 키워드 안내**  \n"
                "다음 키워드를 포함하여 질문하시면 더 정확한 답변을 받을 수 있습니다:  \n"
                "**사업실**, **그룹**, **판매량**, **매출액**, **영업이익**, **세전이익**, **공급사**, **고객사**, **국가**, **판매유형(삼국간,수출,내수)**")
        
        
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
        
        # 다중 파일일 경우 비교 질문 예시 추가
        if len(st.session_state.uploaded_datasets) >= 2:
            comparison_examples = [
                "두 파일의 전체 매출액을 비교해주세요",
                "각 파일의 상위 5개 사업실 영업이익을 비교분석해주세요",
                "파일별 2023년 매출수량 차이를 알려주세요",
                "두 데이터셋의 공급사별 매출 현황을 비교해주세요",
            ]
            starter_examples.extend(comparison_examples)
        
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
                
                # LangGraph 실행 - 다중 데이터셋 정보 전달
                current_df = None
                datasets_info = {}
                dataset_count = 0
                active_dataset_name = "업로드된 파일"
                
                # 현재 활성 데이터셋 설정
                if st.session_state.active_dataset:
                    current_df = st.session_state.active_dataset['df']
                    active_dataset_name = st.session_state.active_dataset['name']
                elif hasattr(st.session_state, 'df_for_chat'):
                    current_df = st.session_state.df_for_chat
                
                if current_df is None:
                    st.error("분석할 데이터셋을 선택해주세요.")
                    st.stop()
                
                # 다중 데이터셋 정보 수집
                if hasattr(st.session_state, 'uploaded_datasets') and st.session_state.uploaded_datasets:
                    # 모든 데이터셋을 datasets_info에 포함
                    for file_key, dataset_info in st.session_state.uploaded_datasets.items():
                        for sheet_name, df in dataset_info['sheets'].items():
                            dataset_name = f"{dataset_info['name']} - {sheet_name}"
                            datasets_info[dataset_name] = df
                    
                    # 실제 시트 개수로 카운트 (더 정확)
                    dataset_count = len(datasets_info)
                else:
                    dataset_count = 1
                    datasets_info[active_dataset_name] = current_df
                
                # 다중 파일 여부 결정
                is_multi_dataset = dataset_count > 1
                
                print(f"데이터셋 수: {dataset_count}, 다중 파일: {is_multi_dataset}")
                print(f"활성 데이터셋: {active_dataset_name}")
                print(f"전체 데이터셋: {list(datasets_info.keys())}")
                
                # LangGraph 상태에 다중 데이터셋 정보 전달
                result = graph_executor.invoke({
                    "input": question, 
                    "df": current_df,
                    "chat_history": chat_context,
                    # 다중 데이터셋 관련 정보
                    "datasets_info": datasets_info,
                    "dataset_count": dataset_count,
                    "is_multi_dataset": is_multi_dataset,
                    "active_dataset_name": active_dataset_name
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