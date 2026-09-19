import discord
from discord.ext import commands
import os
from flask import Flask
import threading
from datetime import timedelta, datetime

app = Flask('')
@app.route('/')
def home():
    return "Dalaluki Bot ON"
def run_web():
    app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_web).start()

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FUNCIÓN DE LOGS ---
async def send_log(guild, title, desc, color, user=None):
    # Busca canal llamado logs, registros, o audit-logs
    channel = discord.utils.get(guild.text_channels, name="logs") or \
              discord.utils.get(guild.text_channels, name="registros") or \
              discord.utils.get(guild.text_channels, name="audit-logs")
    if not channel:
        return
    embed = discord.Embed(title=title, description=desc, color=color, timestamp=datetime.now())
    if user:
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} conectado 24/7")

@bot.command()
async def ping(ctx):
    await ctx.send("!pong")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sin razón"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} baneado")
    await send_log(ctx.guild, "🔨 BAN", f"**Usuario:** {member.mention} ({member.id})\n**Mod:** {ctx.author.mention}\n**Razón:** {reason}", discord.Color.red(), ctx.author)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sin razón"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} kickeado")
    await send_log(ctx.guild, "👢 KICK", f"**Usuario:** {member.mention}\n**Mod:** {ctx.author.mention}\n**Razón:** {reason}", discord.Color.orange(), ctx.author)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutos: int = 10, *, reason="Sin razón"):
    duration = timedelta(minutes=minutos)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"🔇 {member.mention} muteado {minutos} min")
    await send_log(ctx.guild, "🔇 MUTE", f"**Usuario:** {member.mention}\n**Duración:** {minutos} min\n**Mod:** {ctx.author.mention}\n**Razón:** {reason}", discord.Color.dark_grey(), ctx.author)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} desmuteado")
    await send_log(ctx.guild, "🔊 UNMUTE", f"**Usuario:** {member.mention}\n**Mod:** {ctx.author.mention}", discord.Color.green(), ctx.author)

@bot.command()
@commands.has_permissions(administrator=True)
async def lockdown(ctx):
    for ch in ctx.guild.channels:
        try: await ch.set_permissions(ctx.guild.default_role, send_messages=False)
        except: pass
    await ctx.send("🔒 Lockdown activado")
    await send_log(ctx.guild, "🔒 LOCKDOWN", f"Activado por {ctx.author.mention}", discord.Color.red(), ctx.author)

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    for ch in ctx.guild.channels:
        try: await ch.set_permissions(ctx.guild.default_role, send_messages=True)
        except: pass
    await ctx.send("🔓 Servidor abierto")
    await send_log(ctx.guild, "🔓 UNLOCK", f"Abierto por {ctx.author.mention}", discord.Color.green(), ctx.author)

# Logs automaticos de mensajes borrados
@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    await send_log(message.guild, "🗑️ Mensaje Borrado", f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}\n**Contenido:**\n{message.content[:1000]}", discord.Color.light_grey(), message.author)

bot.run(TOKEN)
