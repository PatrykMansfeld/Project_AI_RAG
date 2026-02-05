import json
from typing import Any, Dict, List

import ollama

from .config import Config
from .rag_core import SimpleRAG


def _keyword_metrics(answer: str, keywords: List[str]) -> Dict[str, float]:
    ans_low = answer.lower()
    found = [k for k in keywords if k.lower() in ans_low]
    prec = len(found) / len(keywords) if keywords else 0.0
    rec = prec  # dla prostego matchingu dokładność=pełnia
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return {"precision": prec, "recall": rec, "f1": f1}


def _llm_judge(cfg: Config, question: str, expected: List[str], answer: str) -> float:
    client = ollama.Client(host=cfg.ollama_host)
    kw_str = ", ".join(expected) if expected else "(brak)"
    prompt = (
        "Oceń odpowiedź na pytanie. Zwróć jedynie liczbę 0-1 (1=dobrze, 0=źle).\n"
        f"Pytanie: {question}\n"
        f"Oczekiwane słowa kluczowe: {kw_str}\n"
        f"Odpowiedź: {answer}\n"
        "Jeśli odpowiedź jest zgodna merytorycznie i zawiera oczekiwane informacje, zwróć 1, inaczej 0."
    )
    res = client.chat(model=cfg.judge_model, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.0})
    content = res.get("message", {}).get("content", "0")
    try:
        score = float(content.strip().split()[0])
        return 1.0 if score >= 0.5 else 0.0
    except Exception:
        return 0.0


def evaluate(cfg: Config, qa_path: str) -> Dict[str, Any]:
    rag = SimpleRAG(cfg)
    rag.build()
    items: List[Dict[str, Any]] = []
    with open(qa_path, "r", encoding="utf-8") as f:
        for line in f:
            items.append(json.loads(line))
    total = len(items)
    agg_correct = 0
    agg_judge = 0.0
    results: List[Dict[str, Any]] = []
    for it in items:
        q = it["question"]
        kw = it.get("expected_keywords", [])
        res = rag.answer(q)
        ans = res["answer"]
        km = _keyword_metrics(ans, kw)
        ok = km["f1"] >= 1.0 if kw else True
        agg_correct += int(ok)

        judge_score = None
        if cfg.eval_use_judge:
            judge_score = _llm_judge(cfg, q, kw, ans)
            agg_judge += judge_score

        results.append({
            "question": q,
            "keywords": kw,
            "answer": ans,
            "keywords_precision": km["precision"],
            "keywords_recall": km["recall"],
            "keywords_f1": km["f1"],
            "judge_score": judge_score,
        })

    keyword_acc = agg_correct / total if total else 0.0
    judge_acc = (agg_judge / total) if (total and cfg.eval_use_judge) else None
    return {
        "count": total,
        "keyword_accuracy": keyword_acc,
        "judge_accuracy": judge_acc,
        "results": results,
    }
    # Rozszerzona ewaluacja: metryki słów kluczowych + opcjonalny LLM-judge
