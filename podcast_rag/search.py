"""Recherche sémantique dans les chunks d'une transcription.

Usage :
    python -m podcast_rag.search data/processed/extrait-10min.small.vad.chunks-45s.json \
        "Quel logiciel utiliser pour écrire des partitions ?"
"""

import argparse
import json
from pathlib import Path

import numpy as np

from podcast_rag.embeddings import embed_query
from podcast_rag.utils import format_ts


def search(question: str, chunks: list[dict], vectors: np.ndarray,
           top_k: int = 3) -> list[tuple[dict, float]]:
    """Renvoie les `top_k` chunks les plus proches de la question, avec leur score."""
    query_vector = embed_query(question)       # forme (1024,)
    scores = vectors @ query_vector             # (16, 1024) @ (1024,) -> (16,)
    best = np.argsort(scores)[::-1][:top_k]     # indices triés du meilleur au moins bon
    return [(chunks[i], float(scores[i])) for i in best]


def main() -> None:
    parser = argparse.ArgumentParser(description="Recherche sémantique.")
    parser.add_argument("chunks", type=Path, help="JSON produit par chunk.py")
    parser.add_argument("question", help="La question à poser")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    data = json.loads(args.chunks.read_text(encoding="utf-8"))
    vectors = np.load(args.chunks.with_suffix(".npy"))

    for rank, (chunk, score) in enumerate(search(args.question, data["chunks"],
                                                 vectors, args.top_k), start=1):
        print(f"\n#{rank}  score {score:.3f}  "
              f"[{format_ts(chunk['start'])} -> {format_ts(chunk['end'])}]")
        print(f"   {chunk['text'][:300]}...")


if __name__ == "__main__":
    main()