import discord
from discord.ext import commands, tasks
import logging
import asyncio
from cmds import setup_commands
from cerebras_api import cerebras_response
from polli_text_model import pollinations_text_response
from pplx import perplexity_response
from db_manager import DatabaseManager
from dotenv import load_dotenv
import os
from colorama import Fore, Back, Style, init
import datetime
import re
import time

init(autoreset=True)

load_dotenv()
config = {key: os.getenv(key) for key in os.environ}

VERSION = "3.3"
LOG_LEVEL = config["LOG_LEVEL"]
LOG_FILE = 'alphallm.log'
ROLE_CREATION_DELAY = 1

STATUSES = [
    "/help pour les commandes",
    "@AlphaLLM pour discuter",
    "/image pour créer des images",
    f"Version {VERSION} en ligne"
]

current_status_index = 0
role_model_mapping = {}

class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.WHITE + Back.BLUE + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.INFO: Fore.WHITE + Back.GREEN + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.WARNING: Fore.WHITE + Back.YELLOW + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.ERROR: Fore.WHITE + Back.RED + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.CRITICAL: Fore.WHITE + Back.BLACK + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger('AlphaLLM')
logger.setLevel(LOG_LEVEL)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())

file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(console_handler)
logger.addHandler(file_handler)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

async def get_models(db_manager: DatabaseManager):
    logger.debug("Récupération des modèles depuis la base de données...")
    query = "SELECT * FROM models"
    try:
        models = db_manager.fetchall(query)
        logger.debug(f"Modèles récupérés : {models}")
        if models:
            columns = [column[0] if isinstance(column, tuple) else column.name for column in db_manager.cursor.description]
            models_list = [dict(zip(columns, model)) for model in models]
            logger.debug(f"Liste des modèles : {models_list}")
            return models_list
        else:
            logger.warning("Aucun modèle trouvé dans la base de données.")
            return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles : {e}")
        return []


async def create_model_roles(bot, guild, models, db_manager: DatabaseManager):
    global role_model_mapping
    role_model_mapping = {}

    query = "SELECT id, name FROM roles"
    try:
        roles_db = db_manager.fetchall(query)
        logger.debug(f"Rôles récupérés depuis la base de données : {roles_db}")

        if roles_db:
            for role_id, role_name in roles_db:
                model = next((model for model in models if model["role_name"] == role_name), None)

                if model:
                    role_model_mapping[str(role_id)] = {"role_name": role_name, "model_name": model["name"]}
                    logger.debug(f"Role {role_name} mappé à l'ID {role_id} et au modèle {model['name']}")
                else:
                    logger.warning(f"Aucun modèle trouvé avec le role_name {role_name}. Suppression du rôle.")
                    try:
                        delete_query = "DELETE FROM roles WHERE id = %s"
                        db_manager.execute(delete_query, (role_id,))
                        logger.info(f"Rôle avec ID {role_id} supprimé de la base de données.")

                        role = guild.get_role(int(role_id))
                        if role:
                            await role.delete(reason="Modèle inexistant")
                            logger.info(f"Rôle {role_name} (ID {role_id}) supprimé du serveur {guild.name}.")
                        else:
                            logger.warning(f"Rôle avec ID {role_id} non trouvé sur le serveur {guild.name}.")

                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression du rôle {role_name} (ID {role_id}) : {e}")
        else:
            logger.warning("Aucun rôle trouvé dans la base de données.")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rôles depuis la base de données : {e}")
        return

    existing_roles = guild.roles
    logger.debug(f"Rôles existants sur le serveur : {[role.name for role in existing_roles]}")

    bot_member = guild.me
    bot_roles = bot_member.roles
    logger.debug(f"Rôles attribués au bot : {[role.name for role in bot_roles]}")

    permissions = guild.me.guild_permissions
    if not permissions.manage_roles:
        logger.error(f"Le bot n'a pas la permission 'Manage Roles' sur le serveur {guild.name}")
        return

    for model in models:
        if 'role_name' not in model or 'name' not in model:
            logger.error(f"Modèle sans role_name ou name trouvé: {model}")
            continue

        role_name = model["role_name"]
        model_name = model["name"]
        existing_role = discord.utils.get(existing_roles, name=role_name)
        logger.debug(f"Vérification du rôle : {role_name} sur le serveur : {guild.name}")

        if existing_role:
            role_id = str(existing_role.id)
            logger.debug(f"Le rôle {role_name} existe déjà sur le serveur : {guild.name}")
            if role_id not in role_model_mapping:
                query = "INSERT INTO roles (id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = %s"
                params = (existing_role.id, role_name, role_name)
                try:
                    if db_manager.execute(query, params):
                        role_model_mapping[role_id] = {"role_name": role_name, "model_name": model_name}
                        logger.debug(f"Rôle {role_name} mappé dans la base de données.")
                    else:
                        logger.error(f"Impossible de mapper le rôle {role_name} dans la base de données.")
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de la base de données pour le rôle {role_name} : {e}")
                    continue
            else:
                role_model_mapping[role_id]["model_name"] = model_name

            if existing_role not in bot_roles:
                try:
                    await bot_member.add_roles(existing_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
                except discord.Forbidden:
                    logger.error(f"Permissions insuffisantes pour ajouter le rôle {role_name} au bot sur le serveur {guild.name}. Ensure the bot's role is higher than the role being assigned.")
        else:
            try:
                new_role = await guild.create_role(
                    name=role_name,
                    colour=discord.Colour(0xffffff),
                    mentionable=True
                )
                logger.info(f"Nouveau rôle créé : {role_name}")
                role_id = str(new_role.id)
                try:
                    await guild.me.add_roles(new_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
                except discord.Forbidden:
                    logger.error(f"Permissions insuffisantes pour ajouter le rôle {role_name} au bot sur le serveur {guild.name}. Ensure the bot's role is higher than the role being assigned.")

                query = "INSERT INTO roles (id, name) VALUES (%s, %s)"
                params = (new_role.id, role_name)
                try:
                    if db_manager.execute(query, params):
                        role_model_mapping[role_id] = {"role_name": role_name, "model_name": model_name}
                        logger.debug(f"Rôle {role_name} ajouté dans la base de données.")
                    else:
                        logger.error(f"Impossible d'ajouter le rôle {role_name} dans la base de données.")
                except Exception as e:
                    logger.error(f"Erreur lors de l'ajout du rôle {role_name} à la base de données : {e}")
                await asyncio.sleep(ROLE_CREATION_DELAY)
            except discord.Forbidden:
                logger.error(f"Permission insuffisante pour créer le rôle {role_name}")
            except discord.HTTPException as e:
                logger.error(f"Erreur HTTP lors de la création du rôle {role_name}: {e}")

    logger.info(f"Vérification des rôles terminée pour {guild.name}")


@tasks.loop(seconds=15)
async def change_status():
    logger.debug("Changement de statut du bot...")
    global current_status_index
    current_status = STATUSES[current_status_index]

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=current_status,
        )
    )
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

async def process_ai_response(message, query, ai_choice):
    if ai_choice["model_name"] == "perplexity":
        response = await perplexity_response(query)
    elif ai_choice["model_name"] == "llama 3.3 70b (fastest)":
        response = cerebras_response(query)
    else:
        response = await pollinations_text_response(query, ai_choice["model_name"])

    await smart_long_messages(message.channel, response)
    logger.info(f"Réponse envoyée pour {ai_choice['role_name']}")


async def smart_long_messages(channel, text: str, max_length: int = 2000):
    if len(text) <= max_length:
        await channel.send(text)
        return

    code_block_regex = r"```?```"
    code_blocks = list(re.finditer(code_block_regex, text))

    last_cut = 0
    in_code_block = False
    current_code_block = ""
    for i, match in enumerate(code_blocks):
        start, end = match.span()

        if not in_code_block:
            if start > last_cut:
                text_to_send = text[last_cut:start].strip()
                if text_to_send:
                    await send_text_in_chunks(channel, text_to_send, max_length)

            in_code_block = True
            current_code_block = text[start:end]
            last_cut = end

        else:
            in_code_block = False
            current_code_block += text[last_cut:end]
            await channel.send(current_code_block)
            last_cut = end

    if in_code_block:
        current_code_block += text[last_cut:]
        await channel.send(current_code_block)

    elif last_cut < len(text):
        text_to_send = text[last_cut:].strip()
        if text_to_send:
            await send_text_in_chunks(channel, text_to_send, max_length)

async def send_text_in_chunks(channel, text: str, max_length: int):
    lines = text.splitlines()
    current_message = ""
    for line in lines:
        if len(current_message) + len(line) + 1 > max_length:
            if current_message:
                await channel.send(current_message)
                current_message = ""
        current_message += line + "\n"
    if current_message:
        await channel.send(current_message)

async def main():
    try:
        await bot.start(config["DISCORD_TOKEN"])
        #await bot.start(config["TESTBOT_TOKEN"])
        logger.info("Discord bot démarré")
    except Exception as e:

        logger.error(f"Erreur lors du démarrage du bot : {e}")

if __name__ == "__main__":
    asyncio.run(main())
