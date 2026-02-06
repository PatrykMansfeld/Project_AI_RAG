import os
from dataclasses import dataclass

@dataclass
class Config:
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.1")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    system_prompt_mode: str = os.getenv("SYSTEM_PROMPT_MODE", "strict")  # strict|friendly|concise
    guardrails_enabled: bool = os.getenv("GUARDRAILS", "true").lower() == "true"
    # Wybór wariantu promptu oraz włączenie prostych guardrails

    eval_use_judge: bool = os.getenv("EVAL_USE_JUDGE", "true").lower() == "true"
    judge_model: str = os.getenv("JUDGE_MODEL", llm_model)
    # Parametry ewaluacji LLM-judge

    data_dir: str = os.getenv("DATA_DIR", "data/docs")
    top_k: int = int(os.getenv("TOP_K", "5"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    score_threshold: float = float(os.getenv("SCORE_THRESHOLD", "0.25"))
    retrieval_method: str = os.getenv("RETRIEVAL_METHOD", "embedding")  # embedding|bm25

    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    few_shot: bool = os.getenv("FEW_SHOT", "true").lower() == "true"
    # Parametry aplikacji z ENV

    auto_log_qa: bool = os.getenv("AUTO_LOG_QA", "false").lower() == "true"
    qa_log_path: str = os.getenv("QA_LOG_PATH", "data/eval/qa_log.jsonl")
    # Automatyczny zapis rozmów do pliku QA (jsonl)
