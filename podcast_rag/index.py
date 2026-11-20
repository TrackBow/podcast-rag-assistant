"""Calcule et sauvegarde les embeddings des chunks d'une transcription.

Usage :
    python -m podcast_rag.index data/processed/extrait-10min.small.vad.chunks-45s.json
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

from podcast_rag.embeddings import embed_texts


def main() -> None:
    parser = argparse.ArgumentParser(description="Calcule les embeddings des chunks.")
    parser.add_argument("chunks", type=Path, help="JSON produit par chunk.py")
    args = parser.parse_args()

    data = json.loads(args.chunks.read_text(encoding="utf-8"))
    texts = [chunk["text"] for chunk in data["chunks"]]

    t0 = time.perf_counter()
    vectors = embed_texts(texts)
    elapsed = time.perf_counter() - t0

    out_path = args.chunks.with_suffix(".npy")  
    np.save(out_path, vectors)

    norms = np.linalg.norm(vectors, axis=1)
    print(f"{vectors.shape[0]} vecteurs de dimension {vectors.shape[1]} -> {out_path}")
    print(f"Calcul : {elapsed:.1f} s")
    print(f"Normes : min {norms.min():.4f}, max {norms.max():.4f}")


if __name__ == "__main__":
    main()