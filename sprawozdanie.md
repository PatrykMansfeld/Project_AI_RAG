# Sprawozdanie z projektu: RAG Chatbot (Ollama, Python)

## 1. Informacje ogolne

- Temat projektu: lokalny chatbot RAG odpowiadajacy na pytania na podstawie korpusu dokumentow.
- Technologie: Python 3.10+, Ollama, modele `llama3.1` oraz `nomic-embed-text`, Flask.
- Srodowisko: Windows (CMD/PowerShell), uruchomienie lokalne.

## 2. Problem badawczy

Celem projektu jest sprawdzenie, czy zastosowanie prostej architektury RAG (Retrieval-Augmented Generation) z lokalnym modelem jezykowym poprawia poprawnosc i wiarygodnosc odpowiedzi w porownaniu do odpowiedzi generowanych bez wsparcia dokumentami. Kluczowym zalozeniem jest wymuszenie korzystania z kontekstu oraz cytowanie zrodel, co ma ograniczac halucynacje i ulatwiac weryfikacje odpowiedzi.

## 3. Cel i zakres

Zakres projektu obejmuje:

- zbudowanie indeksu dokumentow i mechanizmu wyszukiwania kontekstu (embeddingi lub BM25),
- generowanie odpowiedzi modelu LLM ograniczonych do dostarczonego kontekstu wraz z cytowaniem zrodel,
- zapewnienie prostego interfejsu CLI oraz frontendu WWW,
- wdrozenie podstawowej ewaluacji poprawnosci odpowiedzi.

## 4. Zrealizowane dzialania i uzasadnienie

**Indeksowanie dokumentow (index)**
- Operacja: chunkowanie dokumentow oraz wyliczanie embeddingow.
- Uzasadnienie: umozliwia semantyczne wyszukiwanie fragmentow istotnych dla zadanego pytania.

**Retrieval (embeddingi / BM25)**
- Operacja: wyszukiwanie fragmentow top-K na podstawie podobienstwa (lub dopasowania w BM25).
- Uzasadnienie: dostarcza do modelu LLM wyselekcjonowany kontekst, co ogranicza ryzyko generowania nieprawdziwych informacji.

**Generowanie odpowiedzi z cytowaniem**
- Operacja: budowa promptu zawierajacego kontekst i wymuszenie cytowania w formacie `[source: ...#chunk-id]`.
- Uzasadnienie: zwieksza wiarygodnosc odpowiedzi i umozliwia szybka weryfikacje, skad pochodza informacje.

**Guardrails**
- Operacja: odmowa odpowiedzi w przypadku braku wystarczajacego kontekstu.
- Uzasadnienie: redukuje liczbe blednych, "wymyslonych" odpowiedzi, gdy system nie znajduje podstaw w dokumentach.

**Ewaluacja na zestawie QA**
- Operacja: metryka dopasowania slow kluczowych w odpowiedzi oraz opcjonalny tryb LLM-judge.
- Uzasadnienie: szybka i praktyczna ocena poprawnosci odpowiedzi na podstawie prostych definicji testowych.

**Frontend WWW (Flask)**
- Operacja: udostepnienie API oraz interfejsu webowego do czatu, ewaluacji i przebudowy indeksu.
- Uzasadnienie: ulatwia testowanie i demonstracje projektu.

## 5. Analiza wynikow (poprawnosc odpowiedzi)

Ocena poprawnosci odpowiedzi opiera sie na dwoch warstwach:

- dopasowanie oczekiwanych slow kluczowych w odpowiedzi,
- opcjonalny LLM-judge, ktory klasyfikuje odpowiedz jako poprawna lub niepoprawna.

Na jakosc odpowiedzi wplywaja przede wszystkim:

- jakosc i spojnosci korpusu dokumentow,
- parametry retrievalu (`TOP_K`, `SCORE_THRESHOLD`),
- dlugosc chunkow i wartosc overlapu,
- dobor modelu LLM oraz modelu embeddingow.

W projekcie zastosowano guardrails i cytowanie zrodel, co zwieksza wiarygodnosc odpowiedzi oraz ulatwia ich weryfikacje. Jest to zgodne z dobrymi praktykami projektowania systemow RAG i pomaga ograniczac halucynacje.

## 6. Rezultaty projektu

W ramach projektu powstaly:

- dzialajacy pipeline RAG (index -> retrieval -> odpowiedz z cytowaniem),
- interfejs CLI oraz panel webowy do testow i ewaluacji,
- mechanizm generowania artykulow w celu rozbudowy korpusu,
- mozliwosc uruchomienia ewaluacji na pliku `qa.jsonl`.

## 7. Wyniki ewaluacji

Uruchomienie:

```bat
python src\main.py eval --qa data\eval\qa.jsonl --out data\eval\report.json --use-judge
```

Wynik (fragment z `data/eval/report.json`):

```json
{
  "count": 2,
  "keyword_accuracy": 0.5,
  "judge_accuracy": 0.5
}
```

Interpretacja:

- w testowym zbiorze QA 1 z 2 odpowiedzi spelnila kryteria slow kluczowych,
- LLM-judge ocenil 1 z 2 odpowiedzi jako poprawna.

## 8. Wnioski

Zaproponowana architektura RAG z lokalnym modelem jezykowym umozliwia generowanie odpowiedzi opartych na zrodlach i ulatwia ich weryfikacje. Poprawnosc odpowiedzi zalezy glownie od jakosci korpusu oraz ustawien retrievalu. Dalsza poprawa wynikow wymaga rozbudowy danych, dopracowania zestawu QA oraz dostrojenia parametrow wyszukiwania.