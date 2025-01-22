import discord
from discord.ext import commands, tasks
import logging
import asyncio
from commands import setup_commands
from cerebras_api import cerebras_response
from polli_text_model import pollinations_text_response, get_available_models
from pplx import perplexity_response
from logger_bot import LoggerBot, DiscordHandler
from dotenv import load_dotenv
import os

logger = logging.getLogger('discord_bot')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

logger_bot = LoggerBot()
discord_handler = DiscordHandler(logger_bot)
discord_handler.setLevel(logging.DEBUG)
logger.addHandler(discord_handler)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
config = {key: os.getenv(key) for key in os.environ}

STATUSES = [
    "/help pour les commandes",
    "@AlphaLLM pour discuter",
    "/image pour créer des images",
    "Version 3.0 en ligne"
]

current_status_index = 0

role_model_mapping = {}

async def create_model_roles(bot):
    global role_model_mapping
    role_model_mapping = {}  # Réinitialiser le dictionnaire à chaque démarrage
    
    for guild in bot.guilds:
        logger.info(f"Création et attribution des rôles pour {guild.name}")
        bot_member = guild.get_member(bot.user.id)
    
        models = list(await get_available_models())
        models.extend(["perplexity", "llama 3.3 70b (fastest)"])

        for model in models:
            role_name = model.capitalize()
            existing_role = discord.utils.get(guild.roles, name=role_name)
        
            if existing_role:
                logger.info(f"Le rôle {role_name} existe déjà")
                if existing_role not in bot_member.roles:
                    await bot_member.add_roles(existing_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
            else:
                try:
                    new_role = await guild.create_role(
                        name=role_name,
                        colour=discord.Colour(0xffffff),
                        mentionable=True
                    )
                    logger.info(f"Nouveau rôle créé : {role_name}")
                    await bot_member.add_roles(new_role)
                    logger.info(f"Rôle {role_name} attribué au bot")
                    existing_role = new_role
                except discord.Forbidden:
                    logger.error(f"Permission insuffisante pour créer le rôle {role_name}")
                    continue
                except discord.HTTPException as e:
                    logger.error(f"Erreur HTTP lors de la création du rôle {role_name}: {e}")
                    continue
            
            role_model_mapping[str(existing_role.id)] = model.lower()

    logger.info("Création et attribution des rôles terminées")
    logger.info(f"Mapping des rôles aux modèles : {role_model_mapping}")

@tasks.loop(seconds=15)
async def change_status():
    global current_status_index
    current_status = STATUSES[current_status_index]
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing,
        name=current_status,
        assets={
            'large_image': 'img1',
        }
    ))
    current_status_index = (current_status_index + 1) % len(STATUSES)
    logger.debug(f"Statut changé pour : {current_status}")

@bot.event
async def on_ready():
    logger.info(f'{bot.user} est connecté à Discord!')
    setup_commands(bot)
    await create_model_roles(bot)
    await bot.tree.sync()
    change_status.start()



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
    
    view = RegenerateView(ai_choice, query)
    await message.channel.send(response, view=view)
    logger.info(f"Réponse envoyée pour {ai_choice}")

class RegenerateView(discord.ui.View):
    def __init__(self, ai_choice, query):
        super().__init__(timeout=None)
        self.ai_choice = ai_choice
        self.query = query

    @discord.ui.button(label="Régénérer", style=discord.ButtonStyle.primary)
    async def regenerate(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"Régénération demandée pour {self.ai_choice}")
        if self.ai_choice == "perplexity":
            response = await perplexity_response(self.query)
        elif self.ai_choice == "llama 3.3 70b (fastest)":
            response = cerebras_response(self.query)
        else:
            response = await pollinations_text_response(self.query, self.ai_choice)
        
        await interaction.response.send_message(response, view=self)
        logger.info(f"Réponse régénérée envoyée pour {self.ai_choice}")

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(logger_bot.start(config["LOGGER_BOT_TOKEN"]))
        logger.info("Logger bot démarré")
        tg.create_task(bot.start(config["DISCORD_TOKEN"]))
        logger.info("Discord bot démarré")

if __name__ == "__main__":
    asyncio.run(main())
