import os
from cerebras.cloud.sdk import Cerebras
import discord
from discord.ext import commands

# Configuration du client Cerebras
cerebras_client = Cerebras(
    api_key="csk-2wv2kthr94ht35cchdktmjyvkv9932cv9eptmjtypxjwntxy",
)

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord!')

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and not message.author.bot:
        # Utilisation de l'API Cerebras pour générer une réponse
        chat_completion = cerebras_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message.content,
                }
            ],
            model="llama3.3-70b",
        )
        
        # Extraction de la réponse générée
        response = chat_completion.choices[0].message.content
        
        # Envoi de la réponse sur Discord
        await message.channel.send(response)
    
    # Permet au bot de traiter les commandes en plus des mentions
    await bot.process_commands(message)

@bot.command()
async def ask(ctx, *, question):
    # Utilisation de l'API Cerebras pour générer une réponse
    chat_completion = cerebras_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model="llama3.3-70b",
    )
    
    # Extraction de la réponse générée
    response = chat_completion.choices[0].message.content
    
    # Envoi de la réponse sur Discord
    await ctx.send(response)

# Lancement du bot
bot.run('MTI4Njk1MTkwODc4Njk2MjQ0Mg.GIWIem.49hXLCecYHMQUA5i22odH39YX5nJhCjR1-l0aI')
