import discord
from discord.ext import commands, tasks
import asyncio
from AlphaLLM.commands.commands import setup_commands
from AlphaLLM.utils.cerebras_api import cerebras_response
from utils.polli_text_model import pollinations_text_response, get_available_models
from utils.pplx import perplexity_response
import os
import json

class AlphaLLMBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        self.VERSION = "3.1"
        self.STATUSES = [
            "/help pour les commandes",
            "@AlphaLLM pour discuter",
            "/image pour créer des images",
            f"Version {self.VERSION} en ligne"
        ]
        self.current_status_index = 0
        self.ROLES_FILE = 'roles.json'
        self.ROLE_CREATION_DELAY = 1
        self.role_model_mapping = {}

    async def setup_hook(self):
        self.change_status.start()
        setup_commands(self)
        await self.create_model_roles()
        await self.tree.sync()

    @tasks.loop(seconds=15)
    async def change_status(self):
        current_status = self.STATUSES[self.current_status_index]
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=current_status,
            )
        )
        self.current_status_index = (self.current_status_index + 1) % len(self.STATUSES)

    async def on_ready(self):
        print(f'{self.user} est connecté à Discord!')

    async def on_message(self, message):
        if not message.author.bot:
            mentioned_role_ids = [str(role.id) for role in message.role_mentions if str(role.id) in self.role_model_mapping]
            
            if self.user.mentioned_in(message) or mentioned_role_ids:
                ai_choice = self.role_model_mapping[mentioned_role_ids[0]] if mentioned_role_ids else "llama 3.3 70b (fastest)"
                await self.process_ai_response(message, ai_choice)

        await self.process_commands(message)

    async def process_ai_response(self, message, ai_choice):
        query = message.content.replace(f'<@!{self.user.id}>', '').strip()
        for role in message.guild.me.roles:
            query = query.replace(f'<@&{role.id}>', '').strip()
        
        if ai_choice == "perplexity":
            response = await perplexity_response(query)
        elif ai_choice == "llama 3.3 70b (fastest)":
            response = cerebras_response(query)
        else:
            response = await pollinations_text_response(query, ai_choice)
        
        view = RegenerateView(ai_choice, query)
        await message.channel.send(response, view=view)

    async def create_model_roles(self):
        self.role_model_mapping = self.load_roles()
        
        for guild in self.guilds:
            bot_member = guild.get_member(self.user.id)
            models = list(await get_available_models())
            models.extend(["perplexity", "llama 3.3 70b (fastest)"])

            for model in models:
                role_name = model.capitalize()
                existing_role = discord.utils.get(guild.roles, name=role_name)
            
                if existing_role:
                    if str(existing_role.id) not in self.role_model_mapping:
                        self.role_model_mapping[str(existing_role.id)] = model.lower()
                    if existing_role not in bot_member.roles:
                        await bot_member.add_roles(existing_role)
                elif str(guild.id) not in self.role_model_mapping.get(model.lower(), {}):
                    try:
                        new_role = await guild.create_role(
                            name=role_name,
                            colour=discord.Colour(0xffffff),
                            mentionable=True
                        )
                        await bot_member.add_roles(new_role)
                        self.role_model_mapping[str(new_role.id)] = model.lower()
                        await asyncio.sleep(self.ROLE_CREATION_DELAY)
                    except discord.Forbidden:
                        print(f"Permission insuffisante pour créer le rôle {role_name}")
                    except discord.HTTPException as e:
                        print(f"Erreur HTTP lors de la création du rôle {role_name}: {e}")

        self.save_roles()

    def load_roles(self):
        if os.path.exists(self.ROLES_FILE):
            with open(self.ROLES_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_roles(self):
        with open(self.ROLES_FILE, 'w') as f:
            json.dump(self.role_model_mapping, f)

class RegenerateView(discord.ui.View):
    def __init__(self, ai_choice, query):
        super().__init__(timeout=None)
        self.ai_choice = ai_choice
        self.query = query

    @discord.ui.button(label="🔄️ Régénérer", style=discord.ButtonStyle.primary)
    async def regenerate(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ai_choice == "perplexity":
            response = await perplexity_response(self.query)
        elif self.ai_choice == "llama 3.3 70b (fastest)":
            response = cerebras_response(self.query)
        else:
            response = await pollinations_text_response(self.query, self.ai_choice)
        
        await interaction.response.send_message(response, view=self)
