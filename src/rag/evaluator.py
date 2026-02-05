import json
from typing import Any, Dict, List, Optional

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


def _llm_judge(cfg: Config, question: str, expected_answer: Optional[str], expected_keywords: List[str], answer: str) -> float:
    client = ollama.Client(host=cfg.ollama_host)
    kw_str = ", ".join(expected_keywords) if expected_keywords else "(brak)"
    ref = expected_answer or "(brak pełnej odpowiedzi referencyjnej)"
    prompt = (
        "Oceń odpowiedź na pytanie. Zwróć jedynie liczbę 0-1 (1=poprawne, 0=niepoprawne).\n"
        "Kryteria: zgodność merytoryczna z odpowiedzią referencyjną, pokrycie kluczowych informacji, brak halucynacji.\n"
        f"Pytanie: {question}\n"
        f"Odpowiedź referencyjna: {ref}\n"
        f"Oczekiwane słowa kluczowe: {kw_str}\n"
        f"Odpowiedź modelu: {answer}\n"
        "Zwróć tylko 1 lub 0."
    )
    res = client.chat(model=cfg.judge_model, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.0})
    content = res.get("message", {}).get("content", "0")
    try:
        score = float(content.strip().split()[0])
        return 1.0 if score >= 0.5 else 0.0
    except Exception:
        return 0.0


def evaluate(cfg: Config, qa_path: str, out_path: Optional[str] = None) -> Dict[str, Any]:
    rag = SimpleRAG(cfg)
    rag.build()
    items: List[Dict[str, Any]] = []
    with open(qa_path, "r", encoding="utf-8") as f:
        for line in f:
            items.append(json.loads(line))
    total = len(items)
    agg_keyword = 0
    agg_judge = 0.0
    judged = 0
    results: List[Dict[str, Any]] = []
    for it in items:
        q = it["question"]
        kw = it.get("expected_keywords", [])
        expected_answer = it.get("expected_answer")
        res = rag.answer(q)
        ans = res["answer"]
        km = _keyword_metrics(ans, kw)
        ok = km["f1"] >= 1.0 if kw else True
        agg_keyword += int(ok)

        judge_score = None
        if cfg.eval_use_judge:
            judge_score = _llm_judge(cfg, q, expected_answer, kw, ans)
            agg_judge += judge_score
            judged += 1

        results.append({
            "question": q,
            "keywords": kw,
            "expected_answer": expected_answer,
            "answer": ans,
            "keywords_precision": km["precision"],
            "keywords_recall": km["recall"],
            "keywords_f1": km["f1"],
            "judge_score": judge_score,
        })

    keyword_acc = agg_keyword / total if total else 0.0
    judge_acc = (agg_judge / judged) if (judged and cfg.eval_use_judge) else None
    summary = {
        "count": total,
        "keyword_accuracy": keyword_acc,
        "judge_accuracy": judge_acc,
        "results": results,
    }

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary
    # Rozszerzona ewaluacja: metryki słów kluczowych + opcjonalny LLM-judge + zapis raportu
