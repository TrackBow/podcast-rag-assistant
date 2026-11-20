# Journal de bord

Journal du développement, entrée par entrée : ce qui a été fait, les problèmes rencontrés et ce que j'en ai appris.

## 2026-11-20 : comparaison des modèles base et small

- Test du modèle `base` sur le même extrait (interrompu avant la fin, RTF non mesuré).
- Observations sur les 5 premières minutes :
  - `base` fait plus d'erreurs que `small` sur le français courant (« Il y a une collette ? » pour « Yann Collette ? », « 80 à 13.1 FM » pour « Cause Commune 93.1 FM »).
  - Sur les noms propres, aucun des deux n'est systématiquement meilleur : `base` reconnaît « Slackware » et « Kempf », que `small` rate ; `small` est plus proche sur « Humbert ».
  - `base` produit des segments beaucoup plus longs (jusqu'à 20 s contre 3 à 6 s), ce qui rend les minutages moins précis pour les citations.
- Décision provisoire : on garde `small`. Une comparaison chiffrée (WER sur la transcription de référence de l'April) viendra en phase d'évaluation.
- Appris : comparer des modèles « à l'œil » sur quelques exemples ne suffit pas à conclure ; il faut une métrique mesurée sur une référence.

## 2026-11-18 : transcription (phase 1)

- Décision documentée dans `docs/adr/0001-faster-whisper.md` : faster-whisper plutôt qu'openai-whisper, whisper.cpp ou WhisperX.
- Extrait de test de 10 min préparé avec ffmpeg : WAV mono 16 kHz (`-t 600 -ac 1 -ar 16000`).
- Script `podcast_rag/transcribe.py` : modèle chargé sur CPU en int8, filtre de détection de voix (VAD), export JSON des segments horodatés, mesure séparée du temps de chargement et du temps de transcription.
- Problème : `TypeError: av.open() got an unexpected keyword argument 'metadata_errors'`. Cause : pip avait installé PyAV 19, dépendance de faster-whisper sans version maximale, incompatible avec faster-whisper 1.2.1. Solution : PyAV figé en 16.1.0 dans `requirements.txt`.
- Mesures (Intel i7-8550U, 16 Go de RAM, sans GPU) :

| Modèle | Durée audio | Temps de transcription | RTF | Chargement | Segments |
|---|---|---|---|---|---|
| small (int8, VAD) | 600 s | 293 s | 0,49 | 2,8 s | 148 |

- Qualité : le français courant est bien transcrit, ponctuation comprise. Les erreurs se concentrent sur les noms propres et le jargon technique : « slacouère » (Slackware), « fait droit » (Fedora), « Muscore » (MuseScore), « Lilliponde » (LilyPond), « Librosic » (LibraZiK). Conséquence pour le RAG : une recherche par mots-clés sur ces noms échouera ; à tester avec la recherche sémantique et avec le paramètre `hotwords` de faster-whisper.
- Appris :
  - `model.transcribe()` renvoie un générateur : la transcription se fait pendant la boucle qui le parcourt, donc le chronomètre doit s'arrêter après la boucle.
  - Figer sa dépendance directe ne suffit pas ; une dépendance transitive peut casser le projet.
  - Lire une traceback de bas en haut pour trouver où l'erreur se produit, et qui a appelé quoi.

## 2026-11-18 : mise en place (phase 0)

- Environnement : Windows 11 + WSL2 (Ubuntu 24.04), VS Code connecté à WSL, authentification GitHub par clé SSH.
- Création du dépôt et de la structure du projet : package `podcast_rag/`, `tests/`, `scripts/`, `docs/adr/`, `data/` (exclu de Git).
- Environnement virtuel Python (`.venv`).
- Média de test : émission « Libre à vous ! » du 1er octobre 2019 (April / Cause Commune), sujet sur les logiciels libres pour l'audio et la musique assistée par ordinateur. Licence Art Libre 1.3 / CC BY-SA 2.0 ou ultérieures. Le fichier n'est pas versionné.
- Appris : WSL2 est une machine virtuelle légère avec un vrai noyau Linux ; le code doit vivre dans le système de fichiers Linux (`~`), pas dans `/mnt/c`, pour éviter des accès disque lents entre WSL et Windows.