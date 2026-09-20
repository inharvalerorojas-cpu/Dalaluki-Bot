import discord
from discord.ext import commands
import os, threading, asyncio
from flask import Flask, request, render_template_string, redirect

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "1234" # CAMBIA ESTO LUEGO

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

HTML = """
<h1>Panel Dalaluki</h1>
<form action="/send?pwd={{pwd}}" method="post">
<select name="channel_id">
{% for g in bot.guilds %}{% for c in g.text_channels %}
<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>
{% endfor %}{% endfor %}
</select><br><br>
<textarea name="msg" placeholder="Escribe mensaje"></textarea><br>
<button>Enviar como el Bot</button>
</form>
"""

@app.route('/')
def home(): return "Bot ON - ve a /panel?pwd=1234"

@app.route('/panel')
def panel():
    if request.args.get('pwd') != PASSWORD: return "Contraseña mal. Pon /panel?pwd=1234", 401
    return render_template_string(HTML, bot=bot, pwd=PASSWORD)

@app.route('/send', methods=['POST'])
def send():
    if request.args.get('pwd') != PASSWORD: return "No", 401
    channel_id = int(request.form['channel_id'])
    msg = request.form['msg']
    ch = bot.get_channel(channel_id)
    asyncio.run_coroutine_threadsafe(ch.send(msg), bot.loop)
    return f"Enviado a {ch.name}! <a href='/panel?pwd={PASSWORD}'>Volver</a>"

@bot.event
async def on_ready(): print(f"ON {bot.user}")

def run_web(): app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_web).start()
bot.run(TOKEN)
