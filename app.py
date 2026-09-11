import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from fpdf import FPDF

# API 설정
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API 키 없음 (.env 확인)")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# 함수들
def generate_text(prompt):
    try:
        response = model.generate_content(prompt)
        
        if not response or not hasattr(response, "text"):
            return None
        
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



def generate_pdf(history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.add_font("Nanum", "", "NanumGothic.ttf", uni=True)
    pdf.set_font("Nanum", size=12)
    
    for i, item in enumerate(history, 1):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt=f"{i}. [{item['mode']}]", ln=True)

        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, item["content"])
        pdf.ln(5)

    file_path = "report.pdf"
    pdf.output(file_path)
    return file_path

if "history" not in st.session_state:
    st.session_state.history = []

# UI
st.title("📄 업무 자동화 도구")

mode = st.selectbox("기능 선택", ["보고서", "이메일"])
user_input = st.text_area("업무 내용을 입력하세요")

if st.button("생성하기"):
    valid, msg = validate_input(user_input)

    if not valid:
        st.error(msg)
    else:
        prompt = build_prompt(user_input, mode)

        result = None

        with st.spinner("문서 생성 중..."):
            result = generate_text(prompt)

        if result is None:
            st.error("❌ 결과를 생성하지 못했습니다. 다시 시도해주세요.")
        else:
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
search = st.text_input("🔍 기록 검색")
filter_mode = st.selectbox("모드 필터", ["전체", "보고서", "이메일"])

st.markdown("## 📚 생성 기록")

filtered_history = st.session_state.history

if filter_mode != "전체":
    filtered_history = [
        item for item in filtered_history
        if item["mode"] == filter_mode
    ]

if search:
    filtered_history = [
        item for item in filtered_history
        if search.lower() in item["content"].lower()
    ]

if st.button("🗑 전체 기록 삭제"):
    st.session_state.history = []

for i, item in enumerate(filtered_history):
    col1, col2 = st.columns([8, 1])

    with col1:
        with st.expander(f"{i+1}번째 [{item['mode']}] 결과"):
            st.markdown(item["content"])

    with col2:
        if st.button("❌", key=f"del_{i}"):
            del st.session_state.history[i]
            st.rerun()

if st.button("📥 전체 PDF 다운로드"):
    if len(st.session_state.history) == 0:
        st.warning("저장된 기록이 없습니다.")
    else:
        file_path = generate_pdf(st.session_state.history)

        with open(file_path, "rb") as f:
            st.download_button(
                "PDF 저장",
                f,
                file_name="llm_report.pdf"
            )