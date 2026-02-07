import argparse
import json

from rag.config import Config
from rag.rag_core import SimpleRAG
from rag.analysis import analyze_corpus
from rag.evaluator import evaluate
from rag.generate import generate_articles

# ---------------- CLI ----------------
# Entry point for CLI subcommands.
def main():
    parser = argparse.ArgumentParser("Simple RAG (Ollama)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("index")
    sub.add_parser("chat")
    sub.add_parser("analyze")
    p_ev = sub.add_parser("eval")
    p_ev.add_argument("--qa", default="data/eval/qa.jsonl")
    p_ev.add_argument("--out", default=None, help="Ścieżka do zapisu raportu JSON")
    p_ev.add_argument("--use-judge", action="store_true", help="Wymuś LLM-judge (nadpisuje ENV)")

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--topic", required=True, help="Temat artykułu")
    p_gen.add_argument("--count", type=int, default=1, help="Liczba artykułów")
    p_gen.add_argument("--min_words", type=int, default=400, help="Minimalna liczba słów")
    p_gen.add_argument("--style", default="encyklopedyczny", help="Styl pisania")

    args = parser.parse_args()
    cfg = Config()

    if args.cmd == "index":
        rag = SimpleRAG(cfg)
        rag.build()
    elif args.cmd == "chat":
        rag = SimpleRAG(cfg)
        rag.build()
        # Prosty tryb interaktywny w konsoli.
        print("Pytaj (Ctrl+C aby wyjść)")
        try:
            while True:
                q = input("\nQ> ").strip()
                if not q:
                    continue
                res = rag.answer(q)
                print("\nA>", res["answer"])  
                print("\nŹródła:")
                for s in res["sources"]:
                    print(f"- {s['source']} (chunk {s['chunk_id']})")
        except KeyboardInterrupt:
            print("\nKoniec.")
    elif args.cmd == "analyze":
        print(json.dumps(analyze_corpus(cfg), ensure_ascii=False, indent=2))
    elif args.cmd == "eval":
        if args.use_judge:
            cfg.eval_use_judge = True
        print(json.dumps(evaluate(cfg, args.qa, args.out), ensure_ascii=False, indent=2))
    elif args.cmd == "generate":
        generate_articles(cfg, topic=args.topic, count=args.count, min_words=args.min_words, style=args.style)
    else:
        parser.print_help()

# Router CLI do funkcji RAG.
if __name__ == "__main__":
    main()