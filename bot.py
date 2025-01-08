"""
Module principal du bot Discord.

Ce module initialise et exécute le bot Discord principal ainsi que le bot de logging.
Il configure le logging, définit les événements du bot et gère l'exécution asynchrone.
"""

import discord
from discord.ext import commands
from commands import setup_commands
import logging
from cerebras_api import cerebras_response
import json
import asyncio
from logger_bot import LoggerBot, DiscordHandler
import re

# Configuration du logging
logger = logging.getLogger('discord_bot')
logger.setLevel(logging.DEBUG)

# Handler pour la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Handler pour Discord
logger_bot = LoggerBot()
discord_handler = DiscordHandler(logger_bot)
discord_handler.setLevel(logging.DEBUG)
logger.addHandler(discord_handler)

# Chargement des intents et configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Chargement de la configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Statut Discord modifiable
STATUS = "/help pour les commandes"

@bot.event
async def on_ready():
    """
    Événement déclenché lorsque le bot est prêt et connecté.
    Configure le statut du bot, synchronise les commandes et log la connexion.
    """
    await bot.change_presence(activity=discord.Game(STATUS))
    logger.info(f'{bot.user} est connecté à Discord!')
    setup_commands(bot)
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if not message.author.bot:
        logger.debug(f"Message reçu de {message.author}: {message.content}")
        if bot.user.mentioned_in(message):
            response = cerebras_response(message.content)
            for part in split_message(response):
                await message.channel.send(part)
            logger.info(f"Réponse envoyée dans {message.channel} à {message.author}")
        elif isinstance(message.channel, discord.DMChannel):
            response = cerebras_response(message.content)
            for part in split_message(response):
                await message.channel.send(part)
            logger.info(f"Réponse envoyée dans {message.channel} à {message.author}")
        else:
            await bot.process_commands(message)


def split_message(message, max_length=2000):
    parts = []
    while len(message) > max_length:
        split_index = max_length
        last_period = message.rfind('.', 0, max_length)
        last_exclamation = message.rfind('!', 0, max_length)
        last_question = message.rfind('?', 0, max_length)
        
        split_index = max(last_period, last_exclamation, last_question)
        
        if split_index == -1:
            split_index = max_length
        
        parts.append(message[:split_index + 1].strip())
        message = message[split_index + 1:].lstrip()

    parts.append(message)
    return parts


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """
    Gestionnaire d'erreurs pour les commandes d'application (slash commands).
    Log l'erreur et envoie un message d'erreur à l'utilisateur.

    Args:
        interaction (discord.Interaction): L'interaction qui a causé l'erreur.
        error (discord.app_commands.AppCommandError): L'erreur survenue.
    """
    logger.error(f"Erreur lors de l'exécution de la commande {interaction.command.name}: {str(error)}")
    await interaction.response.send_message(f"Une erreur s'est produite: {str(error)}", ephemeral=True)

async def main():
    """
    Fonction principale asynchrone.
    Démarre le bot de logging et le bot Discord principal.
    """
    async with asyncio.TaskGroup() as tg:
        tg.create_task(logger_bot.start(config["LOGGER_BOT_TOKEN"]))
        print("Logger bot démarré")
        tg.create_task(bot.start(config["DISCORD_TOKEN"]))
        print("Discord bot démarré")

if __name__ == "__main__":
    asyncio.run(main())
