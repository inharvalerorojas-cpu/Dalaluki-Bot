import discord
from discord.ext import commands
import os, threading, asyncio, random, requests, time
from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "dalaluki_1234"

YT_LINK = "https://www.youtube.com/@Dalaluki"
TWITCH_LINK = "https://www.twitch.tv/dalalukilegacy"
X_LINK = "https://x.com/dalaluki"
INSTA_LINK = "https://www.instagram.com/dalaluki"

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

LOGS = []
BAD_WORDS = ["puta","puto","maricon","gilipollas","cabron","mierda","imbecil","subnormal","retrasado","nigger","fuck"]
LOG_CHANNEL_ID = None
BOT_LOOP = None

def add_log(t):
    LOGS.insert(0, f"[{datetime.now().strftime('%d/%m %H:%M:%S')}] {t}")
    if len(LOGS) > 200: LOGS.pop()
    print(t)

async def send_log(guild, text):
    add_log(text)
    if LOG_CHANNEL_ID:
        ch = bot.get_channel(LOG_CHANNEL_ID)
        if ch:
            try: await ch.send(embed=discord.Embed(description=text, color=0x2b2d31, timestamp=datetime.now()))
            except: pass

def run_coro(coro):
    if BOT_LOOP and BOT_LOOP.is_running():
        asyncio.run_coroutine_threadsafe(coro, BOT_LOOP)

# --- MANTENER ONLINE 24/7 ---
def keep_alive_loop():
    while True:
        time.sleep(240) # cada 4 min se hace ping solo
        try:
            url = os.getenv("RENDER_EXTERNAL_URL")
            if url:
                requests.get(url + "/keepalive", timeout=10)
                add_log("🔋 Auto-ping para mantener online")
        except: pass

threading.Thread(target=keep_alive_loop, daemon=True).start()

HTML = """
<style>
body{background:#0f0f0f;color:white;font-family:Arial;padding:15px;max-width:980px;margin:auto}
.card{background:#1e1e1e;padding:16px;border-radius:12px;margin-bottom:15px;border:1px solid #2a2a2a}
input,select,textarea{width:100%;padding:12px;margin:6px 0;background:#2a2a2a;color:white;border:none;border-radius:8px;box-sizing:border-box}
button{background:#5865F2;color:white;padding:12px;width:100%;border:none;border-radius:8px;cursor:pointer;font-weight:bold;margin-top:6px}
button.red{background:#ef4444}button.yellow{background:#eab308;color:black}button.green{background:#22c55e}button.orange{background:#f97316}button.black{background:#000;border:1px solid #ef4444}button.blue{background:#0ea5e9}
h3{margin:0 0 10px 0;color:#a78bfa}.logs{height:200px;overflow-y:auto;background:#000;padding:10px;border-radius:8px;font-family:monospace;font-size:11px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style>
<h1>🤖 Dalaluki-Bot>
<div class="card">
<h3>Estado: {{'🟢 ONLINE' if bot.is_ready() else '🔴 OFFLINE'}} | <a href='/logs?pwd={{pwd}}' style='color:#22c55e'>Logs</a> | <a href='/keepalive' style='color:#0ea5e9'>KeepAlive OK</a></h3>
<div class="logs">{{logs_html|safe}}</div>
<form action="/wake?pwd={{pwd}}" method="post"><button class="blue">🔋 ACTIVAR / MANTENER ONLINE AHORA</button></form>
<p style='font-size:11px;color:#888'>Si el bot se cae, dale a este botón. Para que NUNCA se caiga, pon esta URL en UptimeRobot: {{url}}/keepalive</p>
</div>
<div class="grid">
<div class="card"><h3>📢 Mensaje</h3><form action="/send?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>{% endfor %}{% endfor %}</select><textarea name="msg" placeholder="Mensaje..."></textarea><button>Enviar</button></form></div>
<div class="card"><h3>🔨 Mod</h3><form action="/mod?pwd={{pwd}}" method="post"><select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select><input name="user_id" placeholder="ID usuario"><select name="action"><option value="ban">BAN</option><option value="kick">KICK</option><option value="mute">MUTE</option><option value="unmute">UNMUTE</option></select><button class="red">Ejecutar</button></form></div>
</div>
<div class="grid">
<div class="card"><h3>🚨 LOCKDOWN</h3><form action="/lockdown?pwd={{pwd}}" method="post"><select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select><textarea name="reason" placeholder="Motivo cierre..."></textarea><button class="black">🔒 BLOQUEAR TODO</button></form><form action="/unlockdown?pwd={{pwd}}" method="post"><select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select><button class="green">🔓 DESBLOQUEAR</button></form></div>
<div class="card"><h3>🎫 Otros</h3><form action="/ticketpanel?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><button class="orange">Crear Panel Tickets</button></form><form action="/giveaway?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><input name="prize" placeholder="Premio"><input name="minutes" type="number" value="1"><button class="yellow">Sorteo</button></form></div>
</div>
"""

@app.route('/')
def home(): return f"BOT {'ONLINE' if bot.is_ready() else 'OFFLINE'} - <a href='/panel?pwd={PASSWORD}'>Panel</a>"
@app.route('/keepalive')
def keepalive(): return "OK - Bot Alive", 200

@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    logs_html = "<br>".join(LOGS[:30]) if LOGS else "Sin logs"
    base_url = request.host_url.rstrip('/')
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, logs_html=logs_html, url=base_url)

@app.route('/wake', methods=['POST'])
def wake():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    async def do():
        try:
            activity = discord.Streaming(name="Sigueme en YouTube, Twitch, X e Insta!", url=TWITCH_LINK)
            await bot.change_presence(activity=activity, status=discord.Status.online)
            add_log("🔋 Bot reactivado manualmente desde la web")
        except Exception as e: add_log(f"❌ Wake error: {e}")
    run_coro(do())
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/logs')
def logs_page():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    return f"<body style='background:#000;color:#0f0;font-family:monospace;padding:20px'>{'<br>'.join(LOGS)}<br><br><a href='/panel?pwd={PASSWORD}' style='color:white'>Volver</a></body>"

@app.route('/send', methods=['POST'])
def send_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    run_coro(ch.send(request.form['msg']))
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/mod', methods=['POST'])
def mod_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id']))
    uid = int(request.form['user_id']); act = request.form['action']
    async def do():
        try:
            m = await g.fetch_member(uid)
            if act=="ban": await g.ban(m)
            elif act=="kick": await g.kick(m)
            elif act=="mute": await m.timeout(discord.utils.utcnow()+timedelta(minutes=10))
            else: await m.timeout(None)
            add_log(f"✅ {act} {m}")
        except Exception as e: add_log(f"❌ MOD {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/lockdown', methods=['POST'])
def lockdown_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id'])); reason = request.form.get('reason','Emergencia')
    async def do():
        try:
            lock_channel = discord.utils.get(g.text_channels, name="servidor-cerrado-temporalmente")
            if not lock_channel:
                overwrites = {g.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False), g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
                for r in g.roles:
                    if r.permissions.administrator: overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                lock_channel = await g.create_text_channel("Servidor-Cerrado-Temporalmente", overwrites=overwrites)
            for ch in g.channels:
                if ch.id == lock_channel.id: continue
                try: await ch.set_permissions(g.default_role, view_channel=False, reason=reason)
                except: pass
            embed = discord.Embed(title="🔒 SERVIDOR CERRADO", description=f"*Motivo:* {reason}\n\nSolo este canal está visible. Solo admins pueden escribir.", color=discord.Color.red(), timestamp=datetime.now())
            await lock_channel.send(embed=embed)
            add_log("✅ LOCKDOWN activado - Solo canal cerrado visible")
        except Exception as e: add_log(f"❌ LOCKDOWN {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/unlockdown', methods=['POST'])
def unlockdown_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id']))
    async def do():
        try:
            for ch in g.channels:
                try: await ch.set_permissions(g.default_role, overwrite=None)
                except: pass
            ch = discord.utils.get(g.text_channels, name="servidor-cerrado-temporalmente")
            if ch: await ch.delete()
            add_log("✅ UNLOCK - Todo restaurado y canal borrado")
        except Exception as e: add_log(f"❌ UNLOCK {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/ticketpanel', methods=['POST'])
def ticketpanel_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    run_coro(ch.send(embed=discord.Embed(title="🎫 Soporte", description="Abre ticket", color=discord.Color.green()), view=TicketView()))
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/giveaway', methods=['POST'])
def giveaway_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id'])); prize = request.form['prize']; mins = int(request.form['minutes'] or 1)
    async def do():
        embed = discord.Embed(title="🎉 SORTEO", description=f"Premio: {prize}", color=discord.Color.gold())
        msg = await ch.send(embed=embed); await msg.add_reaction("🎉"); await asyncio.sleep(mins*60)
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

class TicketView(discord.ui.View):
    def _init(self): super().init_(timeout=None)
    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_final")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True), interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        for r in interaction.guild.roles:
            if r.permissions.administrator: overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(f"{interaction.user.mention}", view=CloseView())
        await interaction.response.send_message(f"Ticket {ch.mention}", ephemeral=True)

class CloseView(discord.ui.View):
    def _init(self): super().init_(timeout=None)
    @discord.ui.button(label="🔒 Cerrar", style=discord.ButtonStyle.red, custom_id="close_ticket_final")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cerrando..."); await asyncio.sleep(2); await interaction.channel.delete()

@bot.event
async def on_ready():
    global BOT_LOOP
    BOT_LOOP = asyncio.get_running_loop()
    bot.add_view(TicketView()); bot.add_view(CloseView())
    await bot.change_presence(activity=discord.Streaming(name="Sigueme en YouTube, Twitch, X e Insta!", url=TWITCH_LINK))
    add_log(f"✅ ONLINE {bot.user}")

@bot.event
async def on_message(m):
    if m.author.bot: await bot.process_commands(m); return
    for bad in BAD_WORDS:
        if bad in m.content.lower():
            try: await m.delete(); return
            except: pass
    await bot.process_commands(m)

@bot.command()
async def redes(ctx):
    embed = discord.Embed(title="🔗 Redes Dalaluki", color=0xFF0000)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="YouTube", url=YT_LINK))
    view.add_item(discord.ui.Button(label="Twitch", url=TWITCH_LINK))
    view.add_item(discord.ui.Button(label="X", url=X_LINK))
    view.add_item(discord.ui.Button(label="Instagram", url=INSTA_LINK))
    await ctx.send(embed=embed, view=view)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if _name_ == "_main_":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
