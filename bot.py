import discord
import json

# Charger le fichier config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialiser le client du bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

last_number = 0  # Variable pour suivre le dernier nombre compté

@client.event
async def on_ready():
    print(f'Bot connecté en tant que {client.user}')
    guild = client.get_guild(int(config['guild_id']))
    channel = guild.get_channel(int(config['channel_id']))
    print(f'Suivi du salon: {channel.name}')

@client.event
async def on_message(message):
    global last_number

    if message.channel.id != int(config['channel_id']):
        return  # Ignorer les messages hors du salon configuré

    if message.author.bot:
        return  # Ignorer les messages des bots

    try:
        current_number = int(message.content)  # Essayer de convertir le message en nombre
    except ValueError:
        return  # Si ce n'est pas un nombre, ignorer le message

    if current_number == last_number + 1:
        # Le nombre est correct
        await message.add_reaction('✅')  # Réaction verte
        last_number = current_number  # Mettre à jour le dernier nombre compté
    else:
        # Le nombre est incorrect
        await message.add_reaction('❌')  # Réaction rouge

client.run(config['token'])
