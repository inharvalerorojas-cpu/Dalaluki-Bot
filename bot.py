import discord
from discord.ext import commands
import os
from flask import Flask
import threading
from datetime import timedelta

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

@bot.event
async def on_ready():
    print(f"✅ {bot.user} conectado 24/7")

@bot.command()
async def ping(ctx):
    await ctx.send("¡Estoy ON 24/7!")

# --- MODERACIÓN ---
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sin razón"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} baneado | Razón: {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sin razón"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} kickeado | Razón: {reason}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutos: int = 10, *, reason="Sin razón"):
    # Mute con timeout de Discord (el oficial)
    duration = timedelta(minutes=minutos)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"🔇 {member.mention} muteado por {minutos} min | Razón: {reason}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} desmuteado")

@bot.command()
@commands.has_permissions(administrator=True)
async def lockdown(ctx):
    for channel in ctx.guild.channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        except:
            pass
    await ctx.send("🔒 Servidor en lockdown")

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    for channel in ctx.guild.channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        except:
            pass
    await ctx.send("🔓 Servidor abierto")

bot.run(TOKEN)
