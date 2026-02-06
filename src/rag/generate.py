import os
from typing import List
import ollama

from .config import Config
from .prompts import article_system_prompt, build_article_prompt
from .utils import slugify


def generate_articles(cfg: Config, topic: str, count: int = 1, min_words: int = 400, style: str = "encyklopedyczny") -> List[str]:
    client = ollama.Client(host=cfg.ollama_host)
    out_dir = os.path.join(cfg.data_dir, "gen")
    os.makedirs(out_dir, exist_ok=True)
    slug = slugify(topic)
    paths: List[str] = []
    for i in range(1, count + 1):
        messages = [
            {"role": "system", "content": article_system_prompt()},
            {"role": "user", "content": build_article_prompt(topic, style, min_words)},
        ]
        res = client.chat(model=cfg.llm_model, messages=messages, options={"temperature": cfg.temperature})
        content = res.get("message", {}).get("content", "")
        if not content:
            content = f"# {topic}\n\n(Brak treści — spróbuj ponownie)\n"
        fname = f"{slug}-{i}.md"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append(fpath)
        print(f"[generate] Zapisano: {fpath}")
    return paths
    # Tworzy artykuły Markdown i zapisuje na dysku
