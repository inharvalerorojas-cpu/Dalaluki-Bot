import discord
from discord.ext import commands
import os, threading, asyncio
from flask import Flask, request, render_template_string, redirect
from datetime import datetime
from collections import defaultdict

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "1234"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

MSG_COUNT = 0
USERS = defaultdict(int)

HTML = """
<style>body{background:#111;color:white;font-family:Arial;padding:20px}.card{background:#222;padding:15px;border-radius:10px;margin-bottom:15px} input,select,textarea{width:100%;padding:10px;margin:5px 0;background:#333;color:white;border:none;border-radius:5px} button{background:#5865F2;color:white;padding:10px;width:100%;border:none;border-radius:5px;cursor:pointer}</style>
<h1>🤖 Panel Dalaluki V3</h1>
<div class="card"><h3>📈 Stats: {{total}} miembros | {{msg}} msgs hoy</h3></div>

<div class="card"><h3>📢 Enviar mensaje</h3>
<form action="/send?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>{% endfor %}{% endfor %}</select>
<textarea name="msg" placeholder="Mensaje"></textarea><button>Enviar</button></form></div>

<div class="card"><h3>🔨 Ban / Kick</h3>
<form action="/mod?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<input name="user_id" placeholder="ID del usuario a banear">
<select name="action"><option value="ban">BAN</option><option value="kick">KICK</option></select>
<button style="background:red">Ejecutar</button></form></div>
"""

@app.route('/')
def home(): return f"Bot ON con {len(bot.guilds)} servers - /panel?pwd={PASSWORD}"
@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD: return "Mal pwd", 401
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
            if request.form['action'] == 'ban': await g.ban(m)
            else: await g.kick(m)
        except Exception as e: print(e)
    asyncio.run_coroutine_threadsafe(do(), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@bot.event
async def on_ready(): print(f"ON {bot.user}")

@bot.event
async def on_message(message):
    global MSG_COUNT
    if not message.author.bot:
        MSG_COUNT+=1
        USERS[message.author.id]+=1
    await bot.process_commands(message)

def run_web(): app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_web).start()
bot.run(TOKEN)
