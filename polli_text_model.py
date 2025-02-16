import pollinations
import asyncio
import logging
import json

logger = logging.getLogger('AlphaLLM')

async def pollinations_text_response(prompt, model):
    text_model = pollinations.Async.Text(model=model)
    try:
        response = await text_model(prompt=prompt)
        return response.response
    except Exception as e:
        logger.error(f"Erreur lors de la génération de texte Pollinations: {e}")
        return f"Une erreur s'est produite: {str(e)}"
