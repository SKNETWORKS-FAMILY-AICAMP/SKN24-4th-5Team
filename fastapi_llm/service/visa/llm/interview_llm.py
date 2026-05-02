"""
llm/interview_llm.py
────────────────────
LLM / 벡터DB / PDF 처리 / 피드백 PDF 생성을 담당하는 핵심 모듈.

Public API
──────────
setup()                        - LLM·임베딩·벡터DB 초기화 (최초 1회)
load_user_pdf(pdf_path)        - 사용자 PDF 를 벡터DB 에 저장, 텍스트 반환
load_qa_dataset()              - HuggingFace QA 데이터셋 로드 및 벡터DB 저장
get_question(profile, history) - LLM 으로 인터뷰 질문 생성
get_final_evaluation(profile, history) - LLM 으로 최종 평가 생성
save_feedback_pdf(text, filename)      - 피드백을 PDF 로 저장
validate_user_file(file_path)          - PDF 파일 유효성 검사
"""

import os
import sys
import re
import random
import datetime

import pandas as pd
from datasets import load_dataset

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from service.visa.config.settings import (
    LLM_MODEL, LLM_TEMPERATURE,
    EMBED_MODEL_NAME, EMBED_DEVICE,
    CHROMA_COLLECTION, CHROMA_DB_PATH,
    FONT_PATH, MAX_PDF_SIZE_MB,
)

# ── 싱글턴 객체 ───────────────────────────────────────────────────────────────
_llm          = None
_embed_model  = None
_vector_store = None
_qa_retriever    = None
_user_retriever  = None
_essay_retriever = None


# ═════════════════════════════════════════════════════════════════════════════
# 초기화
# ═════════════════════════════════════════════════════════════════════════════

def setup() -> None:
    """LLM, 임베딩 모델, 벡터DB를 초기화합니다. 최초 1회만 실행합니다."""
    global _llm, _embed_model, _vector_store
    global _qa_retriever, _user_retriever, _essay_retriever

    if _llm is not None:
        return  # 이미 초기화됨

    print("[LLM] 모델 초기화 중...")
    _llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    print("[Embed] 임베딩 모델 로드 중...")
    _embed_model = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL_NAME,
        model_kwargs={"device": EMBED_DEVICE},
    )

    print("[VectorDB] ChromaDB 연결 중...")
    _vector_store = Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=_embed_model,
        persist_directory=CHROMA_DB_PATH,
    )

    # 리트리버 설정
    _qa_retriever = _vector_store.as_retriever(
        search_kwargs={"filter": {"type": "qa"}}
    )
    _user_retriever = _vector_store.as_retriever(
        search_kwargs={"filter": {"type": "user_data"}, "k": 2}
    )
    _essay_retriever = _vector_store.as_retriever(
        search_kwargs={"filter": {"type": "essay"}, "k": 3}
    )

    # 폰트 등록 (PDF 생성용)
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont("Nanum", FONT_PATH))
    else:
        print(f"[경고] 폰트 파일 없음: {FONT_PATH}")

    print("[초기화 완료]")


# ═════════════════════════════════════════════════════════════════════════════
# PDF 처리
# ═════════════════════════════════════════════════════════════════════════════

def _extract_text_flattened_pdf(pdf_path: str) -> str:
    """
    PDF에서 텍스트를 추출합니다.
    1차: PyPDFLoader (텍스트 레이어가 있는 PDF - 빠르고 정확)
    2차: OCR fallback (스캔본처럼 텍스트 레이어가 없는 경우)
    """
    import shutil

    # 1차: PyPDFLoader로 텍스트 추출 시도
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text = "\n".join(d.page_content for d in docs).strip()
        if len(text) > 100:   # 텍스트가 충분히 추출되면 바로 반환
            print("[PDF] 텍스트 레이어 추출 성공")
            return text
        print("[PDF] 텍스트 레이어 부족 → OCR 시도")
    except Exception as e:
        print(f"[PDF] PyPDFLoader 실패 → OCR 시도: {e}")

    # 2차: OCR fallback
    from pdf2image import convert_from_path
    import pytesseract

    poppler_bin = shutil.which("pdftocairo")
    if poppler_bin:
        poppler_path = os.path.dirname(poppler_bin)
    elif sys.platform == "win32":
        poppler_path = r"C:\Program Files\poppler\Library\bin"
    else:
        poppler_path = "/opt/homebrew/bin/"

    tesseract_bin = shutil.which("tesseract")
    if tesseract_bin:
        pytesseract.pytesseract.tesseract_cmd = tesseract_bin
    elif sys.platform == "win32":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:
        pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

    try:
        print(f"[OCR] Poppler 경로: {poppler_path}")
        pages = convert_from_path(pdf_path, 300, poppler_path=poppler_path)
        full_text = []
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page)
            full_text.append(text)
            print(f"[OCR] Page {i + 1} 처리 완료")
        return "".join(full_text)
    except Exception as e:
        return f"[OCR 오류] {e}"


def validate_user_file(file_path: str) -> str | None:
    """
    PDF 파일 유효성 검사.

    Returns
    -------
    str  : 유효한 파일 경로
    None : 유효하지 않음
    """
    if isinstance(file_path, list):
        if len(file_path) != 1:
            print("파일 개수는 1개만 올려주세요.")
            return None
        file_path = file_path[0]

    if not os.path.exists(file_path):
        print("파일이 존재하지 않습니다.")
        return None

    if not file_path.lower().endswith(".pdf"):
        print("PDF 파일만 업로드 가능합니다.")
        return None

    if os.path.getsize(file_path) > MAX_PDF_SIZE_MB * 1024 * 1024:
        print(f"파일 크기는 {MAX_PDF_SIZE_MB}MB 이하이어야 합니다.")
        return None

    print("파일 검증 완료")
    return file_path


def load_user_pdf(pdf_path: str, doc_type: str = "user_data") -> str:
    """
    PDF 를 벡터DB 에 저장하고, 추출된 텍스트를 반환합니다.

    Parameters
    ----------
    pdf_path : PDF 파일 경로
    doc_type : "user_data" | "essay"
    """
    _check_initialized()
    print(f"[PDF] {doc_type} 처리 중: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    docs   = loader.load()
    final_docs = []

    if doc_type == "essay":
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata = {"source": pdf_path, "type": "essay"}
            final_docs.append(chunk)
        extracted_text = "\n".join(d.page_content for d in docs)
    else:
        extracted_text = _extract_text_flattened_pdf(pdf_path)
        doc = Document(
            page_content=extracted_text,
            metadata={"source": pdf_path, "type": "user_data"},
        )
        final_docs.append(doc)

    _vector_store.add_documents(final_docs)
    print("[PDF] 벡터DB 저장 완료")
    print(f"[PDF] 추출 미리보기:\n{extracted_text[:300]}")  # ← 이 줄만 추가
    return extracted_text


# ═════════════════════════════════════════════════════════════════════════════
# QA 데이터셋 로드
# ═════════════════════════════════════════════════════════════════════════════

# ── 고유명사 정규화 테이블 ─────────────────────────────────────────────────────
_UNIVERSITIES = [
    "Northeastern University", "Tennessee state university", "Imo state university",
    "southeastern louisiana university", "University of Alabama", "Oregon State University",
    "Miami University", "Rice University", "Obafemi Awolowo University", "Vermont Law School",
    "Lousiana State University", "Georgia State University",
    "University of South Carolina Gould",
    "GSU", "TSU", "OSU", "USC", "SLU", "UTA", "Lamar",
]
_MAJORS = [
    "Industrial engineering and Operations research",
    "Advanced Studies in English Language and Digital Humanities",
    "funeral services and mortuary science", "Project Management", "Criminal Justice",
    "Computer Engineering", "Biotechnology", "Microbiology", "Chemistry",
    "Public Health", "Geoscience",
]
_COUNTRIES = [
    "United States of America", "Trinidad and Tobago", "United States", "Ivory Coast",
    "XYZ country", "Nigeria", "Africa", "Ghana", "China", "Turkey", "the US",
]
_LOCATIONS = [
    "Anambra State", "Osun state", "Abidjan", "Portland", "Abeokuta", "Alabama",
    "Osogbo", "Vermont", "Lagos", "Abuja", "Maine", "Ife",
]
_ORGANIZATIONS = [
    "Institute For Agricultural Research",
    "Food and Agricultural Organization of the United Nations",
    "Nigerian center for disease control and prevention",
    "Federal Ministry of Environment", "Nigerian Bar Association",
    "National Youth Service Corps", "Ministry of Environment",
    "MPOWER Financing", "Dakali Ventures", "open dreams",
]
_AMOUNT_PAT = re.compile(
    r'\$[\d,]+(?:\.\d+)?|[\d,]+(?:\.\d+)?\s*USD|[\d,]+(?:\.\d+)?\s*naira'
    r'|[\d,.]+\s*million\s*naira|[\d,]+k',
    re.IGNORECASE,
)
_TOKEN_MAP = {
    "UNIVERSITY"  : _UNIVERSITIES,
    "MAJOR"       : _MAJORS,
    "COUNTRY"     : _COUNTRIES,
    "LOCATION"    : _LOCATIONS,
    "ORGANIZATION": _ORGANIZATIONS,
}


def _build_pattern(terms: list[str]) -> re.Pattern:
    sorted_terms = sorted(terms, key=len, reverse=True)
    escaped = [re.escape(t) for t in sorted_terms]
    return re.compile(r'(?<!\w)(' + "|".join(escaped) + r')(?!\w)', re.IGNORECASE)


def _replace_proper_nouns(text: str) -> str:
    if not isinstance(text, str):
        return text
    for token, terms in _TOKEN_MAP.items():
        text = _build_pattern(terms).sub(token, text)
    text = _AMOUNT_PAT.sub("[AMOUNT]", text)
    return text


def load_qa_dataset() -> None:
    """
    HuggingFace 의 F1 비자 QA 데이터셋을 로드해 전처리 후 벡터DB 에 저장합니다.
    이미 저장된 경우 재호출해도 안전합니다 (중복 저장에 주의).
    """
    _check_initialized()
    print("[Dataset] F1 비자 QA 데이터 로드 중...")

    raw_df = load_dataset("Blessing988/f1_visa_transcripts")
    df = pd.DataFrame(raw_df["train"])[["input", "output"]].copy()
    df["input"]  = df["input"].apply(_replace_proper_nouns)
    df["output"] = df["output"].apply(_replace_proper_nouns)

    qa_docs = [
        Document(
            page_content=row["input"],
            metadata={"answer": row["output"], "source": "f1_visa_interview_qna", "type": "qa"},
        )
        for _, row in df.iterrows()
    ]

    _vector_store.add_documents(qa_docs)
    print(f"[Dataset] {len(qa_docs)}개 QA 문서 저장 완료")


# ═════════════════════════════════════════════════════════════════════════════
# LLM 호출
# ═════════════════════════════════════════════════════════════════════════════

def get_question(profile_context: str, history: list[dict], used_refs: set[str] | None = None) -> str:
    """
    인터뷰 질문을 LLM 으로 생성합니다.

    Parameters
    ----------
    profile_context : 사용자 I-20 텍스트
    history         : [{"question": ..., "answer": ...}, ...]

    Returns
    -------
    str : 생성된 질문 1문장
    """
    _check_initialized()

    if used_refs is None:
        used_refs = set()

    q_ref_docs = _qa_retriever.invoke("F1 visa interview")
    unused = [d for d in q_ref_docs if d.page_content not in used_refs]
    doc = random.choice(unused) if unused else random.choice(q_ref_docs)
    q_ref = doc.page_content
    used_refs.add(q_ref)

    history_text = "".join(
        f"Q: {h['question']}\nA: {h['answer']}\n" for h in history
    )

    prompt = f"""
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

    res = _llm.invoke(prompt)
    return res.content.strip() if hasattr(res, "content") else str(res).strip()


def get_final_evaluation(profile_context: str, history: list[dict]) -> str:
    """
    인터뷰 전체 히스토리를 기반으로 최종 평가를 LLM 으로 생성합니다.

    Returns
    -------
    str : 최종 평가 텍스트 (한국어)
    """
    _check_initialized()

    a_ref_docs = _qa_retriever.invoke("Suggested answers")
    a_ref      = random.choice(a_ref_docs).metadata.get("answer", "")

    history_text = "".join(
        f"Q{i}: {h['question']}\nA{i}: {h['answer']}\n"
        for i, h in enumerate(history, 1)
    )

    prompt = f"""
You are a US F1 visa officer.

지원자 정보:
{profile_context}

참고 답변:
{a_ref}

이전 인터뷰:
{history_text}

[핵심 규칙]

- 평가 시 한국어로 출력합니다.

[평가 기준]

1. 사용자의 답변이 지원자 정보와 일치하는 내용인가를 평가하세요.
2. 사용자의 답변이 논리성이 있는지 평가하세요.
3. 사용자의 답변이 문법적으로 오류가 없는지 평가하세요.
4. 사용자의 답변이 영어로 표현되었는지 평가하세요.
5. 참고 답변과 비교하여 지원자의 답변이 인터뷰 질문에 적절히 답변했는지 평가하세요. 
# 6. 음성 분석에 기반하여 지원자의 자신감과 유창성을 평가하세요. 
#     - 말 속도가 너무 느리거나 빠르지 않은지 평가하세요. 
#     - pause 비율이 낮을수록 유창성이 높다고 평가하세요. 
#     - filler 사용이 적을수록 자신감이 높다고 평가하세요.

Output:

최종 결과: 비자 승인 또는 비자 거절
    - 실제 f1 비자 인터뷰의 결과에 맞게 "비자 승인" 또는 "비자 거절"로 출력하세요.
전반적인 피드백:
    - 한국어 한 문단으로 지원자의 잘한 점과 개선할 점을 평가하세요.

개선사항:
    - 구체적으로 무엇이 부족했는지 설명하세요.    
    - 사용자의 대답마다 1~2문장으로 평가하세요.
    - 참고 답변을 기반으로 추천 답변을 영어 답변으로 제공하세요.
"""

    res = _llm.invoke(prompt)
    return res.content.strip() if hasattr(res, "content") else str(res).strip()


# ═════════════════════════════════════════════════════════════════════════════
# 피드백 PDF 저장
# ═════════════════════════════════════════════════════════════════════════════

def _clean_text(text: str) -> str:
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'#', '', text)
    return text


def save_feedback_pdf(feedback_text: str, filename: str | None = None) -> str:
    """
    피드백 텍스트를 PDF 로 저장합니다.

    Parameters
    ----------
    feedback_text : 저장할 텍스트
    filename      : 저장 파일명 (None 이면 타임스탬프 기반 자동 생성)

    Returns
    -------
    str : 저장된 파일 경로
    """
    if filename is None:
        filename = f"interview_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc    = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "Nanum"
    styles["Title"].fontName  = "Nanum"

    story = [
        Paragraph("F1 Visa Interview Result", styles["Title"]),
        Spacer(1, 20),
    ]

    cleaned = _clean_text(feedback_text)
    for line in cleaned.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    print(f"PDF 저장 완료: {filename}")
    return filename


# ═════════════════════════════════════════════════════════════════════════════
# 내부 헬퍼
# ═════════════════════════════════════════════════════════════════════════════

def _check_initialized() -> None:
    if _llm is None:
        raise RuntimeError("setup() 을 먼저 호출하세요.")
