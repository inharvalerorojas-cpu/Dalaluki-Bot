import discord
from discord.ext import commands
import os, threading, asyncio, random
from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "dalaluki_1234"

# --- TUS REDES ---
YT_LINK = "https://www.youtube.com/@Dalaluki"
TWITCH_LINK = "https://www.twitch.tv/dalalukilegacy"
X_LINK = "https://x.com/dalaluki"
INSTA_LINK = "https://www.instagram.com/dalaluki"

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

MSG_COUNT = 0
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
            try:
                embed = discord.Embed(description=text, color=0x2b2d31, timestamp=datetime.now())
                await ch.send(embed=embed)
            except: pass

def run_coro(coro):
    if BOT_LOOP and BOT_LOOP.is_running():
        asyncio.run_coroutine_threadsafe(coro, BOT_LOOP)

HTML = """
<style>
body{background:#0f0f0f;color:white;font-family:Arial;padding:15px;max-width:980px;margin:auto}
.card{background:#1e1e1e;padding:16px;border-radius:12px;margin-bottom:15px;border:1px solid #2a2a2a}
input,select,textarea{width:100%;padding:12px;margin:6px 0;background:#2a2a2a;color:white;border:none;border-radius:8px;box-sizing:border-box}
button{background:#5865F2;color:white;padding:12px;width:100%;border:none;border-radius:8px;cursor:pointer;font-weight:bold;margin-top:6px}
button.red{background:#ef4444}button.yellow{background:#eab308;color:black}button.green{background:#22c55e}button.orange{background:#f97316}button.black{background:#000;border:1px solid #ef4444}
h3{margin:0 0 10px 0;color:#a78bfa}.logs{height:220px;overflow-y:auto;background:#000;padding:10px;border-radius:8px;font-family:monospace;font-size:11px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style>
<h1>🤖 Dalaluki-Bot - FINAL + LOCKDOWN</h1>
<div class="card">
<h3>Estado: {{'🟢 ONLINE' if bot.is_ready() else '🔴 OFFLINE'}} | Loop: {{'OK' if loop_ok else 'FAIL'}} | <a href='/logs?pwd={{pwd}}' style='color:#22c55e'>Logs</a></h3>
<div class="logs">{{logs_html|safe}}</div>
</div>
<div class="grid">
<div class="card"><h3>📢 Enviar Mensaje</h3>
<form action="/send?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>{% endfor %}{% endfor %}</select>
<textarea name="msg" placeholder="Mensaje..."></textarea><button>Enviar</button></form></div>
<div class="card"><h3>🔨 Moderación</h3>
<form action="/mod?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<input name="user_id" placeholder="ID usuario">
<select name="action"><option value="ban">BAN</option><option value="kick">KICK</option><option value="mute">MUTE 10m</option><option value="unmute">UNMUTE</option></select>
<button class="red">Ejecutar</button></form></div>
</div>
<div class="grid">
<div class="card"><h3>🎁 Sorteo</h3>
<form action="/giveaway?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<input name="prize" placeholder="Premio"><input name="minutes" type="number" value="1"><button class="yellow">Sorteo</button></form></div>
<div class="card"><h3>📊 Encuesta</h3>
<form action="/poll?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<input name="q" placeholder="Pregunta"><input name="o1" placeholder="Op1"><input name="o2" placeholder="Op2"><button class="green">Encuesta</button></form></div>
</div>
<div class="grid">
<div class="card"><h3>🎫 Tickets</h3>
<form action="/ticketpanel?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<button class="orange">Crear Panel Tickets</button></form></div>
<div class="card"><h3>🚨 LOCKDOWN SERVIDOR</h3>
<form action="/lockdown?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<textarea name="reason" placeholder="Motivo del cierre: Ej: Raid masiva, mantenimiento..."></textarea>
<button class="black">🔒 BLOQUEAR TODO EL SERVIDOR</button></form>
<form action="/unlockdown?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<button class="green">🔓 DESBLOQUEAR SERVIDOR</button></form>
</div>
</div>
"""

@app.route('/')
def home(): return f"BOT {'ONLINE' if bot.is_ready() else 'OFFLINE'} - <a href='/panel?pwd={PASSWORD}'>Panel</a>"
@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    logs_html = "<br>".join(LOGS[:30]) if LOGS else "Sin logs"
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, logs_html=logs_html, loop_ok=BOT_LOOP is not None)
@app.route('/logs')
def logs_page():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    return f"<body style='background:#000;color:#0f0;font-family:monospace;padding:20px'><h2>LOGS</h2>{'<br>'.join(LOGS)}<br><br><a href='/panel?pwd={PASSWORD}' style='color:white'>Volver</a></body>"

@app.route('/send', methods=['POST'])
def send():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id'])); txt = request.form['msg']
    run_coro(ch.send(txt)); add_log(f"📢 -> #{ch.name}: {txt[:80]}")
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/mod', methods=['POST'])
def mod():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    guild_id = int(request.form['guild_id']); user_id = int(request.form['user_id']); act = request.form['action']
    g = bot.get_guild(guild_id)
    async def do():
        try:
            try: m = await g.fetch_member(user_id)
            except: m = g.get_member(user_id)
            if not m: add_log(f"❌ No encuentro {user_id}"); return
            if act == "ban": await g.ban(m)
            elif act == "kick": await g.kick(m)
            elif act == "mute": await m.timeout(discord.utils.utcnow()+timedelta(minutes=10))
            elif act == "unmute": await m.timeout(None)
            add_log(f"✅ {act} a {m}")
        except discord.Forbidden: add_log(f"❌ 403 FORBIDDEN - Sube el rol del bot arriba!")
        except Exception as e: add_log(f"❌ MOD: {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/giveaway', methods=['POST'])
def giveaway():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id'])); prize = request.form['prize']; mins = int(request.form['minutes'] or 1)
    async def do():
        embed = discord.Embed(title="🎉 SORTEO", description=f"Premio: **{prize}**\nReacciona 🎉", color=discord.Color.gold())
        msg = await ch.send(embed=embed); await msg.add_reaction("🎉"); await asyncio.sleep(mins*60)
        msg = await ch.fetch_message(msg.id)
        for r in msg.reactions:
            if str(r.emoji) == "🎉":
                users = [u async for u in r.users() if not u.bot]
                if users: await ch.send(f"Ganador {prize}: {random.choice(users).mention}"); return
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/poll', methods=['POST'])
def poll():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    async def do():
        q = request.form['q']; o1 = request.form['o1']; o2 = request.form['o2']
        embed = discord.Embed(title=f"📊 {q}", description=f"1️⃣ {o1}\n2️⃣ {o2}", color=discord.Color.blurple())
        msg = await ch.send(embed=embed); await msg.add_reaction("1️⃣"); await msg.add_reaction("2️⃣")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/ticketpanel', methods=['POST'])
def ticketpanel():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    async def do(): await ch.send(embed=discord.Embed(title="🎫 Soporte", description="Clica para abrir ticket", color=discord.Color.green()), view=TicketView())
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

# --- LOCKDOWN LOGICA ---
@app.route('/lockdown', methods=['POST'])
def lockdown():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    guild_id = int(request.form['guild_id']); reason = request.form.get('reason', 'Mantenimiento')
    g = bot.get_guild(guild_id)
    async def do():
        try:
            add_log(f"🚨 INICIANDO LOCKDOWN en {g.name} Motivo: {reason}")
            # 1. Crear o buscar canal de lockdown
            lock_channel = discord.utils.get(g.text_channels, name="servidor-cerrado-temporalmente")
            if not lock_channel:
                overwrites = {
                    g.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
                    g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                # Admins pueden ver
                for r in g.roles:
                    if r.permissions.administrator or "admin" in r.name.lower() or "mod" in r.name.lower() or "staff" in r.name.lower():
                        overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                lock_channel = await g.create_text_channel("Servidor-Cerrado-Temporalmente", overwrites=overwrites, topic="Canal de emergencia durante lockdown")

            # 2. Bloquear todos los demás canales
            for ch in g.channels:
                if ch.id == lock_channel.id: continue
                try:
                    await ch.set_permissions(g.default_role, view_channel=False, reason=f"Lockdown: {reason}")
                except Exception as e:
                    add_log(f"⚠️ No pude bloquear #{ch.name}: {e}")

            # 3. Mensaje en canal lockdown
            embed = discord.Embed(
                title="🔒 SERVIDOR CERRADO TEMPORALMENTE",
                description=f"**Motivo:** {reason}\n\nTodo el servidor está bloqueado por seguridad.\nSolo el Staff puede ver este canal.\n\nSe reabrirá en cuanto se solucione.",
                color=discord.Color.red(), timestamp=datetime.now()
            )
            embed.add_field(name="Estado", value="🔴 Cerrado", inline=True)
            embed.add_field(name="Acceso", value="Solo Admins+", inline=True)
            embed.set_footer(text=f"Lockdown activado por Panel | {g.name}")
            await lock_channel.send(embed=embed)
            add_log(f"✅ LOCKDOWN OK - Canal: {lock_channel.name}")
        except Exception as e:
            add_log(f"❌ LOCKDOWN ERROR: {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/unlockdown', methods=['POST'])
def unlockdown():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    guild_id = int(request.form['guild_id'])
    g = bot.get_guild(guild_id)
    async def do():
        try:
            add_log(f"🔓 DESBLOQUEANDO {g.name}")
            for ch in g.channels:
                try:
                    await ch.set_permissions(g.default_role, overwrite=None, reason="Fin Lockdown")
                except: pass

            lock_channel = discord.utils.get(g.text_channels, name="servidor-cerrado-temporalmente")
            if lock_channel:
                embed = discord.Embed(title="🔓 SERVIDOR REABIERTO", description="Todo vuelve a la normalidad. Gracias por la paciencia!", color=discord.Color.green())
                await lock_channel.send(embed=embed)
                await asyncio.sleep(5)
                await lock_channel.delete(reason="Fin lockdown")
            add_log(f"✅ UNLOCK OK")
        except Exception as e: add_log(f"❌ UNLOCK ERROR: {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/setlogchannel', methods=['POST'])
def setlogchannel():
    global LOG_CHANNEL_ID
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    LOG_CHANNEL_ID = int(request.form['channel_id']); add_log(f"📜 Logs: {LOG_CHANNEL_ID}")
    return redirect(f"/panel?pwd={PASSWORD}")

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_final")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True), interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        for r in interaction.guild.roles:
            if r.permissions.administrator or any(x in r.name.lower() for x in ["staff","admin","mod"]): overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(f"{interaction.user.mention}", embed=discord.Embed(title=f"Ticket {interaction.user}", description="Staff te atenderá", color=discord.Color.orange()), view=CloseView())
        await interaction.response.send_message(f"Ticket {ch.mention}", ephemeral=True)

class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Cerrar", style=discord.ButtonStyle.red, custom_id="close_ticket_final")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cerrando 3s..."); await asyncio.sleep(3); await interaction.channel.delete()

@bot.event
async def on_ready():
    global BOT_LOOP
    BOT_LOOP = asyncio.get_running_loop()
    bot.add_view(TicketView()); bot.add_view(CloseView())
    activity = discord.Streaming(name="Sigueme en YouTube, Twitch, X e Insta!", url=TWITCH_LINK)
    await bot.change_presence(activity=activity)
    add_log(f"✅ ONLINE {bot.user} | Streaming {TWITCH_LINK}")

@bot.event
async def on_message_delete(m):
    if m.author.bot: return
    await send_log(m.guild, f"🗑️ Borrado {m.author} en #{m.channel.name}: {m.content[:100]}")
@bot.event
async def on_message_edit(b,a):
    if b.author.bot or b.content==a.content: return
    await send_log(b.guild, f"✏️ Edit {b.author}: {b.content[:60]} -> {a.content[:60]}")
@bot.event
async def on_member_join(m): await send_log(m.guild, f"📥 Entró {m}")
@bot.event
async def on_member_remove(m): await send_log(m.guild, f"📤 Salió {m}")

@bot.event
async def on_message(m):
    if m.author.bot: await bot.process_commands(m); return
    add_log(f"👀 {m.author}: {m.content[:50]}")
    for bad in BAD_WORDS:
        if bad in m.content.lower():
            try: await m.delete(); await m.channel.send(f"{m.author.mention} lenguaje no", delete_after=3); return
            except: pass
    await bot.process_commands(m)

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 {round(bot.latency*1000)}ms")
@bot.command()
async def test(ctx): await ctx.send(f"✅ OK")
@bot.command()
async def redes(ctx):
    embed = discord.Embed(title="🔗 Redes Dalaluki", description="Sígueme!", color=0xFF0000)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="YouTube", url=YT_LINK, emoji="🔴"))
    view.add_item(discord.ui.Button(label="Twitch", url=TWITCH_LINK, emoji="💜"))
    view.add_item(discord.ui.Button(label="X", url=X_LINK, emoji="🐦"))
    view.add_item(discord.ui.Button(label="Instagram", url=INSTA_LINK, emoji="📸"))
    await ctx.send(embed=embed, view=view)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
