# RAG Chatbot (Ollama, Python)

Minimalny chatbot RAG z lokalnym Ollama, cytuje źródła i ma prosty interfejs CLI oraz opcjonalny frontend WWW.

## Co Dokładnie Robi Ten Projekt

- Ładuje dokumenty `.txt`/`.md` z folderu `data/docs`, tnie je na chunki i wektoryzuje (embeddingi Ollama).
- Dopasowuje kontekst do pytania: semantycznie (embeddingi, domyślnie) lub leksykalnie (BM25, opcjonalnie).
- Buduje prompt z wybranymi fragmentami i **cytuje źródła** w formacie `[source: ścieżka#chunk-id]`.
- Generuje odpowiedź LLM (domyślnie `llama3.1`), ograniczając się do kontekstu.
- Oferuje analizę korpusu (`analyze`) i prostą ewaluację dokładności (`eval`).
- Potrafi generować artykuły Markdown (`generate`) i zapisywać je do `data/docs/gen`.
- Ma prosty frontend WWW (Flask) do zadawania pytań i przebudowy indeksu.

## Wymagania

- Windows (CMD) lub PowerShell
- Python 3.10+
- Ollama zainstalowane lokalnie: https://ollama.com/
- Modele (jednorazowo): `ollama pull llama3.1`, `ollama pull nomic-embed-text`

## Windows CMD: Krok po Kroku

1) Utwórz i aktywuj środowisko wirtualne, zainstaluj zależności

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

2) Skonfiguruj Ollama i pobierz modele (raz):

```bat
set OLLAMA_HOST=http://localhost:11434
ollama pull llama3.1
ollama pull nomic-embed-text
```

3) Zindeksuj dokumenty i uruchom czat (CLI):

```bat
python src\main.py index
python src\main.py chat
```

Opcjonalnie: uruchom frontend WWW (Flask):

```bat
python src\web_app.py
```

Otwórz przeglądarkę: http://localhost:5000

4) (Opcja) Przełącz dopasowanie na BM25 (leksykalne):

```bat
set RETRIEVAL_METHOD=bm25
python src\main.py chat
```

5) (Opcja) Generuj artykuły do korpusu:

```bat
python src\main.py generate --topic "Sieci neuronowe" --count 2 --min_words 600 --style "encyklopedyczny"
python src\main.py index
```

6) (Opcja) Analiza i ewaluacja:

```bat
python src\main.py analyze
python src\main.py eval --qa data\eval\qa.jsonl
```

Aby zakończyć środowisko:

```bat
deactivate
```

## Wszystkie Komendy (CLI i WWW)

- `python src\main.py index`: buduje indeks (chunkowanie + embeddingi, opcjonalnie BM25).
- `python src\main.py chat`: uruchamia tryb czatu w konsoli (odpowiedzi z cytowaniem źródeł).
- `python src\main.py analyze`: wypisuje statystyki korpusu (liczba dokumentów, tokenów, top termy).
- `python src\main.py eval --qa data\eval\qa.jsonl`: uruchamia prostą ewaluację dokładności na zestawie QA.
- `python src\main.py generate --topic "..." --count N --min_words M --style "..."`: generuje artykuły Markdown i zapisuje do `data/docs/gen`.
- `python src\web_app.py`: startuje frontend WWW pod `http://localhost:5000`.

## Konfiguracja (zmienne środowiskowe)

- `OLLAMA_HOST` (domyślnie `http://localhost:11434`)
- `LLM_MODEL` (domyślnie `llama3.1`)
- `EMBEDDING_MODEL` (domyślnie `nomic-embed-text`)
- `RETRIEVAL_METHOD` = `embedding` | `bm25` (wymaga `rank-bm25`)
- `TOP_K`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `SCORE_THRESHOLD`, `FEW_SHOT`, `TEMPERATURE`

## Struktura Projektu

- `src/main.py` — CLI (index, chat, analyze, eval, generate)
- `src/web_app.py` — prosty serwer Flask + frontend
- `src/rag/` — moduły logiki:
	- `config.py`, `utils.py`, `embeddings.py`, `vector_store.py`, `prompts.py`
	- `rag_core.py` (RAG), `analysis.py`, `evaluator.py`, `generate.py`
- `data/docs` — Twoje dokumenty
- `data/eval/qa.jsonl` — zestaw ewaluacyjny
- `requirements.txt` — zależności

## Co robi każdy ważny plik

- `src/main.py` — CLI; obsługa komend: budowa indeksu, czat, analiza, ewaluacja, generowanie artykułów.
- `src/web_app.py` — serwer Flask; endpointy API (`/api/chat`, `/api/index`, `/api/analyze`, `/api/eval`, `/api/generate`) oraz statyczny frontend.
- `src/rag/config.py` — konfiguracja aplikacji przez zmienne środowiskowe (modele, parametry chunkowania i retrievalu).
- `src/rag/utils.py` — pomocnicze funkcje: tokenizacja, chunkowanie tekstu, slugify itp.
- `src/rag/embeddings.py` — klient do generowania embeddingów przez Ollama.
- `src/rag/vector_store.py` — prosty magazyn wektorowy + wyszukiwanie NN (cosine).
- `src/rag/prompts.py` — definicje promptow: systemowy, few-shot, prompt usera; szablon do generowania artykulow.
- `src/rag/rag_core.py` — glowna logika RAG: ladowanie dokumentow, indeksowanie, retrieval, budowa promptu i odpowiedzi.
- `src/rag/analysis.py` — statystyki korpusu (liczba dokumentow, tokeny, top termy).
- `src/rag/evaluator.py` — prosta ewaluacja odpowiedzi na podstawie zbioru QA.
- `src/rag/generate.py` — generowanie artykulow Markdown do korpusu.
- `data/docs/` — katalog z dokumentami zrodlowymi i generowanymi artykulami.
- `data/eval/qa.jsonl` — zestaw pytan/oczekiwanych slow kluczowych do ewaluacji.
- `web/index.html`, `web/script.js`, `web/style.css` — prosty frontend webowy do zadawania pytan i przebudowy indeksu.

## Notatki

- Dokumenty trzymaj w `data/docs` (generowane artykuły trafiają domyślnie do `data/docs/gen`).
- Jeśli brakuje trafień, zwiększ `TOP_K` lub zmniejsz `SCORE_THRESHOLD`.
- BM25 lepiej radzi sobie z dokładnymi dopasowaniami słów; embeddingi — z podobieństwem semantycznym.