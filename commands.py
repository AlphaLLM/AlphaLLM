import discord
from discord import app_commands
from cerebras_api import cerebras_response
from pollinations import generate_image
from discord import File
from io import BytesIO
import json
import logging

logger = logging.getLogger('discord_bot')

with open('config.json') as config_file:
    config = json.load(config_file)

def setup_commands(bot: discord.Client):
    @bot.tree.command(name="ping", description="Affiche la latence du bot")
    async def ping(interaction: discord.Interaction):
        latence = round(bot.latency * 1000)
        logger.info(f"Commande ping exécutée par {interaction.user}")
        await interaction.response.send_message(f"Latence: {latence} ms")

    @bot.tree.command(name="infos", description="Affiche les informations sur le bot")
    async def infos(interaction: discord.Interaction):
        logger.info(f"Commande infos exécutée par {interaction.user}")
        await interaction.response.send_message(f"Je suis un bot Discord créé par <@{config['dev_ids'][0]}> pour interagir avec l'humanité. J'ai la capacité de générer des images à partir de prompts et de répondre à des questions.")

    @bot.tree.command(name="help", description="Affiche la liste des commandes disponibles")
    async def help_command(interaction: discord.Interaction):
        logger.info(f"Commande help exécutée par {interaction.user}")
        await interaction.response.send_message("Commandes disponibles : \n`/ping` : donne la latence du bot, \n`/infos` : montre les infos du bot, \n`/image` : génère une image grâce à Pollinations, \n`/contact` : envoie un message au développeur")

    @bot.tree.command(name="contact", description="Envoie un message au développeur")
    async def contact(interaction: discord.Interaction, message: str):
        logger.info(f"Commande contact exécutée par {interaction.user}")
        dev_id = config['dev_ids'][0]
        dev_user = await bot.fetch_user(dev_id)
        await dev_user.send(f"Message de <@{interaction.user.id}>: {message}")
        await interaction.response.send_message("Votre message a été envoyé au développeur.")

    @bot.tree.command(name="image", description="Génère une image à partir d'un prompt")
    @app_commands.choices(model=[
        app_commands.Choice(name="Flux", value="flux"),
        app_commands.Choice(name="Flux-Realism", value="flux-realism"),
        app_commands.Choice(name="Flux-Cablyai", value="flux-cablyai"),
        app_commands.Choice(name="Flux-Anime", value="flux-anime"),
        app_commands.Choice(name="Flux-3d", value="flux-3d"),
        app_commands.Choice(name="Any-Dark", value="any-dark"),
        app_commands.Choice(name="Flux-Pro", value="flux-pro"),
        app_commands.Choice(name="Turbo", value="turbo")
    ])
    async def image(
        interaction: discord.Interaction,
        prompt: str,
        model: str = "flux",
        seed: int = None,
        width: int = 1024,
        height: int = 1024,
        nologo: bool = True,
        private: bool = True,
        enhance: bool = False,
        safe: bool = False
    ):
        logger.info(f"Commande image exécutée par {interaction.user} avec : \nprompt: {prompt}\nmodèle: {model} \nseed: {seed} \ndimensions: {width}x{height} \nenhance: {enhance} \nsafe: {safe}")
        if width > 2048 or height > 2048:
            await interaction.response.send_message("Les dimensions de l'image doivent être inférieures ou égales à 2048x2048.")
            logger.error(f"Dimensions de l'image trop grandes pour {interaction.user}")
            return
        
        image_data = await generate_image(prompt, model, seed, width, height, nologo, private, enhance, safe)
        if image_data:
            file = discord.File(BytesIO(image_data), filename="generated_image.png")
            await interaction.followup.send(file=file)
            logger.info(f"Image générée et envoyée à {interaction.user}")
        else:
            await interaction.followup.send("Impossible de générer l'image.")
            logger.error(f"Échec de la génération d'image pour {interaction.user}")
