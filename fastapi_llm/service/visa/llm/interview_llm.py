from fastapi_llm.service.visa.api.schemas import HistoryItem
from fastapi_llm.service.visa.llm.rag import get_visa_rag_store
from fastapi_llm.shared.llm_client import get_llm_client
from fastapi_llm.service.visa.utils.grammar import evaluate_grammar


# Generate the next F1 visa interview question from the applicant profile and history.
def generate_question(profile_context: str, history: list[HistoryItem]) -> str:
    history_text = _format_history(history)
    q_ref = get_visa_rag_store().get_reference_question("F1 visa interview")
    question_prompt = f"""
        당신은 영어권 비자 인터뷰 면접관입니다. 사용자가 영어권 비자 지원자라고 생각하고 다음 조건에 맞게 질문을 생성하세요.
        
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
    grammar_text = _format_grammar(history)
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

문법 정량 평가:
{grammar_text or "문법 정량 평가 결과 없음"}

[핵심 규칙]

- 평가 시 한국어로 출력합니다.

[점수 기반 최종 평가 기준]

최종 평가는 100점 만점으로 산정합니다.
아래 4개 항목을 각각 25점 만점으로 평가합니다.

1. 답변의 논리성 (25점)
- 사용자의 답변이 질문에 대해 논리적으로 구성되어 있는지 평가하세요.
- 답변이 질문의 핵심에 직접 답하고 있는지 확인하세요.
- 주장과 근거가 자연스럽게 연결되어 있으면 높은 점수를 부여하세요.
- 질문과 관련 없는 답변이거나 의미가 모호하면 낮은 점수를 부여하세요.
- 이 항목은 직접 평가하여 0~25점 사이의 점수를 부여하세요.

2. 답변의 일치성 (25점)
- 사용자의 답변이 지원자 정보(profile_context)와 일치하는지 평가하세요.
- 학교명, 전공, 학비, 재정 정보, 입학 시기 등 핵심 정보가 지원자 정보와 충돌하지 않는지 확인하세요.
- 지원자 정보에 없는 내용을 과도하게 단정하거나 허위로 말한 경우 낮은 점수를 부여하세요.
- 이 항목은 직접 평가하여 0~25점 사이의 점수를 부여하세요.

3. 언어 문법 평가 (25점)
- 문법 정량 평가 결과의 grammar_score_25 값을 그대로 사용하세요.
- 이 점수는 Python 문법 평가 모델로 계산된 실제 점수입니다.
- grammar_score_25를 임의로 수정하지 마세요.
- 문법 정량 평가 결과가 없는 경우에만 답변 텍스트를 기준으로 직접 평가하세요.

4. 언어 구사 능력 (25점)
- 음성 분석 결과의 speaking_score_25 값을 그대로 사용하세요.
- 이 점수는 말하기 속도, 리듬, 유창성을 기반으로 계산된 실제 점수입니다.
- speaking_score_25를 임의로 수정하지 마세요.
- 음성 분석 결과가 없는 경우에만 음성 평가는 생략하거나 낮은 점수로 평가하세요.

[합격/불합격 기준]

- 총점은 위 4개 항목의 합산입니다.
- 총점이 80점 이상이면 "합격"으로 판정하세요.
- 총점이 80점 미만이면 "불합격"으로 판정하세요.
- 최종 결과는 반드시 "합격" 또는 "불합격" 중 하나만 출력하세요.
- 총점과 항목별 점수는 내부 판단에만 사용하고, 출력에는 표시하지 마세요.
- 단, 아래 조건 중 하나라도 해당하면 총점과 관계없이 반드시 "불합격"으로 판정하세요.
  1. 사용자가 영어로 답변하지 않은 경우
  2. 사용자의 답변이 지원자 정보(profile_context)와 명백히 일치하지 않는 경우

[피드백 작성 기준]

- 문법 정량 평가 결과가 있는 경우 grammar_score_25는 25점 만점의 실제 문법 점수입니다.
- grammar_score_25가 낮을수록 문법 오류나 어색한 표현이 많은 답변으로 평가하세요.
- grammar_corrected_text는 문법 교정 참고용 문장입니다.
- 단, grammar_error_ratio의 실제 숫자는 출력하지 마세요.
- 실제 숫자는 출력하지 말고 자연스럽게 말하세요. 예를 들어 grammar_score_25가 낮으면 "문법 오류가 다수 발견됩니다"와 같이 표현하세요.
- 출력문에는 점수, 배점, 총점, 항목별 점수, "00/100", "00/25", "(10/25)" 같은 숫자 표현을 절대 포함하지 마세요.
- "답변의 논리성", "답변의 일치성", "언어 문법 평가", "언어 구사 능력" 같은 평가 항목명을 점수표처럼 나열하지 마세요.
- 점수 계산은 내부 판단에만 사용하고, 사용자에게는 자연스러운 문장형 피드백만 제공하세요.

Output:

최종 결과: 합격 또는 불합격

전반적인 피드백:
- 한국어 한 문단으로 지원자의 답변 전반을 평가하고, 합격 또는 불합격 판단의 핵심 이유를 설명하세요.

개선사항:
- 질문과 사용자의 답변을 다시 출력하세요.
- 각 질문에 대한 사용자의 대답마다 1~2문장으로 부족한 점과 개선 방향을 자연스러운 문장으로 작성하세요.
- 필요한 경우 참고 답변을 기반으로 추천 영어 답변을 제공하세요.
- 각 질문마다 음성 분석 결과를 바탕으로 말하기 문법, 속도, 자신감, 유창성에 대한 피드백을 자연스럽게 제공하세요.
"""
    return get_llm_client().invoke(final_prompt)

# 총점: 00/100

# 항목별 점수:
# - 답변의 논리성: 00/25
# - 답변의 일치성: 00/25
# - 언어 문법 평가: 00/25
# - 언어 구사 능력: 00/25
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


# Convert grammar scores for answered history into prompt text.
def _format_grammar(history: list[HistoryItem]) -> str:
    lines = []
    for i, item in enumerate(history, 1):
        if item.answer:
            grammar = evaluate_grammar(item.answer)
            lines.append(f"Q{i}: {grammar}")
    return "\n".join(lines)
