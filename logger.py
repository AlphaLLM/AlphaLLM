#logger.py

import logging
from colorama import Fore, Back, Style, init

init(autoreset=True)

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

def setup_logging(log_level, log_file):
    logger = logging.getLogger('AlphaLLM')
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())

    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
