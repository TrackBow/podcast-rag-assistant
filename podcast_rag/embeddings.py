"""Calcul d'embeddings via l'API locale d'Ollama."""

import httpx
import numpy as np

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "qwen3-embedding:0.6b"

# qwen3-embedding est asymétrique : les QUESTIONS sont précédées d'une instruction,
# les PASSAGES sont encodés tels quels (voir ADR 0002).
QUERY_INSTRUCTION = ("Given a question, retrieve passages from a podcast "
                     "transcript that answer the question")


def embed_texts(texts: list[str], model: str = EMBED_MODEL) -> np.ndarray:
    """Renvoie une matrice (nombre de textes, dimension) de vecteurs normalisés."""
    response = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": model, "input": texts},  
        timeout=300,  # le 1er appel charge le modèle 
    )
    response.raise_for_status()  
    return np.array(response.json()["embeddings"], dtype=np.float32)


def embed_query(question: str, model: str = EMBED_MODEL) -> np.ndarray:
    """Encode une question en ajoutant l'instruction attendue par le modèle."""
    prompt = f"Instruct: {QUERY_INSTRUCTION}\nQuery: {question}"
    return embed_texts([prompt], model)[0]