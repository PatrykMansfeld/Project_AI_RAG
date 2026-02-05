from typing import Any, Dict, List


def system_prompt() -> str:
    return (
        "Jesteś precyzyjnym asystentem. Odpowiadaj tylko na podstawie kontekstu. "
        "Cytuj źródła w formacie [source: ścieżka#chunk-id]. Gdy brak informacji—powiedz, że nie wiesz."
    )
    # Zasady dla modelu


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
    ctx = "\n\n".join(parts)
    return f"Kontekst:\n\n{ctx}\n\nPytanie: {question}\n\nOdpowiedz zwięźle po polsku z cytowaniem źródeł."
    # Łączy konteksty i pytanie


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
