import discord
from discord.ext import commands
import os, threading, asyncio, random
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
BAD_WORDS = ["puta","puto","maricon","gilipollas","cabron","mierda","imbecil","subnormal","retrasado"]
BOT_LOOP = None

def add_log(t):
    LOGS.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {t}")
    if len(LOGS) > 200: LOGS.pop()
    print(t)

def run_coro(coro):
    if BOT_LOOP and BOT_LOOP.is_running():
        asyncio.run_coroutine_threadsafe(coro, BOT_LOOP)

HTML = """
<style>
body{background:#0f0f0f;color:white;font-family:Arial;padding:15px;max-width:980px;margin:auto}
.card{background:#1e1e1e;padding:16px;border-radius:12px;margin-bottom:15px;border:1px solid #2a2a2a}
input,select,textarea{width:100%;padding:12px;margin:6px 0;background:#2a2a2a;color:white;border:none;border-radius:8px;box-sizing:border-box}
button{background:#5865F2;color:white;padding:12px;width:100%;border:none;border-radius:8px;cursor:pointer;font-weight:bold;margin-top:6px}
button.red{background:#ef4444}button.yellow{background:#eab308;color:black}button.green{background:#22c55e}button.orange{background:#f97316}button.black{background:#000;border:1px solid #ef4444}button.blue{background:#0ea5e9}
.logs{height:180px;overflow-y:auto;background:#000;padding:10px;border-radius:8px;font-family:monospace;font-size:11px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
</style>
<h1>🤖 Dalaluki-Bot - ONLINE 24/7</h1>
<div class="card">
<h3>Estado: {{'🟢 ONLINE' if bot.is_ready() else '🔴 OFFLINE'}} | <a href='/keepalive' style='color:#0ea5e9'>KeepAlive</a></h3>
<div class="logs">{{logs_html|safe}}</div>
<form action="/wake?pwd={{pwd}}" method="post"><button class="blue">🔋 ACTIVAR / MANTENER ONLINE AHORA</button></form>
<p style='font-size:11px;color:#888'>URL para UptimeRobot: {{url}}/keepalive</p>
</div>
<div class="grid">
<div class="card"><h3>🚨 LOCKDOWN - Solo se ve cuando esta cerrado</h3>
<form action="/lockdown?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<textarea name="reason" placeholder="Motivo del cierre..."></textarea>
<button class="black">🔒 BLOQUEAR TODO EL SERVIDOR</button></form>
<form action="/unlockdown?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<button class="green">🔓 DESBLOQUEAR Y BORRAR CANAL</button></form>
</div>
<div class="card"><h3>📢 Enviar / Moderacion</h3>
<form action="/send?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>{% endfor %}{% endfor %}</select><textarea name="msg" placeholder="Mensaje..."></textarea><button>Enviar</button></form>
<form action="/mod?pwd={{pwd}}" method="post"><select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select><input name="user_id" placeholder="ID usuario"><select name="action"><option value="ban">BAN</option><option value="kick">KICK</option><option value="mute">MUTE</option><option value="unmute">UNMUTE</option></select><button class="red">Ejecutar</button></form>
</div>
</div>
<div class="grid">
<div class="card"><h3>🎫 Tickets</h3><form action="/ticketpanel?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><button class="orange">Crear Panel Tickets</button></form></div>
<div class="card"><h3>🎁 Sorteo / Encuesta</h3><form action="/giveaway?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><input name="prize" placeholder="Premio"><button class="yellow">Sorteo</button></form></div>
</div>
"""

@app.route('/')
def home(): return f"OK - <a href='/panel?pwd={PASSWORD}'>Panel</a>"
@app.route('/keepalive')
def keepalive(): return "OK - Bot Alive", 200

@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    logs_html = "<br>".join(LOGS[:40]) if LOGS else "Sin logs"
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, logs_html=logs_html, url=request.host_url.rstrip('/'))

@app.route('/wake', methods=['POST'])
def wake():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    async def do():
        activity = discord.Streaming(name="Sigueme en YouTube, Twitch, X e Insta!", url=TWITCH_LINK)
        await bot.change_presence(activity=activity, status=discord.Status.online)
        add_log("🔋 Bot reactivado desde web")
    run_coro(do())
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/send', methods=['POST'])
def send_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    run_coro(ch.send(request.form['msg'])); add_log(f"📢 Mensaje a #{ch.name}")
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/mod', methods=['POST'])
def mod_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id'])); uid = int(request.form['user_id']); act = request.form['action']
    async def do():
        try:
            m = await g.fetch_member(uid)
            if act=="ban": await g.ban(m)
            elif act=="kick": await g.kick(m)
            elif act=="mute": await m.timeout(discord.utils.utcnow()+timedelta(minutes=10))
            else: await m.timeout(None)
            add_log(f"✅ {act} a {m}")
        except Exception as e: add_log(f"❌ {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/lockdown', methods=['POST'])
def lockdown_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id'])); reason = request.form.get('reason','Mantenimiento')
    async def do():
        # Buscar o crear canal que SOLO existe en lockdown
        lock_channel = discord.utils.get(g.text_channels, name="servidor-cerrado-temporalmente")
        if not lock_channel:
            overwrites = {
                g.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
                g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            for r in g.roles:
                if r.permissions.administrator:
                    overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
            lock_channel = await g.create_text_channel("Servidor-Cerrado-Temporalmente", overwrites=overwrites, topic="Solo visible durante lockdown")
        # Bloquear todo lo demas
        for c in g.channels:
            if c.id == lock_channel.id: continue
            try: await c.set_permissions(g.default_role, view_channel=False, reason=f"Lockdown: {reason}")
            except: pass
        embed = discord.Embed(title="🔒 Servidor Cerrado Temporalmente", description=f"**Motivo:** {reason}\n\nEste es el UNICO canal visible. El resto del server esta oculto.\nSolo Admins pueden escribir aqui.", color=discord.Color.red(), timestamp=datetime.now())
        await lock_channel.send(embed=embed)
        add_log(f"🚨 LOCKDOWN en {g.name}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/unlockdown', methods=['POST'])
def unlockdown_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id']))
    async def do():
        for c in g.channels:
            try: await c.set_permissions(g.default_role, overwrite=None, reason="Fin Lockdown")
            except: pass
        ch = discord.utils.get(g.text_channels, name="servidor-cerrado-temporalmente")
        if ch:
            await ch.send("🔓 Servidor reabierto, borrando canal en 3s...")
            await asyncio.sleep(3)
            await ch.delete(reason="Fin lockdown")
        add_log(f"🔓 UNLOCK en {g.name}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/ticketpanel', methods=['POST'])
def ticketpanel_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    run_coro(ch.send(embed=discord.Embed(title="🎫 Soporte", description="Clica para abrir ticket", color=0x22c55e), view=TicketView()))
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/giveaway', methods=['POST'])
def giveaway_route():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    prize = request.form['prize']
    async def do():
        embed = discord.Embed(title="🎉 SORTEO", description=f"Premio: **{prize}**\nReacciona 🎉", color=discord.Color.gold())
        msg = await ch.send(embed=embed); await msg.add_reaction("🎉")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_final_v2")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True), interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        for r in interaction.guild.roles:
            if r.permissions.administrator: overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(f"{interaction.user.mention}", view=CloseView())
        await interaction.response.send_message(f"Ticket {ch.mention}", ephemeral=True)

class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Cerrar", style=discord.ButtonStyle.red, custom_id="close_ticket_final_v2")
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
    if m.author.bot:
        await bot.process_commands(m); return
    for bad in BAD_WORDS:
        if bad in m.content.lower():
            try: await m.delete(); return
            except: pass
    await bot.process_commands(m)

@bot.command()
async def redes(ctx):
    embed = discord.Embed(title="🔗 Redes Dalaluki", color=0xFF0000)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="YouTube", url=YT_LINK, emoji="🔴"))
    view.add_item(discord.ui.Button(label="Twitch", url=TWITCH_LINK, emoji="💜"))
    view.add_item(discord.ui.Button(label="X", url=X_LINK, emoji="🐦"))
    view.add_item(discord.ui.Button(label="Instagram", url=INSTA_LINK, emoji="📸"))
    await ctx.send(embed=embed, view=view)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
