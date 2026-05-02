from fastapi_llm.service.visa.api.schemas import HistoryItem
from fastapi_llm.service.visa.llm.rag import get_visa_rag_store
from fastapi_llm.shared.llm_client import get_llm_client


# Generate the next F1 visa interview question from the applicant profile and history.
def generate_question(profile_context: str, history: list[HistoryItem]) -> str:
    history_text = _format_history(history)
    q_ref = get_visa_rag_store().get_reference_question("F1 visa interview")
    question_prompt = f"""
        당신은 미국 F1 비자 인터뷰 면접관입니다. 사용자가 미국 F1 비자 지원자라고 생각하고 다음 조건에 맞게 질문을 생성하세요.
        
        [절대 규칙 - 반드시 지켜야 함]
        - 오직 질문 1문장만 출력하세요.
        - 다른 설명, 서론, 안내, 인사말 절대 금지
        - 이전 인터뷰를 참고해 질문 유형은 매 질문마다 바뀌어야 함
        
        지원자 정보:
        {profile_context}

        이전 인터뷰:
        {history_text}

        참고 질문:
        {q_ref}

        [정보 추출 단계 - 반드시 수행]

        지원자 정보는 I-20 문서입니다.
        
        다음 위치에서 정보를 정확히 추출하세요:
        
        1. 전공 (Major)
        - "PROGRAM OF STUDY" 섹션
        - 그 안의 "MAJOR 1" 값
        
        2. 학교명 (University)
        - "SCHOOL INFORMATION" 섹션
        - 그 안의 "SCHOOL NAME" 값
        
        3. 비용 (Cost)
        - "ESTIMATED AVERAGE COSTS"
        - TOTAL 값
        
        4. 재정 (Funding)
        - "STUDENT'S FUNDING"
        - TOTAL 값
        
        5. 시작일 (Start Date)
        - "START OF CLASSES"
        
        규칙:
        - 반드시 원문 영어 사용
        - 정확한 키워드 기반으로 찾기 (추측 금지)
        
        --------------------------------------
        [질문 유형 선택]
        
        다음 중 하나 선택:
        
        1. Academic
        2. Financial
        3. Intent
        4. Background
        
        - 이전 질문과 다른 유형 선택
        
        --------------------------------------
        [정보 사용 규칙]
        
        - Academic → Major, University 사용
        - Financial → Cost, Funding 사용
        - Intent → 미래 계획
        - Background → 동기

        [핵심 규칙]
        - 질문은 영어로 1~2문장으로 간결하게 작성하세요.
        - 참고 질문을 그대로 사용하는 것은 금지합니다.
        - 참고 질문은 오직 "문장 구조"만 참고하세요.
        - 반드시 지원자 정보의 실제 내용을 사용해서 질문을 생성하세요. (전공, 학교, 계획 등)
        - 지원자는 학교에 합격한 상태이지, 학교를 다닌 경험은 없습니다. 이를 바탕으로 질문하세요.
        - placeholder ([전공], [학교]) 절대 금지합니다
        - 이전 인터뷰의 질문과 같은 질문은 하지 않습니다.
        - 이전 인터뷰의 답변에 이어지는 꼬리질문은 금지합니다.
        - 없는 정보는 생성하지 않습니다.
        - 정보 추출 결과는 절대 출력하지 마세요.
        - 내부적으로만 사용하세요.
        - 최종 출력은 반드시 질문에 관련된 1개의 문장만 작성하세요.
"""
    return get_llm_client().invoke(question_prompt)


# Generate the final visa interview evaluation from profile, history, and RAG answer reference.
def generate_evaluation(profile_context: str, history: list[HistoryItem]) -> str:
    history_text = _format_history(history)
    audio_text = _format_audio(history)
    a_ref = get_visa_rag_store().get_reference_answer("Suggested answers")
    final_prompt = f"""
You are a US F1 visa officer.

지원자 정보:
{profile_context}

참고 답변:
{a_ref}

이전 인터뷰:
{history_text}

음성 분석:
{audio_text or "음성 분석 결과 없음"}

[핵심 규칙]

- 평가 시 한국어로 출력합니다.

[평가 기준]

1. 사용자의 답변이 지원자 정보와 일치하는 내용인가를 평가하세요.
2. 사용자의 답변이 논리성이 있는지 평가하세요.
3. 사용자의 답변이 문법적으로 오류가 없는지 평가하세요.
4. 사용자의 답변이 영어로 표현되었는지 평가하세요.
5. 참고 답변과 비교하여 지원자의 답변이 인터뷰 질문에 적절히 답변했는지 평가하세요. 
6. 음성 분석에 기반하여 지원자의 자신감과 유창성을 평가하세요. 
     - 말 속도가 너무 느리거나 빠르지 않은지 평가하세요. 
     - pause 비율이 낮을수록 유창성이 높다고 평가하세요. 
     - filler 사용이 적을수록 자신감이 높다고 평가하세요.
[추가 음성 평가 규칙]
- 음성 분석 결과가 있는 경우 위 값은 실제 측정값입니다.
- "가정", "추정", "예상"이라는 표현은 사용하지 마세요.
- duration은 답변 길이, speed는 초당 단어 수, pause_ratio는 침묵 비율, filler_count는 filler 사용 횟수입니다.
- speed, pause_ratio, filler_count를 기준으로 유창성과 자신감을 평가하세요.
- 단, duration, speed, pause_ratio, filler_count의 실제 숫자는 출력하지 마세요.
- 음성 분석 결과는 "말이 다소 빠른 편입니다", "답변 시간이 짧아 설명이 부족해 보입니다", "중간 멈춤이 적어 흐름은 자연스럽습니다"처럼 자연스러운 한국어 피드백으로만 표현하세요.
- 음성 분석 결과가 없는 경우에만 음성 평가는 생략하세요.


Output:

최종 결과: 비자 승인 또는 비자 거절
    - 실제 f1 비자 인터뷰의 결과에 맞게 "비자 승인" 또는 "비자 거절"로 출력하세요.
전반적인 피드백:
    - 한국어 한 문단으로 지원자의 잘한 점과 개선할 점을 평가하세요.

개선사항:
    - 구체적으로 무엇이 부족했는지 설명하세요.    
    - 사용자의 대답마다 1~2문장으로 평가하세요.
    - 참고 답변을 기반으로 추천 답변을 영어 답변으로 제공하세요.
    - 전체적인 음성분석 결과를 바탕으로 말하기 속도, 자신감, 유창성에 대한 피드백을 제공하세요.


"""
    return get_llm_client().invoke(final_prompt)


# Convert history objects to Q/A text for LLM prompts.
def _format_history(history: list[HistoryItem]) -> str:
    lines = []
    for item in history:
        lines.append(f"Q: {item.question}")
        if item.answer:
            lines.append(f"A: {item.answer}")
    return "\n".join(lines)


# Convert audio metrics attached to history into prompt text.
def _format_audio(history: list[HistoryItem]) -> str:
    lines = []
    for i, item in enumerate(history, 1):
        if item.audio:
            lines.append(f"Q{i}: {item.audio}")
    return "\n".join(lines)
