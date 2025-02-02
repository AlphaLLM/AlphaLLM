import discord
import asyncio
import logging
from discord.ext import commands
import os
from dotenv import load_dotenv

class LoggerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix='!', intents=intents)
        
        load_dotenv()
        self.dev_id = int(os.getenv('DEV_IDS'))
        self.log_channel_id = int(os.getenv('LOG_CHANNEL'))
        self.log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f'Connecté en tant que {self.user}')

    @commands.command()
    async def set_log_level(self, ctx, level: str):
        if ctx.author.id != self.dev_id:
            return await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
        try:
            self.log_level = getattr(logging, level.upper())
            await ctx.send(f"Niveau de log défini sur {level.upper()}")
        except AttributeError:
            await ctx.send("Niveau de log invalide.")

class DiscordHandler(logging.Handler):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.send_log(record.levelno, log_entry))

    async def send_log(self, level, message):
        if level >= self.bot.log_level:
            try:
                dev_user = await self.bot.fetch_user(self.bot.dev_id)
                await dev_user.send(message)
            except:
                pass

            try:
                channel = self.bot.get_channel(self.bot.log_channel_id)
                if channel:
                    await channel.send(message)
            except:
                pass

bot = LoggerBot()

discord_handler = DiscordHandler(bot)
discord_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LOGGER')
logger.addHandler(discord_handler)

@bot.tree.command(name="log")
async def log_command(interaction: discord.Interaction, message: str):
    logger.info(f"Log manuel : {message}")
    await interaction.response.send_message("Log envoyé avec succès.")

bot.run(os.getenv('LOGGER_BOT_TOKEN'))
