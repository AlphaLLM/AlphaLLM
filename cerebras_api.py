from cerebras.cloud.sdk import Cerebras
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger('AlphaLLM')

load_dotenv()
config = {key: os.getenv(key) for key in os.environ}

cerebras_client = Cerebras(api_key=config["CEREBRAS_API_KEY"])

def cerebras_response(user_message):
    try:
        completion = cerebras_client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama3.3-70b"
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la réponse Cerebras : {e}")
        return f"Erreur lors de la génération de la réponse : {e}"
