#bot.py

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import datetime
from logger import setup_logging
from cmds import setup_commands
from ai_process import process_ai_response
from db_manager import DatabaseManager, get_models, create_model_roles
from model_monitor import check_online_models
from colorama import init
from dotenv import load_dotenv
import os

init(autoreset=True)

load_dotenv()
config = {key: os.getenv(key) for key in os.environ}

VERSION = "3.5"
LOG_LEVEL = config["LOG_LEVEL"]
LOG_FILE = '#alphallm.log'
ROLE_CREATION_DELAY = 1

STATUSES = [
    "/help pour les commandes",
    "@AlphaLLM pour discuter",
    "/image pour créer des images",
    f"Version {VERSION} en ligne"
]

logger = logging.getLogger('AlphaLLM')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

current_status_index = 0
role_model_mapping = {}

@tasks.loop(seconds=15)
async def change_status():
    logger.debug("Changement de statut du bot...")
    global current_status_index
    current_status = STATUSES[current_status_index]
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=current_status))
    current_status_index = (current_status_index + 1) % len(STATUSES)
    logger.debug(f"Statut changé pour : {current_status}")

@bot.event
async def on_ready():
    logger.info(f'{bot.user} est connecté à Discord!')
    db_manager = DatabaseManager()
    models = await get_models(db_manager)
    logger.info(f"{len(models)} modèles récupérés.")
    for guild in bot.guilds:
        logger.info(f"Vérification pour {guild.name}.")
        await create_model_roles(bot, guild, models, db_manager)
        logger.info("Vérification des rôles terminée.")
    await setup_commands(bot)
    logger.info("Commandes initialisées.")
    check_online_models.start()
    logger.info("Démarrage de la vérification continue")
    now = datetime.datetime.now()
    delay = 60 - now.second
    if delay == 60:
        delay = 0
    logger.info(f"Attente de {delay} secondes avant le début de la rotation des statuts")
    await asyncio.sleep(delay)
    logger.info("Démarrage de la rotation des statuts")
    change_status.start()
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if not message.author.bot and message.channel.type == discord.ChannelType.text:
        logger.debug(f"Message reçu de {message.author}: {message.content}")
        mentioned_role_ids = [str(role.id) for role in message.role_mentions if str(role.id) in role_model_mapping]
        bot_mentioned = bot.user.mentioned_in(message)

        if bot_mentioned or mentioned_role_ids:
            ai_choice = {"model_name": "llama 3.3 70b (fastest)", "role_name": "Default"}
            if mentioned_role_ids:
                role_id = mentioned_role_ids[0]
                if role_id in role_model_mapping:
                    ai_choice = {
                        "model_name": role_model_mapping[role_id]["model_name"],
                        "role_name": role_model_mapping[role_id]["role_name"]
                    }
                    logger.info(f"Modèle {ai_choice['role_name']} mentionné par {message.author.display_name}")
                else:
                    logger.warning(f"Rôle ID {role_id} mentionné mais non trouvé dans role_model_mapping. Utilisation du modèle par défaut.")
            elif bot_mentioned:
                logger.info(f"Bot mentionné par {message.author.display_name}. Utilisation du modèle par défaut.")

            query = message.content.replace(f'<@{bot.user.id}>', '').strip()
            for role in message.role_mentions:
                query = query.replace(f'<@&{role.id}>', '').strip()

            if query == "":
                await message.channel.send("Prompt vide, veuillez entrer un prompt pour obtenir une réponse.")
                logger.warning("Prompt vide, aucune réponse envoyée")
                return

            logger.debug(f"Query : {query}")
            logger.info(f"Envoi de la requête à {ai_choice['role_name']} pour {message.author.display_name}")
            await process_ai_response(message, query, ai_choice)

        await bot.process_commands(message)

async def main():
    try:
        #await bot.start(config["DISCORD_TOKEN"])
        await bot.start(config["TESTBOT_TOKEN"])
        logger.info("Discord bot démarré")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du bot : {e}")

if __name__ == "__main__":
    setup_logging(LOG_LEVEL, LOG_FILE)
    asyncio.run(main())