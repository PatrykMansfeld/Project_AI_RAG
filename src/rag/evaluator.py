import json
from typing import Any, Dict, List

from .config import Config
from .rag_core import SimpleRAG


def evaluate(cfg: Config, qa_path: str) -> Dict[str, Any]:
    rag = SimpleRAG(cfg)
    rag.build()
    items: List[Dict[str, Any]] = []
    with open(qa_path, "r", encoding="utf-8") as f:
        for line in f:
            items.append(json.loads(line))
    total = len(items)
    correct = 0
    results: List[Dict[str, Any]] = []
    for it in items:
        q = it["question"]
        kw = it.get("expected_keywords", [])
        res = rag.answer(q)
        ans = res["answer"].lower()
        ok = all(k.lower() in ans for k in kw)
        correct += int(ok)
        results.append({"question": q, "ok": ok, "keywords": kw})
    acc = correct / total if total else 0.0
    return {"accuracy": acc, "count": total, "results": results}
    # Liczy dokładność na zbiorze QA
