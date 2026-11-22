import re
import unicodedata

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text or "")).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_paragraphs(text: str, min_chars: int = 35):
    raw = str(text or "").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n|\n(?=\[Page\s+\d+\])", raw)
    cleaned = []
    for block in blocks:
        block = re.sub(r"\[Page\s+\d+\]", "", block).strip()
        block = re.sub(r"\s+", " ", block)
        if len(block) >= min_chars:
            cleaned.append(block)
    # PDF extraction may flatten paragraph spacing. Group sentences as a fallback.
    if len(cleaned) <= 1 and len(raw) > 900:
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ0-9])", re.sub(r"\s+", " ", raw))
        grouped, current = [], []
        for sentence in sentences:
            if sentence.strip():
                current.append(sentence.strip())
            if len(" ".join(current)) >= 220:
                grouped.append(" ".join(current))
                current = []
        if current:
            grouped.append(" ".join(current))
        if grouped:
            cleaned = [x for x in grouped if len(x) >= min_chars]
    if not cleaned and len(raw.strip()) >= min_chars:
        cleaned = [re.sub(r"\s+", " ", raw).strip()]
    return cleaned
