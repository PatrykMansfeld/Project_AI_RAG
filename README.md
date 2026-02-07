# RAG Chatbot (Ollama, Python)

Minimalny chatbot RAG na lokalnym Ollama. Zapewnia cytowanie źródeł, CLI oraz prosty frontend WWW (Flask).

## Najważniejsze funkcje

- Indeksuje pliki `.txt`/`.md` z `data/docs` (chunkowanie + embeddingi Ollama).
- Retrieval: semantyczny (embeddingi, domyślnie) lub leksykalny (BM25).
- Generuje odpowiedź ograniczoną do kontekstu i cytuje źródła `[source: ścieżka#chunk-id]`.
- Ma analizę korpusu i prostą ewaluację dokładności.
- Generuje artykuły Markdown do `data/docs/gen`.
- Udostępnia endpointy API i UI WWW.

## Wymagania

- Windows (CMD) lub PowerShell
- Python 3.10+
- Zainstalowane Ollama: https://ollama.com/
- Modele (jednorazowo): `ollama pull llama3.1`, `ollama pull nomic-embed-text`

## Szybki start (CMD/PowerShell)

1) Środowisko i zależności

```bat
python -m venv .venv
\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

2) Modele Ollama (raz)

```batna
ollama pull llama3.1
ollama pull nomic-embed-text
```

3) Indeks + chat (CLI)

```bat
python src\main.py index
python src\main.py chat
```

4) Frontend WWW (opcjonalnie)

```bat
python src\web_app.py
```

Otwórz: http://localhost:5000

## Dodatkowe scenariusze

### BM25 zamiast embeddingów

```bat
set RETRIEVAL_METHOD=bm25
python src\main.py chat
```

### Generowanie artykułów do korpusu

```bat
python src\main.py generate --topic "Sieci neuronowe" --count 2 --min_words 600 --style "encyklopedyczny"
python src\main.py index
```

### Analiza i ewaluacja

```bat
python src\main.py analyze
python src\main.py eval --qa data\eval\qa.jsonl --out data\eval\report.json --use-judge
```

Format `qa.jsonl`:

```json
{ "question": "...", "expected_keywords": ["..."], "expected_answer": "opcjonalna pełna odpowiedź referencyjna" }
```

Zakończenie środowiska:

```bat
deactivate
```

## Komendy (CLI i WWW)

- `python src\main.py index` — buduje indeks (chunkowanie + embeddingi, opcjonalnie BM25).
- `python src\main.py chat` — czat w konsoli (odpowiedzi z cytowaniem źródeł).
- `python src\main.py analyze` — statystyki korpusu (liczba dokumentów, tokeny, top termy).
- `python src\main.py eval --qa data\eval\qa.jsonl` — ewaluacja dokładności na zestawie QA.
- `python src\main.py generate --topic "..." --count N --min_words M --style "..."` — generuje artykuły do `data/docs/gen`.
- `python src\web_app.py` — frontend WWW pod `http://localhost:5000`.

## Konfiguracja (zmienne środowiskowe)

- `OLLAMA_HOST` (domyślnie `http://localhost:11434`)
- `LLM_MODEL` (domyślnie `llama3.1`)
- `EMBEDDING_MODEL` (domyślnie `nomic-embed-text`)
- `SYSTEM_PROMPT_MODE` = `strict` | `friendly` | `concise`
- `GUARDRAILS` = `true` | `false`
- `RETRIEVAL_METHOD` = `embedding` | `bm25` (wymaga `rank-bm25`)
- `TOP_K`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `SCORE_THRESHOLD`, `FEW_SHOT`, `TEMPERATURE`
- `EVAL_USE_JUDGE` = `true` | `false`
- `JUDGE_MODEL` (domyślnie taki jak `LLM_MODEL`)
- `AUTO_LOG_QA` = `true` | `false` (domyślnie `false`)
- `QA_LOG_PATH` (domyślnie `data/eval/qa_log.jsonl`)

## Struktura projektu

- `src/main.py` — CLI (index, chat, analyze, eval, generate)
- `src/web_app.py` — serwer Flask + frontend
- `src/rag/` — logika RAG:
	- `config.py`, `utils.py`, `embeddings.py`, `vector_store.py`, `prompts.py`
	- `rag_core.py`, `analysis.py`, `evaluator.py`, `generate.py`
- `data/docs` — dokumenty źródłowe
- `data/docs/gen` — wygenerowane artykuły
- `data/eval/qa.jsonl` — zestaw ewaluacyjny
- `requirements.txt` — zależności

## Notatki

- Dokumenty trzymaj w `data/docs` (generowane trafiają do `data/docs/gen`).
- Jeśli brakuje trafień, zwiększ `TOP_K` lub zmniejsz `SCORE_THRESHOLD`.
- BM25 lepiej radzi sobie z dopasowaniem słów, embeddingi z podobieństwem semantycznym.
