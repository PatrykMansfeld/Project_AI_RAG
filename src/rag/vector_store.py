from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.neighbors import NearestNeighbors


class VectorStore:
    def __init__(self):
        self.index: Optional[NearestNeighbors] = None
        self.vectors: Optional[np.ndarray] = None
        self.meta: List[Dict[str, Any]] = []
        # Prosty wektorowy store z NN

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return v / norms
        # Normalizacja do kosinusa

    def add(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]):
        vectors = self._normalize(vectors)
        self.vectors = vectors if self.vectors is None else np.vstack([self.vectors, vectors])
        self.meta.extend(metadatas)
        self.index = NearestNeighbors(n_neighbors=min(10, len(self.meta)), metric="cosine")
        self.index.fit(self.vectors)
        # Budowa indeksu NN

    def search(self, query_vec: np.ndarray, top_k: int) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None or self.vectors is None:
            return []
        q = self._normalize(query_vec.reshape(1, -1))
        distances, idxs = self.index.kneighbors(q, n_neighbors=min(top_k, len(self.meta)))
        sims = 1 - distances[0]
        return [(self.meta[i], float(s)) for i, s in zip(idxs[0], sims)]
        # Zwraca meta i podobieństwo
