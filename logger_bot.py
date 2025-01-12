import discord
import asyncio
import logging
from discord import app_commands
import json
from logger_commands import setup_logger_commands

class LoggerBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        
        self.tree = app_commands.CommandTree(self)
        
        with open('config.json', 'r+') as config_file:
            self.config = json.load(config_file)
            if 'LOG_LEVEL' not in self.config:
                self.config['LOG_LEVEL'] = 'DEBUG'
                config_file.seek(0)
                json.dump(self.config, config_file, indent=4)
                config_file.truncate()
        
        self.dev_id = self.config['dev_ids'][0]
        self.log_level = getattr(logging, self.config['LOG_LEVEL'])
        self.log_queue = asyncio.Queue()

    async def setup_hook(self):
        self.bg_task = self.loop.create_task(self.send_logs())
        setup_logger_commands(self)
        await self.tree.sync()
        
    async def on_ready(self):
        print(f'Logger bot connecté en tant que {self.user}')
        print(f"Commandes disponibles: {[cmd.name for cmd in self.tree.get_commands()]}")

    async def send_log(self, message):
        dev_user = await self.fetch_user(self.dev_id)
        await dev_user.send(message)

    async def send_logs(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                log_message = await asyncio.wait_for(self.log_queue.get(), timeout=1)
                if log_message[0] >= self.log_level:
                    await self.send_log(log_message[1])
            except asyncio.TimeoutError:
                pass

class DiscordHandler(logging.Handler):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.run_coroutine_threadsafe(self.bot.log_queue.put((record.levelno, log_entry)), asyncio.get_event_loop())

logger_bot = LoggerBot()
discord_handler = DiscordHandler(logger_bot)
discord_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')
logger.addHandler(discord_handler)

async def run_logger_bot():
    async with logger_bot:
        await logger_bot.start(logger_bot.config["LOGGER_BOT_TOKEN"])

if __name__ == "__main__":
    asyncio.run(run_logger_bot())
