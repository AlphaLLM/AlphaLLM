import asyncio
import logging
from dotenv import load_dotenv
import os
from colorama import Fore, Back, Style, init
from AlphaLLM.bot import AlphaLLMBot
from Logger.logger_bot import LoggerBot

# Initialisation de colorama
init(autoreset=True)

# Configuration du logging
class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.WHITE + Back.BLUE + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.INFO: Fore.BLACK + Back.GREEN + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.WARNING: Fore.BLACK + Back.YELLOW + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.ERROR: Fore.WHITE + Back.RED + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL,
        logging.CRITICAL: Fore.WHITE + Back.BLACK + Style.BRIGHT + '%(asctime)s - %(name)s - %(levelname)s - %(message)s' + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger('MAIN')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColoredFormatter())

logger.addHandler(console_handler)

async def main():
    load_dotenv()
    config = {key: os.getenv(key) for key in os.environ}

    # Initialisation des bots
    alphallm = AlphaLLMBot()
    logger_bot = LoggerBot()

    await asyncio.gather(
        alphallm.start(config["DISCORD_TOKEN"])
    )

if __name__ == "__main__":
    asyncio.run(main())
