import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from collections import defaultdict
import time

load_dotenv()
TOKEN = os.getenv("TOKEN")

# --- CONFIGURACION ---
ANTI_RAID_TIEMPO = 10  # segundos
ANTI_RAID_CANTIDAD = 5 # si entran 5 en 10s = raid
LOG_CHANNEL_NAME = "logs-seguridad" # crea un canal con ese nombre

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Memoria temporal
join_cache = []
spam_cache = defaultdict(list)
user_warns = {}

@bot.event
async def on_ready():
    print(f"✅ {bot.user} LISTO - PROTECCION ACTIVADA")
    for guild in bot.guilds:
        # Crear canal de logs si no existe
        if not discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME):
            try:
                await guild.create_text_channel(LOG_CHANNEL_NAME)
                print(f"Canal #{LOG_CHANNEL_NAME} creado en {guild.name}")
            except:
                pass

async def log(guild, mensaje):
    canal = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if canal:
        embed = discord.Embed(description=mensaje, color=discord.Color.red())
        await canal.send(embed=embed)

# --- ANTI-RAID ---
@bot.event
async def on_member_join(member):
    global join_cache
    now = time.time()
    join_cache.append(now)
    # Limpiar viejos
    join_cache = [t for t in join_cache if now - t < ANTI_RAID_TIEMPO]
    
    if len(join_cache) >= ANTI_RAID_CANTIDAD:
        await log(member.guild, f"🚨 **POSIBLE RAID DETECTADO!** {len(join_cache)} usuarios en {ANTI_RAID_TIEMPO}s. Activando bloqueo.")
        # Bloquear invitaciones
        try:
            # Banear a los ultimos que entraron (opcional, aqui solo los kickea)
            async for m in member.guild.fetch_members(limit=ANTI_RAID_CANTIDAD):
                if (now - m.joined_at.timestamp()) < ANTI_RAID_TIEMPO + 2:
                    try:
                        await m.kick(reason="Anti-Raid: Entrada masiva")
                    except:
                        pass
            await log(member.guild, f"✅ Raid mitigado, usuarios recientes expulsados.")
        except Exception as e:
            print(e)
        join_cache.clear()

# --- ANTI-NUKE (canales y roles) ---
@bot.event
async def on_guild_channel_delete(channel):
    await log(channel.guild, f"⚠️ Canal borrado: `{channel.name}` por posible nuke. Revisa la auditoría!")
    # Aqui podrias banear automaticamente al que lo borró mirando el audit log
    try:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                await entry.user.ban(reason="Anti-Nuke: Borrado de canal")
                await log(channel.guild, f"🔨 Baneado {entry.user} por borrar canal.")
    except:
        pass

@bot.event
async def on_guild_role_delete(role):
    await log(role.guild, f"⚠️ Rol borrado: `{role.name}`")
    try:
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            await entry.user.ban(reason="Anti-Nuke: Borrado de rol")
            await log(role.guild, f"🔨 Baneado {entry.user} por borrar rol.")
    except:
        pass

# --- ANTI-SPAM Y ANTI-LINKS ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Anti-links (discord.gg, http)
    if "discord.gg/" in message.content or "https://" in message.content or "http://" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(f"{message.author.mention} ❌ Links no permitidos!", delete_after=5)
            await log(message.guild, f"🔗 Link bloqueado de {message.author}: {message.content[:100]}")
            return

    # Anti-spam 5 mensajes en 5 seg
    now = time.time()
    spam_cache[message.author.id].append(now)
    spam_cache[message.author.id] = [t for t in spam_cache[message.author.id] if now - t < 5]
    
    if len(spam_cache[message.author.id]) >= 5:
        await message.channel.send(f"{message.author.mention} 🤫 Para de spamear!", delete_after=5)
        try:
            await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=5), reason="Anti-Spam")
            await log(message.guild, f"⏱️ {message.author} muteado 5m por spam")
        except:
            pass
        spam_cache[message.author.id].clear()
        return

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def lockdown(ctx):
    """Bloquea el servidor (quita permiso de enviar mensajes a @everyone)"""
    await ctx.guild.default_role.edit(send_messages=False)
    await ctx.send("🔒 Servidor en cuarentena! Nadie puede hablar.")
    await log(ctx.guild, f"🔒 Lockdown activado por {ctx.author}")

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    await ctx.guild.default_role.edit(send_messages=True)
    await ctx.send("🔓 Servidor desbloqueado.")
    await log(ctx.guild, f"🔓 Unlock por {ctx.author}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Latencia: {round(bot.latency*1000)}ms | Protegiendo {ctx.guild.name}")

bot.run(TOKEN)