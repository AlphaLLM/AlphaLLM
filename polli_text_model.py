import pollinations
import asyncio
import logging

logger = logging.getLogger('discord_bot')

async def pollinations_text_response(prompt, model):
    logger.info(f"Génération de texte Pollinations demandée avec le modèle {model}")
    text_model = pollinations.Async.Text(model=model)
    try:
        response = await text_model(prompt=prompt)
        logger.info("Réponse Pollinations générée avec succès")
        return response.response
    except Exception as e:
        logger.error(f"Erreur lors de la génération de texte Pollinations: {e}")
        return f"Une erreur s'est produite: {str(e)}"

async def get_available_models():
    logger.info("Récupération des modèles Pollinations disponibles")
    try:
        models = pollinations.Text.models()
        logger.info(f"Modèles Pollinations récupérés: {models}")
        return models
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles Pollinations: {e}")
        return []
