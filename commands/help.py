import discord
import logging

logger = logging.getLogger('AlphaLLM')

async def setup(bot: discord.Client):
    @bot.tree.command(name="help", description="Affiche la liste des commandes disponibles")
    async def help_command(interaction: discord.Interaction):
        logger.info(f"Commande help exécutée par {interaction.user.display_name}")
        cmds = "Commandes disponibles : "
        cmds += "\n- /ping : Affiche la latence du bot"
        cmds += "\n- /guilds : Affiche la liste des serveurs où le bot est présent"
        cmds += "\n- /guild-info : Affiche les infos complètes du serveur"
        cmds += "\n- /contact : Envoie un message au développeur"
        cmds += "\n- /help : Affiche la liste des commandes disponibles"
        cmds += "\n- /image : Génère une image basé sur le prompt donné"
        await interaction.response.send_message(cmds)