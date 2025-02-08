import discord
from discord.ext import commands, tasks
import logging
import asyncio
from commands import setup_commands
from cerebras_api import cerebras_response
from polli_text_model import pollinations_text_response, get_available_models
from pplx import perplexity_response
from dotenv import load_dotenv
import os
import json
import time
from colorama import Fore, Back, Style, init

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.WHITE + Back.BLUE + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.INFO: Fore.WHITE + Back.GREEN + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.WARNING: Fore.BLACK + Back.YELLOW + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.ERROR: Fore.WHITE + Back.RED + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.CRITICAL: Fore.WHITE + Back.BLACK + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger('AlphaLLM')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColoredFormatter())

logger.addHandler(console_handler)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
config = {key: os.getenv(key) for key in os.environ}

VERSION = "3.1"

STATUSES = [
    "/help pour les commandes",
    "@AlphaLLM pour discuter",
    "/image pour créer des images",
    f"Version {VERSION} en ligne"
]

current_status_index = 0

ROLES_FILE = 'roles.json'
ROLE_CREATION_DELAY = 1

role_model_mapping = {}

async def create_invite_link(channel):
    invite = await channel.create_invite(
        max_age=0,
        max_uses=1,
        unique=True
    )
    return invite.url

def load_roles():
    if os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_roles():
    with open(ROLES_FILE, 'w') as f:
        json.dump(role_model_mapping, f)

async def create_model_roles(bot):
    global role_model_mapping
    role_model_mapping = load_roles()
    
    for guild in bot.guilds:
        logger.info(f"Vérification des rôles pour {guild.name}")
        bot_member = guild.get_member(bot.user.id)
    
        models = list(await get_available_models())
        models.extend(["perplexity", "llama 3.3 70b (fastest)"])

        for model in models:
            role_name = model.capitalize()
            existing_role = discord.utils.get(guild.roles, name=role_name)
        
            if existing_role:
                logger.info(f"Le rôle {role_name} existe déjà")
                if str(existing_role.id) not in role_model_mapping:
                    role_model_mapping[str(existing_role.id)] = model.lower()
                if existing_role not in bot_member.roles:
                    await bot_member.add_roles(existing_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
            elif str(guild.id) not in role_model_mapping.get(model.lower(), {}):
                try:
                    new_role = await guild.create_role(
                        name=role_name,
                        colour=discord.Colour(0xffffff),
                        mentionable=True
                    )
                    logger.info(f"Nouveau rôle créé : {role_name}")
                    await bot_member.add_roles(new_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
                    role_model_mapping[str(new_role.id)] = model.lower()
                    await asyncio.sleep(ROLE_CREATION_DELAY)
                except discord.Forbidden:
                    logger.error(f"Permission insuffisante pour créer le rôle {role_name}")
                except discord.HTTPException as e:
                    logger.error(f"Erreur HTTP lors de la création du rôle {role_name}: {e}")

    save_roles()
    logger.info("Vérification et attribution des rôles terminées")

@tasks.loop(seconds=15)
async def change_status():
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

    logger.info("Liste des serveurs où le bot est présent :")
    for guild in bot.guilds:
        logger.info("-----------------------------------------------------")
        logger.info(f"Nom du serveur : {guild.name}")
        logger.info(f"ID du serveur : {guild.id}")
        logger.info(f"Nombre de membres : {guild.member_count}")
        logger.info(f"Date de création : {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Lien d'invitation : { await create_invite_link(guild.text_channels[0])}")
        logger.info(f"Propriétaire : {guild.owner} (ID: {guild.owner_id})")

    change_status.start()
    setup_commands(bot)
    await create_model_roles(bot)
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if not message.author.bot:
        logger.debug(f"Message reçu de {message.author}: {message.content}")
        
        mentioned_role_ids = [str(role.id) for role in message.role_mentions if str(role.id) in role_model_mapping]
        
        if bot.user.mentioned_in(message) or mentioned_role_ids:
            logger.info(f"Bot ou rôle mentionné par {message.author}")
            
            if mentioned_role_ids:
                ai_choice = role_model_mapping[mentioned_role_ids[0]]
            else:
                ai_choice = "llama 3.3 70b (fastest)"
            
            await process_ai_response(message, ai_choice)

    await bot.process_commands(message)

async def process_ai_response(message, ai_choice):
    query = message.content.replace(f'<@!{bot.user.id}>', '').strip()
    for role in message.guild.me.roles:
        query = query.replace(f'<@&{role.id}>', '').strip()
    
    logger.info(f"IA choisie : {ai_choice}, Query : {query}")
    
    if ai_choice == "perplexity":
        response = await perplexity_response(query)
    elif ai_choice == "llama 3.3 70b (fastest)":
        response = cerebras_response(query)
    else:
        response = await pollinations_text_response(query, ai_choice)
    
    await message.channel.send(response)
    logger.info(f"Réponse envoyée pour {ai_choice} : {response}")

async def main():
    async with asyncio.TaskGroup() as tg:

        tg.create_task(bot.start(config["DISCORD_TOKEN"]))
        logger.info("Discord bot démarré")

if __name__ == "__main__":
    asyncio.run(main())
