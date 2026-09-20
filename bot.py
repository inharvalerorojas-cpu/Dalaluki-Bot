import discord
from discord.ext import commands
import os, threading, asyncio
from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "1234" # CAMBIA ESTO LUEGO A ALGO SEGURO

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

MSG_COUNT = 0
USERS = defaultdict(int)

HTML = """
<style>
body{background:#111;color:white;font-family:Arial;padding:15px;max-width:800px;margin:auto}
.card{background:#222;padding:16px;border-radius:12px;margin-bottom:15px;border:1px solid #333}
input,select,textarea{width:100%;padding:12px;margin:6px 0;background:#333;color:white;border:none;border-radius:8px;box-sizing:border-box}
button{background:#5865F2;color:white;padding:12px;width:100%;border:none;border-radius:8px;cursor:pointer;font-weight:bold;margin-top:6px}
button.red{background:#ef4444}
h3{margin:0 0 10px 0;color:#a78bfa}
</style>
<h1>🤖 Panel Dalaluki V3</h1>
<div class="card"><h3>📈 {{total}} miembros | {{msg}} msgs hoy</h3></div>

<div class="card"><h3>📢 Enviar mensaje</h3>
<form action="/send?pwd={{pwd}}" method="post">
<select name="channel_id">
{% for g in bot.guilds %}{% for c in g.text_channels %}
<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>
{% endfor %}{% endfor %}
</select>
<textarea name="msg" placeholder="Mensaje como el bot..."></textarea>
<button>Enviar</button>
</form></div>

<div class="card"><h3>🔨 Moderación</h3>
<form action="/mod?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<input name="user_id" placeholder="ID del usuario (click derecho > Copiar ID)">
<select name="action">
<option value="ban">BAN</option>
<option value="kick">KICK</option>
<option value="mute">MUTE 10m</option>
<option value="unmute">UNMUTE</option>
</select>
<button class="red">Ejecutar</button>
</form></div>
"""

@app.route('/')
def home():
    return f"Bot ON con {len(bot.guilds)} servers - ve a /panel?pwd={PASSWORD}"

@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD:
        return "Contraseña mal. Pon /panel?pwd=1234", 401
    total = bot.guilds[0].member_count if bot.guilds else 0
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, total=total, msg=MSG_COUNT)

@app.route('/send', methods=['POST'])
def send():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    asyncio.run_coroutine_threadsafe(ch.send(request.form['msg']), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/mod', methods=['POST'])
def mod():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id']))
    uid = int(request.form['user_id'])
    async def do():
        try:
            m = await g.fetch_member(uid)
            act = request.form['action']
            if act == 'ban':
                await g.ban(m, reason="Ban desde panel")
            elif act == 'kick':
                await g.kick(m, reason="Kick desde panel")
            elif act == 'mute':
                await m.timeout(timedelta(minutes=10), reason="Mute desde panel")
            elif act == 'unmute':
                await m.timeout(None)
            print(f"{act} ejecutado a {m}")
        except Exception as e:
            print(f"Error mod: {e}")
    asyncio.run_coroutine_threadsafe(do(), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@bot.event
async def on_ready():
    print(f"✅ ON {bot.user}")

@bot.event
async def on_message(message):
    global MSG_COUNT
    if not message.author.bot:
        MSG_COUNT += 1
        USERS[message.author.id] += 1
    await bot.process_commands(message)

def run_web():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_web).start()
bot.run(TOKEN)
