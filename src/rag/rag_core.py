import os
from typing import Any, Dict, List, Optional, Tuple

import ollama
import numpy as np

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except Exception:
    HAS_BM25 = False
# BM25 opcjonalnie, inaczej wektory

from .config import Config
from .embeddings import EmbeddingClient
from .vector_store import VectorStore
from .utils import word_tokenize, chunk_text
from .prompts import system_prompt, few_shot, user_prompt


class SimpleRAG:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.embed = EmbeddingClient(cfg.embedding_model, host=cfg.ollama_host)
        self.vs = VectorStore()
        self.corpus_meta: List[Dict[str, Any]] = []
        self.bm25 = None
        # Inicjalizacja klientów i pamięci

    def load_and_chunk(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        texts: List[str] = []
        metas: List[Dict[str, Any]] = []
        for dirpath, _, filenames in os.walk(self.cfg.data_dir):
            for fn in filenames:
                if not fn.lower().endswith((".txt", ".md")):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        raw = f.read()
                    chunks = chunk_text(raw, self.cfg.chunk_size, self.cfg.chunk_overlap)
                    for i, ch in enumerate(chunks):
                        texts.append(ch)
                        metas.append({"source": path, "chunk_id": i, "text": ch})
                except Exception as e:
                    print(f"[loader] Nie udało się wczytać {path}: {e}")
        return texts, metas
        # Ładuje pliki i dzieli na chunki

    def build(self):
        chunk_texts, metas = self.load_and_chunk()
        if not chunk_texts:
            print("[index] Brak dokumentów do zindeksowania.")
            return
        vecs = self.embed.embed_texts(chunk_texts)
        self.vs.add(vecs, metas)
        self.corpus_meta = metas
        if self.cfg.retrieval_method == "bm25" and HAS_BM25:
            token_docs = [word_tokenize(m["text"]) for m in metas]
            self.bm25 = BM25Okapi(token_docs)
        print(f"[index] Zindeksowano {len(metas)} chunków.")
        # Buduje indeks wektorowy/BM25

    def retrieve(self, question: str) -> List[Dict[str, Any]]:
        if self.cfg.retrieval_method == "bm25" and self.bm25 is not None:
            scores = self.bm25.get_scores(word_tokenize(question))
            ranked = sorted(
                [{"meta": m, "score": float(s)} for m, s in zip(self.corpus_meta, scores)],
                key=lambda x: x["score"],
                reverse=True,
            )
            return [r["meta"] for r in ranked[: self.cfg.top_k]]
        # Embedding
        qv = self.embed.embed_query(question)
        ranked = self.vs.search(qv, top_k=self.cfg.top_k)
        return [m for (m, s) in ranked if s >= self.cfg.score_threshold]
        # Zwraca najlepsze konteksty

    def answer(self, question: str) -> Dict[str, Any]:
        ctx = self.retrieve(question)
        client = ollama.Client(host=self.cfg.ollama_host)
        messages = [{"role": "system", "content": system_prompt()}]
        if self.cfg.few_shot:
            messages.extend(few_shot())
        messages.append({"role": "user", "content": user_prompt(question, ctx)})
        res = client.chat(model=self.cfg.llm_model, messages=messages, options={"temperature": self.cfg.temperature})
        ans = res["message"]["content"]  # type: ignore[index]
        return {"answer": ans, "sources": ctx}
        # Buduje prompt i zwraca odpowiedź
