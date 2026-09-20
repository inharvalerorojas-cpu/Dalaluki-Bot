import discord
from discord.ext import commands
import os, threading, asyncio, random, re
from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "dalaluki_1234"

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
    else:
        add_log("❌ BOT_LOOP no listo")

HTML = """
<style>
body{background:#0f0f0f;color:white;font-family:Arial;padding:15px;max-width:950px;margin:auto}
.card{background:#1e1e1e;padding:16px;border-radius:12px;margin-bottom:15px;border:1px solid #2a2a2a}
input,select,textarea{width:100%;padding:12px;margin:6px 0;background:#2a2a2a;color:white;border:none;border-radius:8px;box-sizing:border-box}
button{background:#5865F2;color:white;padding:12px;width:100%;border:none;border-radius:8px;cursor:pointer;font-weight:bold;margin-top:6px}
button.red{background:#ef4444}button.yellow{background:#eab308;color:black}button.green{background:#22c55e}button.orange{background:#f97316}
h3{margin:0 0 10px 0;color:#a78bfa}.logs{height:220px;overflow-y:auto;background:#000;padding:10px;border-radius:8px;font-family:monospace;font-size:11px;line-height:1.4}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style>

<h1>🤖 Dalaluki-Bot-3 FINAL FIX</h1>
<div class="card">
<h3>Estado: {{'🟢 ONLINE' if bot.is_ready() else '🔴 OFFLINE'}} | {{total}} miembros | Loop: {{'OK' if loop_ok else 'FAIL'}} | <a href='/logs?pwd={{pwd}}' style='color:#22c55e'>Ver Logs Completos</a></h3>
<div class="logs">{{logs_html|safe}}</div>
</div>

<div class="grid">
<div class="card"><h3>📢 Enviar Mensaje</h3>
<form action="/send?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">{{g.name}} - #{{c.name}}</option>{% endfor %}{% endfor %}</select>
<textarea name="msg" placeholder="Escribe mensaje..."></textarea><button>Enviar al Discord</button></form></div>

<div class="card"><h3>🔨 Moderación</h3>
<form action="/mod?pwd={{pwd}}" method="post">
<select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select>
<input name="user_id" placeholder="ID del usuario">
<select name="action"><option value="ban">BAN</option><option value="kick">KICK</option><option value="mute">MUTE 10m</option><option value="unmute">UNMUTE</option></select>
<button class="red">Ejecutar</button></form></div>
</div>

<div class="grid">
<div class="card"><h3>🎁 Sorteo (usa 1 min para test)</h3>
<form action="/giveaway?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<input name="prize" placeholder="Premio: Nitro">
<input name="minutes" type="number" value="1" min="1" max="60"><button class="yellow">Iniciar Sorteo</button></form></div>

<div class="card"><h3>📊 Encuesta</h3>
<form action="/poll?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select>
<input name="q" placeholder="Pregunta"><input name="o1" placeholder="Opción 1"><input name="o2" placeholder="Opción 2">
<button class="green">Crear Encuesta</button></form></div>
</div>

<div class="grid">
<div class="card"><h3>🎫 Tickets</h3>
<form action="/ticketpanel?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}} - DONDE CREAR PANEL</option>{% endfor %}{% endfor %}</select>
<button class="orange">Crear Panel de Tickets</button></form></div>

<div class="card"><h3>📜 Canal de Logs</h3>
<form action="/setlogchannel?pwd={{pwd}}" method="post">
<select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}} - DONDE MANDAR LOGS</option>{% endfor %}{% endfor %}</select>
<button>Setear Canal Logs</button></form></div>
</div>
"""

@app.route('/')
def home(): return f"BOT {'ONLINE' if bot.is_ready() else 'OFFLINE'} - <a href='/panel?pwd={PASSWORD}'>Ir al Panel</a>"

@app.route('/panel')
def panel():
    if request.args.get('pwd')!= PASSWORD: return "Contraseña mal", 401
    total = bot.guilds[0].member_count if bot.guilds else 0
    logs_html = "<br>".join(LOGS[:30]) if LOGS else "Sin logs aún. Escribe!ping en Discord"
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, total=total, logs_html=logs_html, loop_ok=BOT_LOOP is not None)

@app.route('/logs')
def logs_page():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    html = "<br>".join(LOGS) if LOGS else "Vacio"
    return f"<body style='background:#000;color:#0f0;font-family:monospace;padding:20px;white-space:pre-wrap'><h2>📜 {len(LOGS)} Logs</h2>{html}<br><br><a href='/panel?pwd={PASSWORD}' style='color:white'>Volver</a></body>"

@app.route('/send', methods=['POST'])
def send():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    try:
        ch = bot.get_channel(int(request.form['channel_id']))
        txt = request.form['msg']
        run_coro(ch.send(txt))
        add_log(f"📢 Panel -> #{ch.name}: {txt[:80]}")
    except Exception as e: add_log(f"❌ Error send: {e}")
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/mod', methods=['POST'])
def mod():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    g = bot.get_guild(int(request.form['guild_id']))
    uid = int(request.form['user_id'])
    act = request.form['action']
    async def do():
        try:
            m = await g.fetch_member(uid)
            if act == "ban": await g.ban(m); await send_log(g, f"🔨 BAN a {m} ({m.id}) desde panel")
            elif act == "kick": await g.kick(m); await send_log(g, f"👢 KICK a {m} desde panel")
            elif act == "mute": await m.timeout(timedelta(minutes=10)); await send_log(g, f"🔇 MUTE 10m a {m}")
            elif act == "unmute": await m.timeout(None); await send_log(g, f"🔊 UNMUTE a {m}")
        except Exception as e: add_log(f"❌ MOD ERROR: {e}")
    run_coro(do())
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/giveaway', methods=['POST'])
def giveaway():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id'])); prize = request.form['prize']; mins = int(request.form['minutes'] or 1)
    async def do():
        try:
            embed = discord.Embed(title="🎉 SORTEO", description=f"Premio: **{prize}**\nReacciona 🎉\nTermina en {mins} min", color=discord.Color.gold())
            msg = await ch.send(embed=embed); await msg.add_reaction("🎉")
            add_log(f"🎁 Sorteo '{prize}' iniciado en #{ch.name} ({mins}m)")
            await asyncio.sleep(mins*60)
            msg = await ch.fetch_message(msg.id)
            for r in msg.reactions:
                if str(r.emoji) == "🎉":
                    users = [u async for u in r.users() if not u.bot]
                    if users:
                        w = random.choice(users)
                        await ch.send(f"🎉 Ganador de **{prize}**: {w.mention}!")
                        await send_log(ch.guild, f"🏆 Sorteo '{prize}' ganado por {w}")
                        return
            await ch.send(f"Sorteo {prize} sin participantes")
        except Exception as e: add_log(f"❌ SORTEO ERROR: {e}")
    run_coro(do())
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/poll', methods=['POST'])
def poll():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    async def do():
        q = request.form['q']; o1 = request.form['o1']; o2 = request.form['o2']
        embed = discord.Embed(title=f"📊 {q}", description=f"1️⃣ {o1}\n2️⃣ {o2}", color=discord.Color.blurple())
        msg = await ch.send(embed=embed); await msg.add_reaction("1️⃣"); await msg.add_reaction("2️⃣")
        add_log(f"📊 Encuesta '{q}' en #{ch.name}")
    run_coro(do())
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/ticketpanel', methods=['POST'])
def ticketpanel():
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    ch = bot.get_channel(int(request.form['channel_id']))
    async def do():
        embed = discord.Embed(title="🎫 Soporte", description="Clica el botón para abrir ticket privado", color=discord.Color.green())
        await ch.send(embed=embed, view=TicketView())
        add_log(f"🎫 Panel tickets creado en #{ch.name}")
    run_coro(do())
    return redirect(f"/panel?pwd={PASSWORD}")

@app.route('/setlogchannel', methods=['POST'])
def setlogchannel():
    global LOG_CHANNEL_ID
    if request.args.get('pwd')!= PASSWORD: return "No", 401
    LOG_CHANNEL_ID = int(request.form['channel_id'])
    add_log(f"📜 Canal logs seteado: {LOG_CHANNEL_ID}")
    return redirect(f"/panel?pwd={PASSWORD}")

# --- VIEWS TICKETS ---
class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_final")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        for r in interaction.guild.roles:
            if any(x in r.name.lower() for x in ["staff","admin","mod"]):
                overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(f"{interaction.user.mention}", embed=discord.Embed(title=f"Ticket de {interaction.user}", description="Staff te atenderá pronto", color=discord.Color.orange()), view=CloseView())
        await interaction.response.send_message(f"Ticket creado {ch.mention}", ephemeral=True)
        await send_log(interaction.guild, f"🎫 Ticket abierto por {interaction.user} -> {ch.name}")

class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Cerrar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_final")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_log(interaction.guild, f"🔒 Ticket {interaction.channel.name} cerrado por {interaction.user}")
        await interaction.response.send_message("Cerrando en 3s...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

# --- EVENTOS ---
@bot.event
async def on_ready():
    global BOT_LOOP
    BOT_LOOP = asyncio.get_running_loop()
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    add_log(f"✅ BOT ONLINE como {bot.user} | Loop OK")
    print(f"✅ ONLINE {bot.user}")

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    await send_log(message.guild, f"🗑️ Mensaje borrado de {message.author} en #{message.channel.name}: `{message.content[:300]}`")

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    await send_log(before.guild, f"✏️ Editado {before.author} en #{before.channel.name}:\nAntes: {before.content[:150]}\nDespués: {after.content[:150]}")

@bot.event
async def on_member_join(member):
    await send_log(member.guild, f"📥 Entró {member} ({member.id})")

@bot.event
async def on_member_remove(member):
    await send_log(member.guild, f"📤 Salió {member} ({member.id})")

@bot.event
async def on_message(m):
    global MSG_COUNT
    if m.author.bot:
        await bot.process_commands(m)
        return
    MSG_COUNT += 1
    add_log(f"👀 Visto: {m.author}: {m.content[:60]} en #{m.channel.name}")

    # Auto-mod
    low = m.content.lower()
    for bad in BAD_WORDS:
        if bad in low:
            try:
                await m.delete()
                await send_log(m.guild, f"🤬 Auto-mod borró a {m.author} en #{m.channel.name} por `{bad}`: {m.content[:200]}")
                await m.channel.send(f"{m.author.mention} lenguaje no permitido", delete_after=4)
                return
            except: pass

    #!ping directo por si falla el command
    if m.content.lower().strip() == "!ping":
        await m.channel.send(f"🏓 Pong! {round(bot.latency*1000)}ms | ONLINE")
        add_log("✅!ping directo respondido")

    await bot.process_commands(m)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency*1000)}ms")
    add_log(f"🏓!ping por comando de {ctx.author}")

@bot.command()
async def test(ctx):
    await ctx.send(f"✅ Test OK | Guilds: {len(bot.guilds)} | Loop: {'OK' if BOT_LOOP else 'FAIL'}")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    if not TOKEN:
        print("❌ NO HAY TOKEN EN ENV - Pon TOKEN en Render > Environment")
    else:
        bot.run(TOKEN)
