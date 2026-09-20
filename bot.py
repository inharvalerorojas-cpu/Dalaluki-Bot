import discord
from discord.ext import commands
import os, threading, asyncio, random
from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "dalaluki_1234"

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
button.red{background:#ef4444} button.yellow{background:#eab308;color:black} button.green{background:#22c55e}
h3{margin:0 0 10px 0;color:#a78bfa}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style>

<h1>🤖 Panel Dalaluki FINAL</h1>
<div class="card"><h3>📈 {{total}} miembros | {{msg}} msgs hoy</h3></div>

<div class="grid">
<div class="card"><h3>📢 Mensaje</h3>
<form action="/send?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<textarea name="msg" placeholder="Mensaje..."></textarea><button>Enviar</button></form></div>

<div class="card"><h3>🔨 Mod</h3>
<form action="/mod?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<input name="user_id" placeholder="ID Usuario">
<select name="action"><option value="ban">BAN</option><option value="kick">KICK</option><option value="mute">MUTE 10m</option><option value="unmute">UNMUTE</option></select>
<button class="red">Ejecutar</button></form></div>
</div>

<div class="grid">
<div class="card"><h3>🎁 Sorteo</h3>
<form action="/giveaway?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<input name="prize" placeholder="Premio: Nitro">
<input name="minutes" type="number" value="5" placeholder="Minutos">
<button class="yellow">Iniciar Sorteo</button></form></div>

<div class="card"><h3>📊 Encuesta</h3>
<form action="/poll?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<input name="q" placeholder="¿Qué jugamos?">
<input name="o1" placeholder="Opción 1">
<input name="o2" placeholder="Opción 2">
<button class="green">Crear Encuesta</button></form></div>
</div>
<p style="text-align:center;opacity:0.5">Panel protegido con dalaluki_1234</p>
"""

@app.route('/')
def home(): return f"Bot ON - /panel?pwd={PASSWORD}"
@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD: return "Contraseña mal", 401
    total = bot.guilds[0].member_count if bot.guilds else 0
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, total=total, msg=MSG_COUNT)

@app.route('/send', methods=['POST'])
def send():
    if request.args.get('pwd')!= PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id']))
    asyncio.run_coroutine_threadsafe(ch.send(request.form['msg']), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/mod', methods=['POST'])
def mod():
    if request.args.get('pwd')!= PASSWORD: return "No",401
    g=bot.get_guild(int(request.form['guild_id'])); uid=int(request.form['user_id'])
    async def do():
        try:
            m=await g.fetch_member(uid); act=request.form['action']
            if act=="ban": await g.ban(m)
            elif act=="kick": await g.kick(m)
            elif act=="mute": await m.timeout(timedelta(minutes=10))
            elif act=="unmute": await m.timeout(None)
        except Exception as e: print(e)
    asyncio.run_coroutine_threadsafe(do(), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/giveaway', methods=['POST'])
def giveaway():
    if request.args.get('pwd')!= PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id'])); prize=request.form['prize']; mins=int(request.form['minutes'] or 5)
    async def do():
        embed=discord.Embed(title="🎉 SORTEO", description=f"Premio: **{prize}**\nReacciona 🎉\nTermina en {mins} min", color=discord.Color.gold())
        msg=await ch.send(embed=embed); await msg.add_reaction("🎉")
        await asyncio.sleep(mins*60)
        msg=await ch.fetch_message(msg.id)
        users=[u async for u in msg.reactions[0].users() if not u.bot]
        if users: await ch.send(f"🎉 Ganador de **{prize}**: {random.choice(users).mention}!")
        else: await ch.send("Nadie participó")
    asyncio.run_coroutine_threadsafe(do(), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/poll', methods=['POST'])
def poll():
    if request.args.get('pwd')!= PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id']))
    async def do():
        q=request.form['q']; o1=request.form['o1']; o2=request.form['o2']
        embed=discord.Embed(title=f"📊 {q}", description=f"1️⃣ {o1}\n2️⃣ {o2}", color=discord.Color.blurple())
        msg=await ch.send(embed=embed)
        await msg.add_reaction("1️⃣"); await msg.add_reaction("2️⃣")
    asyncio.run_coroutine_threadsafe(do(), bot.loop)
    return redirect(f"/panel?pwd={PASSWORD}")

@bot.event
async def on_ready(): print(f"✅ FINAL ON {bot.user}")
@bot.event
async def on_message(m):
    global MSG_COUNT
    if not m.author.bot: MSG_COUNT+=1
    await bot.process_commands(m)

def run_web(): app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_web).start()
bot.run(TOKEN)
