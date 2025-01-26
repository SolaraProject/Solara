import discord
import asyncio
import random
from discord import app_commands
from discord.ext import commands

intents = discord.Intents().all()
intents.message_content = True
intents.members = True

intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f'{bot.user.name} est bien en ligne.')
    
    activities = ["!help", "https://github.com/SolaraProject", "Bot d'administration"]
    
    async def change_activity():
        while True:
            activity = random.choice(activities)
            await bot.change_presence(activity=discord.Game(name=activity))
            await asyncio.sleep(60)

    # Lancer la tâche de changement d'activité
    bot.loop.create_task(change_activity())

    await bot.tree.sync()

# Ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! _Latence_: {bot.latency * 1000:.2f} ms")

# Say
@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)
    await ctx.message.delete()

# Lock
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"Le canal {ctx.channel.mention} a été verrouillé.")

# Unlock
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"Le canal {ctx.channel.mention} a été déverrouillé.")

# Help
@bot.command()
async def help(ctx: commands.Context) -> discord.Message:
    embed = discord.Embed(title="Help", description=f"Voici la liste des commandes de {bot.user.name}", color=0x800080)
    embed.add_field(name="!ping", value="Affiche la latence du bot.", inline=False)
    embed.add_field(name="!say", value="Fait dire quelque chose au bot.", inline=False)
    embed.add_field(name="!lock", value="Verrouille le chanel actuel.", inline=False)
    embed.add_field(name="!unlock", value="Déverrouille le chanel actuel.", inline=False)
    embed.add_field(name="!help", value="Affiche l'ensemble des commandes présentes.", inline=False)
    embed.add_field(name="!setactivity", value=f"Permet de changer directement le status de {bot.user.name}.", inline=False)
    embed.add_field(name="!nuke", value=f"Permet de supprimer l'entièreté des messages d'un channel", inline=False)
    embed.add_field(name="!serverinfo", value="Affiche les informations du serveur", inline=False)
    embed.add_field(name="!support", value="Pour demander de l'aide", inline=False)
    return await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setactivity(ctx, activity_type: str, *, activity: str):
    if activity_type.lower() == "joue":
        await bot.change_presence(activity=discord.Game(name=activity))
    elif activity_type.lower() == "regarde":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
    elif activity_type.lower() == "écoute":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))
    else:
        await ctx.send("Type d'activité non reconnu. Utilisez 'joue', 'regarde' ou 'écoute'.")
        return
    await ctx.send(f"Activité du bot changée en : {activity_type} {activity}")

# Nuke
@bot.command()
@commands.has_permissions(manage_messages=True)
async def nuke(ctx):
    await ctx.channel.purge()  # Supprime tous les messages dans le canal
    channel_name = ctx.channel.name
    await ctx.send(f"le channel {channel_name} a bien été nuke.")

# Server Info
@bot.command()
@commands.has_permissions(administrator=True)
async def serverinfo(ctx):
    async def update_embed():
        guild = ctx.guild
        voice_count = sum(1 for member in guild.members if member.voice)
        
        embed = discord.Embed(title=f"Informations sur {guild.name}", color=0x800080)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Nombre de membres", value=guild.member_count, inline=False)
        embed.add_field(name="Membres en vocal", value=voice_count, inline=False)
        return embed

    message = await ctx.send(embed=await update_embed())

    # Rafraichissement des informations toutes les 5 minutes
    while True:
        await asyncio.sleep(300)
        try:
            await message.edit(embed=await update_embed())
        except discord.errors.NotFound:
            break

# Support
@bot.tree.command()
async def support(ctx: commands.Context) -> discord.Message:
    embed = discord.Embed(title="Support", description=f"Pour obtenir de l'aide, vous pouvez rejoindre le serveur Discord de Solara :", color=0x800080)
    embed.add_field(name="Serveur Discord Officiel", value="[Discord Officiel](https://discord.gg/Utrd4893M8)")
    embed.set_image(url="https://64.media.tumblr.com/c3ef835b5aa64778be2a3265bb5ef692/f0b242a57b5ffae2-76/s640x960/ec64b729b5ddbc22f9eb9f4ef729df7c75c72119.gif")
    return await ctx.send(embed=embed)









































































bot.run("")

