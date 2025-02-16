import discord
from discord import app_commands
import logging

logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
    @bot.tree.command(name="guild-info", description="Affiche les infos complètes du serveur")
    async def guild_info(interaction: discord.Interaction):
        try:
            guild = interaction.guild
            created_at = int(guild.created_at.timestamp())

            logger.info(f"Commande guild-info exécutée par {interaction.user.display_name}")

            embed = discord.Embed(
                title=f"Informations sur le serveur : {guild.name}",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Demandé par {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

            info_general = ""
            info_general += f"Propriétaire : <@{guild.owner_id}>"
            info_general += f"\nID du serveur : {guild.id}"
            info_general += f"\nCréé le : <t:{created_at}:F>"
            info_general += f"\nVérification : {(str(guild.verification_level)).capitalize()}"
            if guild.scheduled_events:
                info_general += f"\nÉvenements : {guild.scheduled_events}"

            embed.add_field(name="Informations générales :", value=info_general, inline=False)

            if guild.icon:
                icon_url = guild.icon.url
                icon_128 = icon_url.replace("?size=1024", "?size=128") if "?size=" in icon_url else f"{icon_url}?size=128"
                icon_256 = icon_url.replace("?size=1024", "?size=256") if "?size=" in icon_url else f"{icon_url}?size=256"
                icon_512 = icon_url.replace("?size=1024", "?size=512") if "?size=" in icon_url else f"{icon_url}?size=512"
                icon_1024 = icon_url if "?size=" in icon_url else f"{icon_url}?size=1024"
                embed.add_field(
                    name="Icône",
                    value=f"[128px]({icon_128}) | [256px]({icon_256}) | [512px]({icon_512}) | [1024px]({icon_1024})",
                    inline=True
                )
                embed.set_thumbnail(url=icon_1024)
            else:
                embed.add_field(name="Icône", value="Aucune", inline=False)

            bots_count = 0
            humans_count = 0
            async for member in guild.fetch_members(limit=None):
                if member.bot:
                    bots_count += 1
                else:
                    humans_count += 1

            members_info = ""
            members_info += f"Membres : {str(guild.member_count)}"
            members_info += f"\nHumains : {str(humans_count)}"
            members_info += f"\nBots : {str(bots_count)}"
            embed.add_field(name="Membres", value=members_info, inline=False)

            channels_info = ""
            channels_info += f"Salons : {str(len(guild.channels))}"
            channels_info += f"\nSalons textuels : {str(len(guild.text_channels))}"
            channels_info += f"\nSalons vocaux : {str(len(guild.voice_channels))}"
            channels_info += f"\nSalons de forums : {str(len(guild.forums))}"
            channels_info += f"\nSalons de conférence : {str(len(guild.stage_channels))}"
            embed.add_field(name="Salons", value=channels_info, inline=False)

            roles_info = ""
            roles_info += f"Rôles : {str(len(guild.roles))}"
            embed.add_field(name="Rôles", value=roles_info, inline=False)

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de guild-info : {str(e)}")
            await interaction.response.send_message("Une erreur s'est produite lors de la récupération des informations du serveur.")
