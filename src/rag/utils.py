import re
from typing import List


def word_tokenize(text: str) -> List[str]:
    return [t.lower() for t in re.findall(r"\b\w+\b", text)]
    # Prosta tokenizacja słów


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    tokens = word_tokenize(text)
    if chunk_size <= 0:
        return [text]
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))
        if end == len(tokens):
            break
        start = max(0, end - chunk_overlap)
    return chunks
    # Dzieli tekst na zachodzące chunki


def slugify(text: str) -> str:
    s = re.sub(r"\s+", "-", text.strip().lower())
    s = re.sub(r"[^a-z0-9\-]", "", s)
    return s or "article"
    # Bezpieczny identyfikator z tematu
