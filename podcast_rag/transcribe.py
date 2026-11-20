"""Transcription d'un fichier audio avec faster-whisper.

Usage :
    python -m podcast_rag.transcribe data/raw/extrait-10min.wav --model small
"""

import argparse
import json
import time
from pathlib import Path

from faster_whisper import WhisperModel


def format_ts(seconds: float) -> str:
    """Convertit des secondes (ex. 125.4) en texte HH:MM:SS (ex. 00:02:05)."""
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def transcribe(audio_path: Path, model_size: str = "small",
               language: str = "fr", vad: bool = True) -> dict:
    """Transcrit un fichier audio et renvoie les segments horodatés + des mesures."""

    # 1. Chargement du modèle (téléchargé depuis Hugging Face la 1re fois)
    t0 = time.perf_counter()
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    load_time = time.perf_counter() - t0

    # 2. Lancement de la transcription
    t1 = time.perf_counter()
    segments, info = model.transcribe(
        str(audio_path),
        language=language,  # on impose le français 
        vad_filter=vad,     # saute les passages sans parole
        beam_size=5,
    )


    results = []
    for seg in segments:
        text = seg.text.strip()
        results.append({
            "id": seg.id,
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": text,
        })
        print(f"[{format_ts(seg.start)} -> {format_ts(seg.end)}] {text}")
    transcribe_time = time.perf_counter() - t1

    return {
        "source": audio_path.name,
        "model": model_size,
        "language": info.language,
        "vad": vad,
        "audio_duration_s": round(info.duration, 2),
        "load_time_s": round(load_time, 2),
        "transcribe_time_s": round(transcribe_time, 2),
        "real_time_factor": round(transcribe_time / info.duration, 3),
        "segments": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcrit un fichier audio.")
    parser.add_argument("audio", type=Path, help="Chemin du fichier audio")
    parser.add_argument("--model", default="small",
                        help="Taille du modèle : tiny, base, small, medium...")
    parser.add_argument("--no-vad", action="store_true",
                        help="Désactive le filtre de détection de voix")
    args = parser.parse_args()

    result = transcribe(args.audio, model_size=args.model, vad=not args.no_vad)

    # Nom de sortie qui garde la trace des paramètres : extrait-10min.small.vad.json
    suffix = "vad" if result["vad"] else "novad"
    out_path = Path("data/processed") / f"{args.audio.stem}.{args.model}.{suffix}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"\n{len(result['segments'])} segments -> {out_path}")
    print(f"Chargement du modèle : {result['load_time_s']} s")
    print(f"Transcription : {result['transcribe_time_s']} s "
          f"pour {result['audio_duration_s']} s d'audio "
          f"(RTF = {result['real_time_factor']})")


if __name__ == "__main__":
    main()