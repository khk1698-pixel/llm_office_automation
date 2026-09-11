import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai

# API 설정
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# 함수들
def generate_text(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error("LLM 호출 중 문제가 발생했습니다.")
        return None
    
def build_prompt(text, mode):
    if mode == "이메일":
        return f"""
당신은 회사 이메일 작성 전문가입니다.
공손하고 명확한 이메일을 작성하세요.

내용:
{text}
"""
    else:
        return f"""
당신은 회사 보고서 작성 전문가입니다.

다음 내용을 기반으로 보고서를 작성하세요.

형식:
- 제목
- 요약
- 상세 내용
- 결론

내용:
{text}
"""

def validate_input(text):
    if not text or text.strip() == "":
        return False, "❌ 내용을 입력하세요."
    if len(text.strip()) < 10:
        return False, "❌ 너무 짧습니다."
    return True, "OK"

def generate_text(prompt):
    try:
        st.write("DEBUG PROMPT:", prompt)  # 👈 확인용
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"LLM 호출 실패: {e}")  # 👈 진짜 에러 보기
        return None
    
# UI
if "history" not in st.session_state:
    st.session_state.history = []

st.title("📄 업무 자동화 도구")

mode = st.selectbox("기능 선택", ["보고서", "이메일"])

user_input = st.text_area("업무 내용을 입력하세요")

if st.button("생성하기"):
    valid, msg = validate_input(user_input)

    if not valid:
        st.error(msg)
    else:
        prompt = build_prompt(user_input, mode)
        with st.spinner("문서 생성 중..."):
            result = generate_text(prompt)

        if result:
            st.markdown("## 📌 생성 결과")
            st.markdown(result)

            st.session_state.history.append({
                "mode": mode,
                "content": result
            })

            st.download_button(
                "결과 다운로드",
                result,
                file_name="result.txt"
            )

st.markdown("## 📚 생성 기록")

if st.button("🗑 전체 기록 삭제"):
    st.session_state.history = []

for i, item in enumerate(st.session_state.history):
    col1, col2 = st.columns([8, 1])

    with col1:
        with st.expander(f"{i+1}. [{item['mode']}] 결과"):
            st.markdown(item["content"])

    with col2:
        if st.button("❌", key=f"del_{i}"):
            st.session_state.history.pop(i)
            st.rerun()
            
