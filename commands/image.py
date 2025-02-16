import discord
from discord import app_commands
from cerebras_api import cerebras_response
from polli_image_model import generate_image
from io import BytesIO
import logging
from dotenv import load_dotenv
import random

logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
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
        width: int = 1024,
        height: int = 1024,
        nologo: bool = True,
        private: bool = True,
        enhance: bool = False,
        safe: bool = True
    ):
        logger.info(f"Commande image exécutée par {interaction.user.display_name}")
    
        if width > 2048 or height > 2048:
            await interaction.response.send_message("Les dimensions de l'image doivent être inférieures ou égales à 2048x2048.")
            logger.error(f"Dimensions de l'image trop grandes pour {interaction.user.display_name}")
            return

        await interaction.response.defer()

        seed = None
        safe = True if interaction.guild.nsfw_level == discord.NSFWLevel.default else safe
        image_data = await generate_image(prompt, model, seed, width, height, nologo, private, enhance, safe)
    
        if image_data:
            file = discord.File(BytesIO(image_data), filename="generated_image.png")
            view = RegenerateImageView(prompt, model, width, height, nologo, private, enhance, safe)
            await interaction.followup.send(file=file, view=view)
            logger.info(f"Image générée et envoyée à {interaction.user.display_name}")
        else:
            await interaction.followup.send("Impossible de générer l'image.")
            logger.error(f"Échec de la génération d'image pour {interaction.user.display_name}")

class RegenerateImageView(discord.ui.View):
    def __init__(self, prompt, model, width, height, nologo, private, enhance, safe):
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.width = width
        self.height = height
        self.nologo = nologo
        self.private = private
        self.enhance = enhance
        self.safe = safe

    @discord.ui.button(label="Régénérer", style=discord.ButtonStyle.primary)
    async def regenerate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        seed = random.randint(0, 1000000)
        image_data = await generate_image(self.prompt, self.model, seed, self.width, self.height, self.nologo, self.private, self.enhance, self.safe)
        
        if image_data:
            file = discord.File(BytesIO(image_data), filename="regenerated_image.png")
            await interaction.followup.send(file=file, view=self)
            logger.info(f"Image régénérée et envoyée à {interaction.user.display_name}")
        else:
            await interaction.followup.send("Impossible de régénérer l'image.")
            logger.error(f"Échec de la régénération d'image pour {interaction.user.display_name}")
