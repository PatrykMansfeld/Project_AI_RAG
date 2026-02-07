import os
from collections import Counter
from typing import Any, Dict, List

from .config import Config
from .utils import word_tokenize


def analyze_corpus(cfg: Config) -> Dict[str, Any]:
    docs: List[Dict[str, Any]] = []
    tokens: List[str] = []
    total_chars = 0
    # Przechodzi po plikach .txt/.md i zbiera statystyki tekstu.
    for dirpath, _, filenames in os.walk(cfg.data_dir):
        for fn in filenames:
            if not fn.lower().endswith((".txt", ".md")):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            docs.append({"id": path})
            total_chars += len(txt)
            tokens.extend(word_tokenize(txt))
    cnt = Counter(tokens)
    # Zwraca podstawowe statystyki korpusu.
    return {
        "total_docs": len(docs),
        "total_chars": total_chars,
        "total_tokens": len(tokens),
        "vocab_size": len(cnt),
        "top_terms": cnt.most_common(25),
    }
