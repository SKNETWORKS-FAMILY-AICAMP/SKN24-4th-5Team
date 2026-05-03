from difflib import SequenceMatcher


_GRAMMAR_MODEL = None
_GRAMMAR_TOKENIZER = None
_MODEL_NAME = "vennify/t5-base-grammar-correction"


# Score English grammar by comparing the answer with a corrected version.
def evaluate_grammar(text: str) -> dict:
    cleaned_text = " ".join((text or "").split())
    if not cleaned_text:
        return {
            "grammar_score_25": 0,
            "grammar_error_ratio": 1.0,
            "grammar_corrected_text": "",
        }

    corrected_text = _correct_grammar(cleaned_text)
    similarity = SequenceMatcher(None, cleaned_text.lower(), corrected_text.lower()).ratio()
    error_ratio = max(0.0, min(1.0, 1.0 - similarity))
    grammar_score = _score_grammar(error_ratio, len(cleaned_text.split()))

    return {
        "grammar_score_25": grammar_score,
        "grammar_error_ratio": round(error_ratio, 3),
        "grammar_corrected_text": corrected_text,
    }


# Run a Python-only Hugging Face grammar correction model.
def _correct_grammar(text: str) -> str:
    global _GRAMMAR_MODEL, _GRAMMAR_TOKENIZER

    if _GRAMMAR_MODEL is None or _GRAMMAR_TOKENIZER is None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        _GRAMMAR_TOKENIZER = AutoTokenizer.from_pretrained(_MODEL_NAME)
        _GRAMMAR_MODEL = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)

    inputs = _GRAMMAR_TOKENIZER(
        f"grammar: {text}",
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )
    outputs = _GRAMMAR_MODEL.generate(
        **inputs,
        max_length=256,
        num_beams=4,
        early_stopping=True,
    )
    corrected = _GRAMMAR_TOKENIZER.decode(outputs[0], skip_special_tokens=True)
    return corrected.strip() or text


# Convert correction difference into a 25-point grammar score.
def _score_grammar(error_ratio: float, word_count: int) -> int:
    if word_count < 3:
        return 5
    if error_ratio <= 0.03:
        return 25
    if error_ratio <= 0.08:
        return 20
    if error_ratio <= 0.15:
        return 15
    if error_ratio <= 0.25:
        return 10
    return 5
