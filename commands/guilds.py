import discord
from discord import app_commands
import logging

logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
    @bot.tree.command(name="guilds", description="Affiche la liste des serveurs où le bot est présent")
    async def guilds(interaction: discord.Interaction):
        guilds = bot.guilds
        logger.info(f"Commande guilds exécutée par {interaction.user.display_name}")

        embed = discord.Embed(
                title=f"Liste des serveurs :",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        for guild in guilds:     
            embed.add_field(name=guild.name, value=f"Propriétaire : <@{guild.owner_id}>\nID : {guild.id}", inline=False)
            icon_url = guild.icon.url if guild.icon else ""
        
        await interaction.response.send_message(embed=embed)
