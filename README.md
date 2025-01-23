# Bot Discord avec IA et génération d'images

### [Site Internet](https://alphallm.fr.nf)

## Description

Ce projet est un bot Discord polyvalent intégrant des fonctionnalités d'IA conversationnelle et de génération d'images. Il utilise l'API Cerebras pour le traitement du langage naturel, ainsi que l'API de Perplexity Ai et l'API Pollinations pour la génération d'images et d'autres modèles de texte.

## Fonctionnalités principales

- Réponses IA aux mentions et messages privés
- Génération d'images à partir de prompts textuels
- Commandes slash pour diverses fonctionnalités
- Système de logging avancé

## Installation

1. Clonez ce dépôt :
```shell
git clone https://github.com/AlphaLLM/AlphaLLM.git
```
2. Installez les dépendances :
```shell
pip install -r requirements.txt
```
## Utilisation

Lancez le bot avec la commande :
```shell
python bot.py
```

## Commandes disponibles

### Bot principal
- `/ping` : Affiche la latence du bot
- `/infos` : Montre les informations sur le bot
- `/help` : Liste les commandes disponibles
- `/image` : Génère une image à partir d'un prompt
- `/contact` : Envoie un message au développeur

### Bot de logging
- `/logging-level` : Définit le niveau de log
- `/log-status` : Affiche le statut actuel du logger

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

[License MIT](LICENSE)
