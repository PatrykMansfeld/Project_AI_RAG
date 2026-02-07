import os
import json
import re
from typing import List, Iterable

STOPWORDS = {
    "i", "oraz", "lub", "albo", "a", "w", "we", "z", "za", "do", "na", "o", "u", "od", "po", "pod", "nad", "przez", "dla", "to", "jest", "są", "być", "się", "że", "czy", "jak", "co", "kiedy", "który", "która", "które", "tego", "tej", "tych", "ten", "ta", "tam", "tu", "tutaj", "oraz", "ale", "bardziej", "mniej", "jako", "jego", "jej", "ich", "swoje", "swoja", "swoje", "swoich", "ma", "mieć", "mamy", "mają", "może", "mogą"
}


def word_tokenize(text: str) -> List[str]:
    # Prosta tokenizacja słów.
    return [t.lower() for t in re.findall(r"\b\w+\b", text)]


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    # Dzieli tekst na zachodzące chunki.
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


def slugify(text: str) -> str:
    # Bezpieczny identyfikator z tematu.
    s = re.sub(r"\s+", "-", text.strip().lower())
    s = re.sub(r"[^a-z0-9\-]", "", s)
    return s or "article"


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    # Proste wyłuskanie top słów kluczowych.
    tokens = word_tokenize(text)
    filtered = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    if not filtered:
        return []
    from collections import Counter
    cnt = Counter(filtered)
    return [w for w, _ in cnt.most_common(top_n)]


def append_qa_log(path: str, question: str, expected_keywords: Iterable[str], expected_answer: str) -> None:
    # Dopisuje linię QA do pliku JSONL.
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entry = {
        "question": question,
        "expected_keywords": list(expected_keywords),
        "expected_answer": expected_answer,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
