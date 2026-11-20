# ADR 0002 : embeddings avec qwen3-embedding via Ollama

- Date : 2026-11-20
- Statut : acceptée

## Contexte

La recherche sémantique transforme les passages de la transcription et les questions en vecteurs (embeddings). Le contenu est en français, le calcul se fait sur CPU, l'espace disque est limité, et un LLM local via Ollama sera de toute façon nécessaire pour générer les réponses.

## Décision

Utiliser **Ollama** pour calculer les embeddings, avec le modèle **qwen3-embedding:0.6b** (Apache 2.0, 639 Mo, 1 024 dimensions).

Raisons :
- modèle multilingue, adapté à un contenu en français ;
- un seul service local (Ollama) pour les embeddings et le LLM, appelé par HTTP, qui deviendra un conteneur dans le Docker Compose ;
- pas de dépendance à PyTorch, contrairement à sentence-transformers ;
- taille raisonnable pour le disque disponible.

## Alternatives écartées

- **nomic-embed-text** : déjà utilisé pendant mon stage, sur des contenus français et anglais. Sa version standard est surtout entraînée sur l'anglais, alors que ce projet est entièrement en français. Hypothèse à vérifier en phase d'évaluation en comparant les deux modèles sur le même jeu de questions.
- **bge-m3** : multilingue et sans préfixe de requête, mais deux fois plus lourd (1,2 Go). Candidat de comparaison pour la phase d'évaluation.
- **sentence-transformers en Python** : ajoute PyTorch, plusieurs Go.

## Conséquences

- Le modèle est asymétrique : les questions doivent être précédées d'une instruction, pas les passages. Un oubli dégrade la qualité sans message d'erreur.
- Les vecteurs renvoyés par Ollama sont normalisés (norme 1) : la similarité cosinus se calcule par un simple produit scalaire.
- Ollama a détecté le GPU et répartit le modèle entre CPU et GPU ; les mesures de temps en dépendent.