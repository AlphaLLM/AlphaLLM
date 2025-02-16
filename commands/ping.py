import discord
import logging
from db_manager import DatabaseManager

logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
    @bot.tree.command(name="ping", description="Affiche la latence du bot")
    async def ping(interaction: discord.Interaction):
        latence = round(bot.latency * 1000)

        if latence < 100:
            color = discord.Color.green()
        elif latence < 200:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()

        embed = discord.Embed(
                title=f"Latence : {latence} ms",
                color=color,
                timestamp=discord.utils.utcnow()
            )
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        logger.info(f"Commande ping exécutée par {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
