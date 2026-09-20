import discord
from discord.ext import commands
import os, threading, asyncio, random
from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta

app = Flask('')
TOKEN = os.getenv("TOKEN")
PASSWORD = "dalaluki_1234"

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MSG_COUNT = 0
LOGS = []
BAD_WORDS = ["puta","puto","maricon","gilipollas","cabron","mierda","imbecil"]
LOG_CHANNEL_ID = None
BOT_LOOP = None # FIX IMPORTANTE

def add_log(t):
    LOGS.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {t}")
    print(t)

async def send_log(guild, text):
    add_log(text)
    if LOG_CHANNEL_ID:
        ch=bot.get_channel(LOG_CHANNEL_ID)
        if ch:
            try: await ch.send(embed=discord.Embed(description=text, color=0x2b2d31, timestamp=datetime.now()))
            except: pass

def run_coro(coro):
    if BOT_LOOP and BOT_LOOP.is_running():
        asyncio.run_coroutine_threadsafe(coro, BOT_LOOP)
    else:
        add_log(f"❌ BOT_LOOP no listo, no se pudo ejecutar")

HTML = """ PON AQUÍ EL HTML QUE YA TENIAS, NO LO CAMBIO PARA NO HACERLO LARGO, USA EL ANTERIOR """

# --- COPIA TODO EL HTML DEL MENSAJE ANTERIOR AQUI ---
# Para que no falle te lo pongo corto, usa el anterior completo
HTML = """
<style>body{background:#111;color:white;font-family:Arial;padding:15px;max-width:900px;margin:auto}.card{background:#222;padding:16px;border-radius:12px;margin-bottom:15px;border:1px solid #333}input,select,textarea{width:100%;padding:12px;margin:6px 0;background:#333;color:white;border:none;border-radius:8px}button{background:#5865F2;color:white;padding:12px;width:100%;border:none;border-radius:8px;font-weight:bold}button.red{background:#ef4444}button.yellow{background:#eab308;color:black}button.green{background:#22c55e}button.orange{background:#f97316}h3{color:#a78bfa}.logs{height:200px;overflow-y:scroll;background:#000;padding:10px;font-family:monospace;font-size:12px;border-radius:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}</style>
<h1>🤖 Dalaluki-Bot-3 FIX</h1>
<div class="card"><h3>Estado: {{'🟢 ONLINE' if bot.is_ready() else '🔴 OFFLINE'}} | {{total}} miembros</h3><div class="logs">{{logs_html|safe}}</div><a href='/logs?pwd={{pwd}}' style='color:#22c55e'>Logs completos</a></div>
<div class="grid">
<div class="card"><h3>📢 Mensaje</h3><form action="/send?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><textarea name="msg"></textarea><button>Enviar</button></form></div>
<div class="card"><h3>🔨 Mod</h3><form action="/mod?pwd={{pwd}}" method="post"><select name="guild_id">{% for g in bot.guilds %}<option value="{{g.id}}">{{g.name}}</option>{% endfor %}</select><input name="user_id" placeholder="ID"><select name="action"><option value="ban">BAN</option><option value="kick">KICK</option><option value="mute">MUTE</option><option value="unmute">UNMUTE</option></select><button class="red">Ejecutar</button></form></div>
</div>
<div class="grid">
<div class="card"><h3>🎁 Sorteo</h3><form action="/giveaway?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><input name="prize" placeholder="Premio"><input name="minutes" type="number" value="1"><button class="yellow">Iniciar 1min test</button></form></div>
<div class="card"><h3>📊 Encuesta</h3><form action="/poll?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><input name="q" placeholder="Pregunta"><input name="o1" placeholder="O1"><input name="o2" placeholder="O2"><button class="green">Crear</button></form></div>
</div>
<div class="grid">
<div class="card"><h3>🎫 Tickets</h3><form action="/ticketpanel?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><button class="orange">Crear Panel</button></form></div>
<div class="card"><h3>📜 Logs</h3><form action="/setlogchannel?pwd={{pwd}}" method="post"><select name="channel_id">{% for g in bot.guilds %}{% for c in g.text_channels %}<option value="{{c.id}}">#{{c.name}}</option>{% endfor %}{% endfor %}</select><button>Setear</button></form></div>
</div>
"""

@app.route('/')
def home(): return f"BOT {'ONLINE' if bot.is_ready() else 'OFFLINE'} - <a href='/panel?pwd={PASSWORD}'>Panel</a>"
@app.route('/panel')
def panel():
    if request.args.get('pwd')!=PASSWORD: return "mal",401
    total=bot.guilds[0].member_count if bot.guilds else 0
    logs_html="<br>".join(LOGS[:25]) if LOGS else "Sin logs - bot no arrancó"
    return render_template_string(HTML, bot=bot, pwd=PASSWORD, total=total, logs_html=logs_html)
@app.route('/logs')
def logs_page():
    if request.args.get('pwd')!=PASSWORD: return "No",401
    return f"<body style='background:#000;color:#0f0;font-family:monospace;padding:20px'>{'<br>'.join(LOGS)}<br><br><a href='/panel?pwd={PASSWORD}' style='color:white'>Volver</a></body>"
@app.route('/send', methods=['POST'])
def send():
    if request.args.get('pwd')!=PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id']))
    if not ch: return "Canal no encontrado",404
    run_coro(ch.send(request.form['msg'])); add_log(f"📢 Enviado a #{ch.name}"); return redirect(f"/panel?pwd={PASSWORD}")
@app.route('/mod', methods=['POST'])
def mod():
    if request.args.get('pwd')!=PASSWORD: return "No",401
    g=bot.get_guild(int(request.form['guild_id'])); uid=int(request.form['user_id']); act=request.form['action']
    async def do():
        try:
            m=await g.fetch_member(uid)
            if act=="ban": await g.ban(m)
            elif act=="kick": await g.kick(m)
            elif act=="mute": await m.timeout(timedelta(minutes=10))
            elif act=="unmute": await m.timeout(None)
            await send_log(g, f"🔨 {act} a {m}")
        except Exception as e: add_log(f"❌ MOD ERROR: {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")
@app.route('/giveaway', methods=['POST'])
def giveaway():
    if request.args.get('pwd')!=PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id'])); prize=request.form['prize']; mins=int(request.form['minutes'] or 1)
    async def do():
        try:
            embed=discord.Embed(title="🎉 SORTEO", description=f"Premio **{prize}**\nReacciona 🎉 - {mins} min", color=discord.Color.gold())
            msg=await ch.send(embed=embed); await msg.add_reaction("🎉"); add_log(f"🎁 Sorteo {prize} iniciado")
            await asyncio.sleep(mins*60)
            msg=await ch.fetch_message(msg.id)
            for r in msg.reactions:
                if str(r.emoji)=="🎉":
                    users=[u async for u in r.users() if not u.bot]
                    if users: await ch.send(f"Ganador {prize}: {random.choice(users).mention}"); return
            await ch.send("Sin participantes")
        except Exception as e: add_log(f"❌ SORTEO ERROR {e}")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")
@app.route('/poll', methods=['POST'])
def poll():
    if request.args.get('pwd')!=PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id']))
    async def do():
        embed=discord.Embed(title=request.form['q'], description=f"1️⃣ {request.form['o1']}\n2️⃣ {request.form['o2']}", color=discord.Color.blurple())
        msg=await ch.send(embed=embed); await msg.add_reaction("1️⃣"); await msg.add_reaction("2️⃣")
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")
@app.route('/ticketpanel', methods=['POST'])
def ticketpanel():
    if request.args.get('pwd')!=PASSWORD: return "No",401
    ch=bot.get_channel(int(request.form['channel_id']))
    async def do():
        await ch.send(embed=discord.Embed(title="🎫 Soporte", description="Clica para abrir ticket", color=discord.Color.green()), view=TicketView())
    run_coro(do()); return redirect(f"/panel?pwd={PASSWORD}")
@app.route('/setlogchannel', methods=['POST'])
def setlogchannel():
    global LOG_CHANNEL_ID
    if request.args.get('pwd')!=PASSWORD: return "No",401
    LOG_CHANNEL_ID=int(request.form['channel_id']); add_log(f"Logs seteados {LOG_CHANNEL_ID}"); return redirect(f"/panel?pwd={PASSWORD}")

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_fix")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True), interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        ch=await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await ch.send(f"{interaction.user.mention}", embed=discord.Embed(title="Ticket", color=0x00ff00), view=CloseView())
        await interaction.response.send_message(f"{ch.mention}", ephemeral=True)
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Cerrar", style=discord.ButtonStyle.red, custom_id="close_ticket_fix")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

@bot.event
async def on_ready():
    global BOT_LOOP
    BOT_LOOP = asyncio.get_running_loop()
    bot.add_view(TicketView()); bot.add_view(CloseView())
    add_log(f"✅ BOT ONLINE {bot.user} - LOOP OK")
    print(f"✅ ONLINE {bot.user}")

@bot.event
async def on_message(m):
    global MSG_COUNT
    if not m.author.bot: MSG_COUNT+=1
    await bot.process_commands(m)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    if not TOKEN:
        print("❌ NO HAY TOKEN EN ENV!")
    else:
        bot.run(TOKEN)
