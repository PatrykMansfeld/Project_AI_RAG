import os
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory

from rag.config import Config
from rag.rag_core import SimpleRAG
from rag.analysis import analyze_corpus
from rag.evaluator import evaluate
from rag.generate import generate_articles

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "..", "web"))
# Aplikacja Flask serwująca UI i API RAG

cfg = Config()
rag = SimpleRAG(cfg)
index_built = False


def ensure_index():
    global index_built
    if not index_built:
        rag.build()
        index_built = True
    # Gwarantuje zbudowany indeks przed zapytaniami


@app.route("/")
def index_page():
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
    return send_from_directory(static_dir, "index.html")
    # Serwuje stronę główną


@app.route("/static/<path:filename>")
def static_files(filename: str):
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
    return send_from_directory(static_dir, filename)
    # Serwuje pliki statyczne


@app.route("/api/index", methods=["POST"])
def api_index():
    rag.build()
    global index_built
    index_built = True
    return jsonify({"status": "ok"})
    # Przebudowa indeksu


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data: Dict[str, Any] = request.get_json(force=True) or {}
    q = str(data.get("question", "")).strip()
    if not q:
        return jsonify({"error": "question is required"}), 400
    ensure_index()
    res = rag.answer(q)
    return jsonify({
        "answer": res["answer"],
        "sources": res["sources"],
    })
    # Czat RAG z cytowaniem źródeł


@app.route("/api/analyze", methods=["GET"])
def api_analyze():
    stats = analyze_corpus(cfg)
    return jsonify(stats)
    # Statystyki korpusu


@app.route("/api/eval", methods=["POST"])
def api_eval():
    data: Dict[str, Any] = request.get_json(force=True) or {}
    qa_path = str(data.get("qa_path", "data/eval/qa.jsonl"))
    try:
        res = evaluate(cfg, qa_path)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    # Ewaluacja odpowiedzi na zbiorze QA


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data: Dict[str, Any] = request.get_json(force=True) or {}
    topic = str(data.get("topic", "")).strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    count = int(data.get("count", 1))
    min_words = int(data.get("min_words", 400))
    style = str(data.get("style", "encyklopedyczny"))
    try:
        paths = generate_articles(cfg, topic=topic, count=count, min_words=min_words, style=style)
        return jsonify({"generated": paths})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    # Generuje artykuły Markdown do korpusu


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"[web] Starting Flask on http://{host}:{port}")
    app.run(host=host, port=port)
