from typing import Any, Dict, List


def system_prompt(mode: str = "strict", with_guardrails: bool = True) -> str:
    base = {
        "strict": "Jesteś rygorystycznym asystentem. Odpowiadaj tylko na podstawie kontekstu. Cytuj źródła w formacie [source: ścieżka#chunk-id]. Jeśli w kontekście brakuje informacji, powiedz wprost, że nie wiesz.",
        "friendly": "Jesteś uprzejmym asystentem. Odpowiadaj zwięźle na podstawie kontekstu i zawsze cytuj źródła [source: ścieżka#chunk-id]. Jeśli czegoś nie ma w kontekście, przyznaj to.",
        "concise": "Jesteś bardzo zwięzłym asystentem. Udzielaj krótkich odpowiedzi wyłącznie z kontekstu. Cytuj źródła [source: ścieżka#chunk-id]. Gdy brak danych, napisz, że brak informacji."
    }.get(mode, "strict")
    if not with_guardrails:
        return base
    rails = (
        "Guardrails: (1) Nie odpowiadaj na pytania niezwiązane z kontekstem. "
        "(2) Nie zmyślaj faktów ani źródeł. (3) Jeśli kontekst jest pusty lub za słaby, odpowiedz 'Brak informacji w dokumentach'."
    )
    return base + " " + rails
    # Warianty system promptu + proste guardrails


def few_shot() -> List[Dict[str, str]]:
    return [
        {"role": "user", "content": "Co to jest RAG?"},
        {"role": "assistant", "content": "RAG łączy wyszukiwanie dokumentów z generowaniem. [source: sample.md#chunk-0]"},
    ]
    # Przykłady do promptu


def user_prompt(question: str, passages: List[Dict[str, Any]]) -> str:
    parts = []
    for p in passages:
        parts.append(f"[source: {p['source']}#chunk-{p['chunk_id']}]\n{p['text']}")
    ctx = "\n\n".join(parts) if parts else "(brak kontekstu)"
    return (
        f"Kontekst:\n\n{ctx}\n\n"
        f"Zasady odpowiedzi: cytuj źródła, nie wymyślaj faktów, jeśli brak danych napisz 'Brak informacji w dokumentach'.\n"
        f"Pytanie: {question}\n\n"
        f"Udziel zwięzłej odpowiedzi po polsku."
    )
    # Łączy konteksty, pytanie i przypomina o guardrails


def article_system_prompt() -> str:
    return (
        "Jesteś pomocnym autorem. Tworzysz samodzielne artykuły w Markdown po polsku, "
        "z czytelną strukturą (tytuł, sekcje, listy), bez zbędnego wodolejstwa. "
        "Unikaj halucynacji: gdy temat wymaga źródeł zewnętrznych, przedstaw neutralne, ogólne informacje."
    )
    # Zasady generowania artykułu


def build_article_prompt(topic: str, style: str, min_words: int) -> str:
    return (
        f"Napisz artykuł w Markdown o temacie: '{topic}'.\n"
        f"Styl: {style}.\n"
        f"Wymagania: min. {min_words} słów, tytuł (H1), 3–5 sekcji (H2/H3), listy punktowane, krótkie podsumowanie.\n"
        f"Nie dodawaj zewnętrznych cytatów ani linków — artykuł ma być samowystarczalny i stanie się dokumentem w korpusie RAG.\n"
    )
    # Szablon promptu artykułu
