import discord
import asyncio
import random
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

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
    embed.add_field(name="**Commandes Générales**", value="Voici les commandes que tout le monde peut utiliser.", inline=False)
    embed.add_field(name="!ping", value="Affiche la latence du bot.", inline=False)
    embed.add_field(name="!say", value="Fait dire quelque chose au bot.", inline=False)
    embed.add_field(name="!help", value="Affiche l'ensemble des commandes présentes.", inline=False)
    embed.add_field(name="!support", value="Pour demander de l'aide.", inline=False)

    button = Button(label="Voir les commandes Admin", style=discord.ButtonStyle.primary)

    async def button_callback(interaction: discord.Interaction):
        # Modifie l'embed avec les commandes administratives
        admin_embed = discord.Embed(title="Help - Commandes Administratives", description=f"Commandes administratives", color=0x800080)
        admin_embed.add_field(name="!lock", value="Verrouille le chanel actuel.", inline=False)
        admin_embed.add_field(name="!unlock", value="Déverrouille le chanel actuel.", inline=False)
        admin_embed.add_field(name="!setactivity", value=f"Permet de changer directement le status de {bot.user.name}.", inline=False)
        admin_embed.add_field(name="!nuke", value=f"Permet de supprimer l'entièreté des messages d'un channel.", inline=False)
        admin_embed.add_field(name="!serverinfo", value="Affiche les informations du serveur.", inline=False)
        admin_embed.add_field(name="!ban", value="Sert à bannir un utilisateur du serveur.", inline=False)
        admin_embed.add_field(name="!unban", value="Sert à débannir un utilisateur du serveur.", inline=False)
        admin_embed.add_field(name="!mute", value="Permet de mute un utilisateur.", inline=False)
        admin_embed.add_field(name="!unmute", value="Permet de unmute un utilisateur.", inline=False)
        
        await interaction.response.edit_message(embed=admin_embed, view=None)
    button.callback = button_callback

    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

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
    await ctx.channel.purge()
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
@bot.command()
async def support(ctx: commands.Context) -> discord.Message:
    embed = discord.Embed(title="Support", description=f"Pour obtenir de l'aide, vous pouvez rejoindre le serveur Discord de Solara :", color=0x800080)
    embed.add_field(name="Serveur Discord Officiel", value="[Discord Officiel](https://discord.gg/Utrd4893M8)")
    embed.set_image(url="https://64.media.tumblr.com/c3ef835b5aa64778be2a3265bb5ef692/f0b242a57b5ffae2-76/s640x960/ec64b729b5ddbc22f9eb9f4ef729df7c75c72119.gif")
    return await ctx.send(embed=embed)

# Ban
@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    if ctx.author.guild_permissions.ban_members:
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member} a été banni avec succès !")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour bannir cet utilisateur.")
        except discord.HTTPException:
            await ctx.send("Une erreur s'est produite lors du bannissement.")
    else:
        await ctx.send("Tu n'as pas la permission de bannir des membres.")

# Unban

@bot.command()
async def unban(ctx, user: discord.User, *, reason=None):
    """Commande pour dé-bannir un membre du serveur"""
    if ctx.author.guild_permissions.ban_members:  # Vérifie si l'utilisateur a les permissions nécessaires
        try:
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"{user} a été débanni avec succès !")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour dé-bannir cet utilisateur.")
        except discord.HTTPException:
            await ctx.send("Une erreur s'est produite lors du dé-bannissement.")
    else:
        await ctx.send("Tu n'as pas la permission de dé-bannir des membres.")

# Mute
@bot.command()
async def mute(ctx, member: discord.Member, *, reason=None):
    if ctx.author.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="mute")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="mute", permissions=discord.Permissions.none())
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        try:
            await member.add_roles(muted_role, reason=reason)
            await ctx.send(f"{member} a été mute avec succès!")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour mute cet utilisateur.")
        except discord.HTTPException:
            await ctx.send("Une erreur s'est produite lors du mute.")

# Unmute
@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.author.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="mute")
        
        if not muted_role:
            await ctx.send("Le rôle 'mute' n'existe pas dans ce serveur.")
            return
        
        try:
            await member.remove_roles(muted_role, reason="Unmute")
            await ctx.send(f"{member} a été unmute avec succès!")
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour unmute cet utilisateur.")
        except discord.HTTPException:
            await ctx.send("Une erreur s'est produite lors du unmute.")
            
# Token
bot.run("")
