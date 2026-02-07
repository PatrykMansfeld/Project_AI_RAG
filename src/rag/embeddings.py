from typing import List, Optional

import numpy as np
import ollama


class EmbeddingClient:
    def __init__(self, model: str, host: Optional[str] = None):
        # Klient do embeddingów Ollama.
        self.model = model
        self.client = ollama.Client(host=host) if host else ollama.Client()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        # Embeduje listę tekstów do macierzy wektorów.
        vecs: List[List[float]] = []
        for t in texts:
            res = self.client.embeddings(model=self.model, prompt=t)
            vecs.append(res["embedding"])  # type: ignore[index]
        return np.array(vecs, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        # Embeduje pojedyncze pytanie.
        return self.embed_texts([text])[0]
