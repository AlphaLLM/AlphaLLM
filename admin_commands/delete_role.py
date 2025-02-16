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
    @bot.tree.command(name="delete-role", description="Supprime un rôle par son nom dans tous les serveurs")
    async def delete_role(interaction: discord.Interaction, role_name: str):
        logger.info(f"Commande delete_role exécutée par {interaction.user.display_name} pour le rôle {role_name}")
        if not str(interaction.user.id) == config["DEV_ID"]:
            await interaction.response.send_message("Vous n'avez pas la permission d'exécuter cette commande administrateur.", ephemeral=True)
            return
        deleted_count = 0
        failed_count = 0

        for guild in bot.guilds:
            try:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await role.delete(reason=f"Supprimé par la commande /delete_role de {interaction.user.display_name}")
                    logger.info(f"Rôle {role_name} supprimé du serveur {guild.name}")
                    deleted_count += 1
                else:
                    logger.warning(f"Rôle {role_name} non trouvé sur le serveur {guild.name}")
            except discord.Forbidden:
                logger.error(f"Permissions insuffisantes pour supprimer le rôle {role_name} sur le serveur {guild.name}")
                failed_count +=1
            except Exception as e:
                logger.error(f"Erreur lors de la suppression du rôle {role_name} sur le serveur {guild.name}: {e}")
                failed_count += 1

        await interaction.response.send_message(f"Suppression du rôle '{role_name}' terminée.\n"
                                                f"Succès: {deleted_count} serveurs\n"
                                                f"Échecs: {failed_count} serveurs", ephemeral=True)
