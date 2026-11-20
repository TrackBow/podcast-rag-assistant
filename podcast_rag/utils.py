"""Fonctions utilitaires partagées."""


def format_ts(seconds: float) -> str:
    """Convertit des secondes (ex. 125.4) en texte HH:MM:SS (ex. 00:02:05)."""
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"