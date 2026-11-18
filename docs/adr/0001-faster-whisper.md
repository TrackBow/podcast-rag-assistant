# ADR 0001 : faster-whisper pour la transcription

- Date : 2026-11-18
- Statut : acceptée

## Contexte

Le projet doit transcrire des fichiers audio et vidéo avec des horodatages, en local, sans GPU (Intel i7-8550U, 16 Go de RAM) et sans API payante. Le contenu testé est en français.

## Décision

Utiliser **faster-whisper** (SYSTRAN, licence MIT), une réimplémentation des modèles Whisper d'OpenAI sur le moteur d'inférence CTranslate2.

Raisons :
- plus rapide que l'implémentation d'origine à qualité équivalente, ce qui compte sur CPU ;
- quantification int8 sur CPU : moins de mémoire et de calcul ;
- pas de dépendance à PyTorch, donc une installation bien plus légère (espace disque limité) ;
- filtre de détection de voix (VAD) intégré pour sauter les passages sans parole.

## Alternatives écartées

- **openai-whisper** : l'implémentation de référence, mais elle dépend de PyTorch (plusieurs Go) et elle est plus lente sur CPU.
- **whisper.cpp** : très performant sur CPU, mais écrit en C++ ; l'intégration Python est moins directe.
- **WhisperX** : ajoute l'alignement mot à mot et l'identification des locuteurs, mais dépend de PyTorch. Piste possible plus tard pour la diarisation (savoir qui parle).
- **API cloud** (OpenAI, Deepgram…) : exclue par la contrainte « gratuit et local ».

## Conséquences

- La taille du modèle sera choisie en mesurant le compromis vitesse/qualité sur la machine.
- Les modèles sont téléchargés depuis Hugging Face au premier lancement, puis gardés en cache.