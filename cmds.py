import os
import importlib
import logging
import discord

logger = logging.getLogger('AlphaLLM')

async def setup_commands(bot: discord.Client):
    commands_dir = 'commands'
    for filename in os.listdir(commands_dir):
        if filename.endswith('.py'):
            if filename == '__init__.py':
                continue
            module_name = f'{filename[:-3]}'
            try:
                module = importlib.import_module(f'{commands_dir}.{module_name}')
                if hasattr(module, 'setup'):
                    await module.setup(bot)
                    logger.info(f"Commande chargée depuis {filename}")
                else:
                    logger.warning(f"Le fichier {filename} n'a pas de fonction 'setup'")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {filename}: {e}")
                logger.exception(e)

    commands_dir = 'admin_commands'
    for filename in os.listdir(commands_dir):
        if filename.endswith('.py'):
            if filename == '__init__.py':
                continue
            module_name = f'{filename[:-3]}'
            try:
                module = importlib.import_module(f'{commands_dir}.{module_name}')
                if hasattr(module, 'setup'):
                    await module.setup(bot)
                    logger.info(f"Commande admin chargée depuis {filename}")
                else:
                    logger.warning(f"Le fichier {filename} n'a pas de fonction 'setup'")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {filename}: {e}")
                logger.exception(e)
