import discord
from discord.ext import commands
import json
import os

# Charger le fichier config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Charger ou initialiser les records
if os.path.exists('record.json'):
    with open('record.json') as record_file:
        records = json.load(record_file)
else:
    records = {"highest": 0}

# Initialiser le bot avec les intents appropriés
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

last_number = 0  # Variable pour suivre le dernier nombre compté
last_user = None  # Variable pour suivre le dernier utilisateur

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    await bot.tree.sync()

@bot.event
async def on_message(message):
    global last_number, last_user, records

    # Ignorer les messages du bot et hors du salon configuré
    if message.author.bot or message.channel.id != int(config['channel_id']):
        return

    content = message.content.strip()

    if content:
        try:
            current_number = int(content)  # Essayer de convertir le message en nombre
        except ValueError:
            return  # Si ce n'est pas un nombre, ignorer le message

        if current_number == last_number + 1:
            await message.add_reaction('✅')  # Réaction verte
            last_number = current_number  # Mettre à jour le dernier nombre compté
            last_user = message.author  # Mettre à jour le dernier utilisateur
            
            # Vérifier si le record est battu
            if last_number > records["highest"]:
                old_record = records["highest"]
                records["highest"] = last_number  # Mettre à jour le record
                # Annonce du nouveau record
                announcement_channel = bot.get_channel(int(config['channel_id']))  # Changez ceci si nécessaire
                await announcement_channel.send(f"Le record a été battu ! Il était à : {old_record} et maintenant il est à : {last_number} par {last_user.mention} !")
                # Enregistrer le nouveau record dans le fichier
                with open('record.json', 'w') as record_file:
                    json.dump(records, record_file)

        else:
            await message.add_reaction('❌')  # Réaction rouge
            # Créer l'embed pour l'erreur
            embed = discord.Embed(title="Erreur de Comptage", color=discord.Color.red())
            embed.add_field(name="Membre", value=message.author.mention, inline=False)
            embed.add_field(name="Nombre Tenté", value=current_number, inline=False)
            embed.add_field(name="Le record était à", value=records["highest"], inline=False)

            await message.channel.send(embed=embed)  # Envoyer l'embed d'erreur
            last_number = 0  # Réinitialiser le compteur
            last_user = None  # Réinitialiser le dernier utilisateur

    await bot.process_commands(message)  # Permet au bot de traiter les commandes

@bot.tree.command(name='compteur', description='Affiche l\'état actuel du compteur.')
async def compteur(interaction: discord.Interaction):
    embed = discord.Embed(title="État du Compteur", color=discord.Color.blue())
    embed.add_field(name="Dernier Nombre", value=str(last_number) if last_number else "0", inline=False)
    if last_user:
        embed.add_field(name="Dernier Utilisateur", value=last_user.mention, inline=False)
    else:
        embed.add_field(name="Dernier Utilisateur", value="Personne", inline=False)
    embed.add_field(name="Record", value=str(records["highest"]), inline=False)

    await interaction.response.send_message(embed=embed)

bot.run(config['token'])
