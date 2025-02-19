import logging
import asyncio
from cerebras_api import cerebras_response
from polli_text_model import pollinations_text_response
from pplx import perplexity_response
from db_manager import DatabaseManager, get_models
from discord.ext import tasks

logger = logging.getLogger('AlphaLLM')

@tasks.loop(hours=1)
async def check_online_models():
    db_manager = DatabaseManager()
    try:
        models = await get_models(db_manager)
        logger.debug(f"Modèles : {models}")

        test_message = "test"
        working_model = 0
        models_to_test = models[:-2]

        for model in models_to_test:
            try:
                r = await pollinations_text_response(test_message, model["name"])
                if r != "":
                    working_model += 1
                    logger.debug(f"{model['name']} Online")
            except Exception as e:
                logger.error(f"Vérification échouée pour {model['role_name']} : {e}")
                pass

        if working_model == len(models_to_test):
            logger.info("Tous les modèles sont en ligne !")

    except Exception as e:
        logger.error(f"Erreur durant la vérification : {e}")
    finally:
        db_manager.disconnect()
