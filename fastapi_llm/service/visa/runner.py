# service/visa/runner.py

import os
import tempfile
from service.visa.llm.interview_llm import (
    setup,
    load_user_pdf,
    load_qa_dataset,
    get_question,
    get_final_evaluation,
    save_feedback_pdf,
    validate_user_file,
)

# 서버 시작 시 1회 초기화
setup()
load_qa_dataset()


async def run_mock(req: dict) -> dict:
    """
    실전 모의면접 - PDF 필수, 질문 생성
    req: { file, answer, mode }
    """
    file = req.get("file")
    answer = req.get("answer")

    # 1. PDF 저장 및 텍스트 추출
    if file is None:
        return {"error": "PDF 파일이 필요합니다."}

    # UploadFile → 임시파일로 저장
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    valid_path = validate_user_file(tmp_path)
    if not valid_path:
        return {"error": "유효하지 않은 PDF 파일입니다."}

    profile_context = load_user_pdf(valid_path, doc_type="user_data")

    # 2. 히스토리 구성 (answer 있으면 이전 답변 포함)
    history = []
    if answer:
        history.append({"question": "이전 질문", "answer": answer})

    # 3. 질문 생성
    question = get_question(profile_context, history)

    return {
        "mode": "mock",
        "question": question,
        "profile_preview": profile_context[:200],
    }


async def run_practice(req: dict) -> dict:
    """
    연습 모드 - PDF 선택, 최종 평가 or 질문 생성
    req: { file, answer, topic, mode }
    """
    file   = req.get("file")
    answer = req.get("answer")
    topic  = req.get("topic", "")

    profile_context = topic or "일반 F1 비자 지원자"

    # PDF 있으면 추출
    if file is not None:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        valid_path = validate_user_file(tmp_path)
        if valid_path:
            profile_context = load_user_pdf(valid_path, doc_type="user_data")

    history = []
    if answer:
        history.append({"question": "연습 질문", "answer": answer})

    # answer 있으면 → 최종 평가, 없으면 → 질문 생성
    if answer:
        evaluation = get_final_evaluation(profile_context, history)
        return {
            "mode": "practice",
            "evaluation": evaluation,
        }
    else:
        question = get_question(profile_context, history)
        return {
            "mode": "practice",
            "question": question,
        }