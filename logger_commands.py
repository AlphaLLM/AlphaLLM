import discord
from discord import app_commands
import json
import logging

logger = logging.getLogger('logger_bot')

with open('config.json') as config_file:
    config = json.load(config_file)

def setup_logger_commands(bot: discord.Client):
    @bot.tree.command(name="logging-level", description="Définir le niveau de log")
    @app_commands.choices(level=[
        app_commands.Choice(name="DEBUG", value="DEBUG"),
        app_commands.Choice(name="INFO", value="INFO"),
        app_commands.Choice(name="WARNING", value="WARNING"),
        app_commands.Choice(name="ERROR", value="ERROR"),
        app_commands.Choice(name="CRITICAL", value="CRITICAL")
    ])
    async def logging_level(interaction: discord.Interaction, level: str):
        bot.log_level = getattr(logging, level)
        config['LOG_LEVEL'] = level
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        logger.info(f"Niveau de log changé à {level} par {interaction.user}")
        await interaction.response.send_message(f"Niveau de log défini sur {level}")

    @bot.tree.command(name="log-status", description="Affiche le statut actuel du logger")
    async def log_status(interaction: discord.Interaction):
        logger.info(f"Statut du logger demandé par {interaction.user}")
        await interaction.response.send_message(f"Niveau de log actuel : {logging.getLevelName(bot.log_level)}\n"
                                                f"Nombre de logs en attente : {bot.log_queue.qsize()}")
