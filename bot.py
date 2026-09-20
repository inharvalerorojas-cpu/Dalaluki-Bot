import discord
from discord.ext import commands
import os
from flask import Flask

app = Flask('')

# Esta es la web más simple
@app.route('/')
def home():
    return "<h1>Mi bot está ON ✅</h1><p>Si ves esto, la web funciona.</p>"

# Tu bot de discord
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Para que funcionen las dos cosas a la vez
import threading
def run_web():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_web).start()
bot.run(TOKEN)
