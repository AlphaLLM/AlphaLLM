import discord
import logging
from dotenv import load_dotenv
import os

load_dotenv()
config = {
    key: os.getenv(key)
    for key in os.environ
}
logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
    @bot.tree.command(name="contact", description="Envoie un message au développeur")
    async def contact(interaction: discord.Interaction, message: str):
        logger.info(f"Commande contact exécutée par {interaction.user.display_name}")
        dev_id = config["DEV_ID"]
        dev_user = await bot.fetch_user(dev_id)
        await dev_user.send(f"Message de <@{interaction.user.id}>: {message}")
        await interaction.response.send_message("Votre message a été envoyé au développeur.", ephemeral=True)