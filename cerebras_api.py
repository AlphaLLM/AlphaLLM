from cerebras.cloud.sdk import Cerebras
import json
from dotenv import load_dotenv
import os

load_dotenv()
config = {
    key: os.getenv(key)
    for key in os.environ
}

# Initialisation du client Cerebras
cerebras_client = Cerebras(api_key=config["CEREBRAS_API_KEY"])

def cerebras_response(user_message):
    try:
        completion = cerebras_client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama3.3-70b"
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération de la réponse : {e}"
