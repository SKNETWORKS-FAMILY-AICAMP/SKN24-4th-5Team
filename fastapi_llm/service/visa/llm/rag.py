import random
import re
from functools import lru_cache

from fastapi_llm.service.visa.config.settings import settings


# HuggingFace F1 visa transcript
class VisaRAGStore:
    def __init__(self):
        self.vector_store = self._load_vector_store()
        self._ensure_qa_documents()
        self.retriever = self.vector_store.as_retriever(search_kwargs={"filter": {"type": "qa"}, "k": 6})

    # embedding 紐⑤뜽怨?Chroma ??μ냼瑜?濡쒕뱶?⑸땲??
    def _load_vector_store(self):
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        embed_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
        return Chroma(
            collection_name=settings.CHROMA_COLLECTION,
            embedding_function=embed_model,
            persist_directory=str(settings.CHROMA_DIR),
        )


    def _ensure_qa_documents(self) -> None:
        if self.vector_store._collection.count() > 0:
            return

        import pandas as pd
        from datasets import load_dataset
        from langchain_core.documents import Document

        dataset = load_dataset(settings.HF_VISA_DATASET)
        df = pd.DataFrame(dataset["train"])[["input", "output"]].copy()
        df["input"] = df["input"].apply(replace_proper_nouns)
        df["output"] = df["output"].apply(replace_proper_nouns)

        qa_docs = [
            Document(
                page_content=row["input"],
                metadata={"answer": row["output"], "source": "f1_visa_transcripts", "type": "qa"},
            )
            for _, row in df.iterrows()
        ]
        self.vector_store.add_documents(qa_docs)

    def get_reference_question(self, query: str = "F1 visa interview question") -> str:
        docs = self.retriever.invoke(query)
        if not docs:
            return "Why did you choose this university?"
        return random.choice(docs).page_content

    def get_reference_answer(self, query: str = "suggested answers F1 visa") -> str:
        docs = self.retriever.invoke(query)
        if not docs:
            return ""
        return random.choice(docs).metadata.get("answer", "")


def replace_proper_nouns(text: str) -> str:
    if not isinstance(text, str):
        return text
    for token, pattern in _patterns().items():
        text = pattern.sub(token, text)
    return _amount_pattern().sub("[AMOUNT]", text)


@lru_cache(maxsize=1)
def get_visa_rag_store() -> VisaRAGStore:
    return VisaRAGStore()


@lru_cache(maxsize=1)
def _patterns() -> dict[str, re.Pattern]:
    token_map = {
        "[UNIVERSITY]": [
            "Northeastern University",
            "Tennessee state university",
            "Imo state university",
            "southeastern louisiana university",
            "University of Alabama",
            "Oregon State University",
            "Miami University",
            "Rice University",
            "Obafemi Awolowo University",
            "Vermont Law School",
            "Lousiana State University",
            "Georgia State University",
            "University of South Carolina Gould",
            "GSU",
            "TSU",
            "OSU",
            "USC",
            "SLU",
            "UTA",
            "Lamar",
        ],
        "[MAJOR]": [
            "Industrial engineering and Operations research",
            "Advanced Studies in English Language and Digital Humanities",
            "funeral services and mortuary science",
            "Project Management",
            "Criminal Justice",
            "Computer Engineering",
            "Biotechnology",
            "Microbiology",
            "Chemistry",
            "Public Health",
            "Geoscience",
        ],
        "[COUNTRY]": [
            "United States of America",
            "Trinidad and Tobago",
            "United States",
            "Ivory Coast",
            "XYZ country",
            "Nigeria",
            "Africa",
            "Ghana",
            "China",
            "Turkey",
            "the US",
        ],
        "[LOCATION]": [
            "Anambra State",
            "Osun state",
            "Abidjan",
            "Portland",
            "Abeokuta",
            "Alabama",
            "Osogbo",
            "Vermont",
            "Lagos",
            "Abuja",
            "Maine",
            "Ife",
        ],
        "[ORGANIZATION]": [
            "Institute For Agricultural Research",
            "Food and Agricultural Organization of the United Nations",
            "Nigerian center for disease control and prevention",
            "Federal Ministry of Environment",
            "Nigerian Bar Association",
            "National Youth Service Corps",
            "Ministry of Environment",
            "MPOWER Financing",
            "Dakali Ventures",
            "open dreams",
        ],
    }
    return {token: _build_pattern(terms) for token, terms in token_map.items()}


@lru_cache(maxsize=1)
def _amount_pattern() -> re.Pattern:
    return re.compile(
        r"\$[\d,]+(?:\.\d+)?|[\d,]+(?:\.\d+)?\s*USD"
        r"|[\d,]+(?:\.\d+)?\s*naira|[\d,.]+\s*million\s*naira|[\d,]+k",
        re.IGNORECASE,
    )


def _build_pattern(terms: list[str]) -> re.Pattern:
    escaped = [re.escape(term) for term in sorted(terms, key=len, reverse=True)]
    return re.compile(r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)", re.IGNORECASE)

