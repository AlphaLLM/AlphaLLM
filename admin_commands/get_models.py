import discord
import logging
import aiohttp
import json
from dotenv import load_dotenv
import os

load_dotenv()
config = {
    key: os.getenv(key)
    for key in os.environ
}

logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
    @bot.tree.command(name="get-models", description="Récupère la liste des modèles disponibles")
    async def get_models(interaction: discord.Interaction):
        logger.info(f"Commande get_models exécutée par {interaction.user.display_name}")
        if not str(interaction.user.id) == config["DEV_ID"]:
            await interaction.response.send_message("Vous n'avez pas la permission d'exécuter cette commande administrateur.", ephemeral=True)
            return
        model_url = "https://text.pollinations.ai/models"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(model_url) as response:
                    if response.status == 200:
                        models_json = await response.json()
                        
                        model_list_text = ""
                        for model in models_json:
                            name = model.get("name", "N/A").upper()
                            description = model.get("description", "N/A")
                            vision = model.get("vision", "N/A")
                            model_list_text += f"**{name}**: {description} (Vision: {vision})\n"
                        model_list_text += f"**PERPLEXITY**: Perplexity Web Search (Vision: \"N/A\")\n"
                        model_list_text += f"**LLAMA 3.3 70B (FAST)**: Llama 3.3 70B (fast) (Vision: \"N/A\")\n"

                        
                        messages = []
                        while len(model_list_text) > 0:
                            if len(model_list_text) <= 1900:
                                messages.append(model_list_text)
                                break
                            else:
                                split_index = model_list_text[:1900].rfind('\n')
                                if split_index == -1:
                                    split_index = 1900
                                messages.append(model_list_text[:split_index])
                                model_list_text = model_list_text[split_index:].strip()

                        for message in messages:
                            await interaction.response.send_message(message)
                    else:
                        await interaction.response.send_message(f"Erreur lors de la récupération des modèles: {response.status}", ephemeral=True)
                        logger.error(f"Erreur lors de la récupération des modèles: {response.status}")

        except aiohttp.ClientError as e:
            await interaction.response.send_message(f"Erreur de connexion: {e}", ephemeral=True)
            logger.error(f"Erreur de connexion: {e}")
        except json.JSONDecodeError as e:
            await interaction.response.send_message(f"Erreur lors de la lecture du JSON: {e}", ephemeral=True)
            logger.error(f"Erreur lors de la lecture du JSON: {e}")
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenue: {e}", ephemeral=True)
            logger.error(f"Une erreur est survenue: {e}")