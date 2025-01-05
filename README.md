# Bot Discord avec IA et génération d'images

## Description

Ce projet est un bot Discord polyvalent intégrant des fonctionnalités d'IA conversationnelle et de génération d'images. Il utilise l'API Cerebras pour le traitement du langage naturel et l'API Pollinations pour la génération d'images.

## Fonctionnalités principales

- Réponses IA aux mentions et messages privés
- Génération d'images à partir de prompts textuels
- Commandes slash pour diverses fonctionnalités
- Système de logging avancé

## Prérequis

- Python 3.9+
- Bibliothèques Python : discord.py, aiohttp, cerebras-cloud-sdk

## Installation

1. Clonez ce dépôt :
```shell
git clone https://github.com/YoannDev90/AlphaLLM-v2.git
```
2. Installez les dépendances :
```shell
pip install -r requirements.txt
```
3. Configurez le fichier `config.json` avec vos tokens et paramètres :
```json
{
"DISCORD_TOKEN": "votre_token_discord",
"LOGGER_BOT_TOKEN": "token_du_bot_logger",
"CEREBRAS_API_KEY": "votre_clé_api_cerebras",
"dev_ids": ["votre_id_discord"]
}
```
## Utilisation

Lancez le bot avec la commande :
```shell
python bot.py
```
## Commandes disponibles

- `/ping` : Affiche la latence du bot
- `/infos` : Montre les informations sur le bot
- `/help` : Liste les commandes disponibles
- `/image` : Génère une image à partir d'un prompt
- `/contact` : Envoie un message au développeur

## Structure du projet

- `bot.py` : Script principal du bot
- `cerb_api.py` : Interface avec l'API Cerebras
- `commands.py` : Définition des commandes slash
- `pollinations.py` : Interface avec l'API Pollinations pour la génération d'images
- `logger_bot.py` : Bot de logging

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

[License MIT](https://github.com/YoannDev90/AlphaLLM-v2/blob/main/LICENSE)

