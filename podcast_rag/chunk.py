"""Découpage d'une transcription en chunks horodatés.

Usage :
    python -m podcast_rag.chunk data/processed/extrait-10min.small.vad.json
"""

import argparse
import json
from pathlib import Path


def make_chunks(segments: list[dict], target_duration: float = 45.0,
                overlap: int = 2) -> list[dict]:
    """Regroupe des segments consécutifs en chunks d'environ `target_duration` secondes.

    Chaque chunk recommence `overlap` segments avant la fin du précédent.
    """
    chunks = []
    start = 0  

    while start < len(segments):
        end = start
        while (end < len(segments) - 1
               and segments[end]["end"] - segments[start]["start"] < target_duration):
            end += 1

        window = segments[start:end + 1]  # +1 car la borne de fin d'un slice est exclue
        chunks.append({
            "chunk_id": len(chunks),
            "start": window[0]["start"],
            "end": window[-1]["end"],
            "segment_ids": [seg["id"] for seg in window],
            "text": " ".join(seg["text"] for seg in window),
        })

        if end == len(segments) - 1:
            break  

        # Le prochain chunk recommence `overlap` segments en arrière...
        # ... mais toujours au moins un segment plus loin, sinon boucle infinie
        start = max(end + 1 - overlap, start + 1)

    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Découpe une transcription en chunks.")
    parser.add_argument("transcript", type=Path, help="JSON produit par transcribe.py")
    parser.add_argument("--duration", type=float, default=45.0,
                        help="Durée cible d'un chunk en secondes")
    parser.add_argument("--overlap", type=int, default=2,
                        help="Nombre de segments partagés entre deux chunks")
    args = parser.parse_args()

    data = json.loads(args.transcript.read_text(encoding="utf-8"))
    chunks = make_chunks(data["segments"], args.duration, args.overlap)

    result = {
        "source": data["source"],
        "transcript": args.transcript.name,
        "params": {"target_duration": args.duration, "overlap": args.overlap},
        "chunks": chunks,
    }
    out_path = args.transcript.with_name(
        f"{args.transcript.stem}.chunks-{int(args.duration)}s.json")
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    durations = [c["end"] - c["start"] for c in chunks]
    words = [len(c["text"].split()) for c in chunks]
    print(f"{len(chunks)} chunks -> {out_path}")
    print(f"Durée : moyenne {sum(durations) / len(durations):.1f} s, "
          f"min {min(durations):.1f} s, max {max(durations):.1f} s")
    print(f"Mots par chunk : moyenne {sum(words) / len(words):.0f}")


if __name__ == "__main__":
    main()