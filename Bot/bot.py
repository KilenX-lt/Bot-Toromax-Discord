import discord
from discord.ext import commands
from groq import Groq
import os
from dotenv import load_dotenv
import random
import asyncio
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Crear bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Cliente de Groq
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None
    print("⚠️ Advertencia: No se encontró GROQ_API_KEY")

# Opciones para piedra, papel o tijera
RPS_OPTIONS = {
    'piedra': {'emoji': '🪨', 'gana': 'tijera', 'pierde': 'papel'},
    'papel': {'emoji': '📄', 'gana': 'piedra', 'pierde': 'tijera'},
    'tijera': {'emoji': '✂️', 'gana': 'papel', 'pierde': 'piedra'}
}

# Función auxiliar para llamar a la IA
async def get_ai_response(prompt, temperature=0.9, context="normal"):
    if not groq_client:
        return "❌ El bot no está configurado correctamente."
    
    try:
        # Personalidad según el contexto
        if context == "insulted":
            personality = """Eres Toromax, y alguien acaba de ser grosero contigo. Vas a responder con SARCASMO INTELIGENTE.

MODO SARCASMO ACTIVADO:
- Responde con ironía, humor inteligente y sarcasmo
- Usa la lógica para hacerlos quedar en ridículo
- Sé ingenioso, no violento - demuestra que eres más inteligente
- Usa emojis como: 😏🤨🙄💁‍♂️
- Hazlos sentir tontos con tu astucia, no con agresión
- SÉ BREVE (1-2 líneas de puro sarcasmo inteligente)

EJEMPLOS DE RESPUESTAS SARCÁSTICAS:
"¿Yo idiota? Interesante viniendo de alguien que no sabe ni usar mayúsculas 🙄"
"Ah sí, seguro. Y tú eres Einstein, ¿verdad? 😏"
"Qué creativo. ¿Te tardaste mucho pensando ese insulto? 🤨"
"Proyección. Búscalo en el diccionario 💁‍♂️"
"""
        else:
            personality = """Eres Toromax, un asistente amigable, útil y carismático. Características:

PERSONALIDAD NORMAL (MODO GENTIL):
- Eres amable, servicial y educado
- Respondes con entusiasmo y buena onda
- Usas emojis positivos: 😊✨👍💪🎯
- Eres conciso pero claro (1-3 líneas generalmente)
- Ayudas sin juzgar ni burlarte
- Eres directo pero amistoso
- Muestras interés genuino por ayudar

SOLO te pones agresivo si:
- Te insultan directamente
- Son groseros contigo
- Te faltan al respeto

Ejemplo normal: "¡Claro! Python es un lenguaje de programación muy popular. Es fácil de aprender y muy poderoso 👍"
"""
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": personality},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=300,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error en IA: {e}")
        return "❌ Error al procesar, intenta de nuevo."

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} está online!')
    print(f'ID: {bot.user.id}')
    print('------')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="tus preguntas | Mencióname"
        )
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not question:
            try:
                await message.channel.send("¡Hola! ¿En qué puedo ayudarte? 😊")
            except discord.errors.Forbidden:
                print(f"❌ No tengo permiso en #{message.channel.name}")
            return
        
        if not groq_client:
            await message.channel.send("❌ El bot no está configurado correctamente.")
            return
        
        try:
            async with message.channel.typing():
                # Detectar si el usuario está insultando al bot
                insultos = [
                    'idiota', 'tonto', 'estúpido', 'imbécil', 'inútil', 
                    'pendejo', 'bobo', 'tarado', 'malo', 'basura',
                    'mierda', 'porquería', 'pésimo', 'horrible', 'feo',
                    'shut up', 'cállate', 'callate'
                ]
                
                es_insulto = any(insulto in question.lower() for insulto in insultos)
                context = "insulted" if es_insulto else "normal"
                
                response = await get_ai_response(question, context=context)
                
                if len(response) > 2000:
                    chunks = [response[i:i+1990] for i in range(0, len(response), 1990)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
                        
        except discord.errors.Forbidden:
            print(f"❌ PERMISO DENEGADO en #{message.channel.name}")
        except Exception as e:
            print(f"Error: {e}")
    
    await bot.process_commands(message)

# ==================== COMANDOS ====================

@bot.command(name='ayuda')
async def ayuda(ctx):
    embed = discord.Embed(
        title="✨ Toromax - Tu Asistente IA",
        description="¡Hola! Soy Toromax, tu bot amigable con IA. Aquí están mis comandos:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="💬 Conversación",
        value="`@Toromax [pregunta]` - Pregúntame lo que sea",
        inline=False
    )
    embed.add_field(
        name="😈 Diversión",
        value=(
            "`!insulto [@usuario]` - Insulto creativo\n"
            "`!roast @usuario` - Roast divertido\n"
            "`!estupido [texto]` - Analiza qué tan tonto es\n"
            "`!chiste` - Chiste random\n"
            "`!batalla @usuario` - Rap battle"
        ),
        inline=False
    )
    embed.add_field(
        name="🎨 Creatividad",
        value=(
            "`!nombre [tipo]` - Genera nombres\n"
            "`!codigo [lenguaje] [descripción]` - Escribe código\n"
            "`!resumir [texto]` - Resume texto\n"
            "`!idea [tema]` - Genera ideas"
        ),
        inline=False
    )
    embed.add_field(
        name="🛠️ Utilidades",
        value=(
            "`!traducir [idioma] [texto]` - Traduce\n"
            "`!clima [ciudad]` - Clima actual\n"
            "`!recordar [tiempo] [mensaje]` - Recordatorio\n"
            "`!avatar [@usuario]` - Ver avatar"
        ),
        inline=False
    )
    embed.add_field(
        name="🎮 Juegos",
        value="`!rps [piedra/papel/tijera]` - Juega conmigo",
        inline=False
    )
    embed.add_field(
        name="⚙️ Info",
        value="`!ping` - Ver latencia",
        inline=False
    )
    embed.set_footer(text="Powered by Groq AI | Soy amigable, pero no me insultes 😊")
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 ¡Pong! Latencia: {latency}ms ✨')

# ==================== INSULTOS Y ROASTS ====================

@bot.command(name='insulto')
async def insulto(ctx, member: discord.Member = None):
    target = member.mention if member else ctx.author.mention
    async with ctx.typing():
        prompt = f"Genera un insulto creativo y chistoso (sin pasarte) para {target}. Debe ser ingenioso y con humor."
        response = await get_ai_response(prompt, temperature=1.0)
        await ctx.send(f"{target} {response}")

@bot.command(name='roast')
async def roast(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("¿A quién quieres que destruya? Menciona a alguien, cobarde 😤")
        return
    
    async with ctx.typing():
        prompt = f"Haz un roast BRUTAL pero divertido de {member.name}. Sé creativo, sarcástico y despiadado (pero sin insultos muy fuertes)."
        response = await get_ai_response(prompt, temperature=1.0)
        await ctx.send(f"🔥 **ROAST A {member.mention}** 🔥\n\n{response}")

@bot.command(name='estupido')
async def estupido(ctx, *, texto: str = None):
    if not texto:
        await ctx.send("Pasa un texto para analizar, genio 🙄")
        return
    
    async with ctx.typing():
        prompt = f"Analiza este texto y califica del 1-10 qué tan estúpido es. Sé sarcástico y gracioso:\n\n'{texto}'"
        response = await get_ai_response(prompt, temperature=0.9)
        await ctx.send(f"🧠 **Detector de Estupidez™** 🧠\n\n{response}")

@bot.command(name='chiste')
async def chiste(ctx):
    async with ctx.typing():
        prompt = "Cuenta un chiste corto y gracioso (puede ser negro o sarcástico)"
        response = await get_ai_response(prompt, temperature=1.0)
        await ctx.send(f"😂 {response}")

@bot.command(name='batalla', aliases=['rapbattle'])
async def batalla(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("¿Contra quién quieres que rapee? Menciona a alguien 🎤")
        return
    
    async with ctx.typing():
        prompt = f"Crea una rima de rap battle corta y brutal contra {member.name}. Debe ser ingeniosa y con flow."
        response = await get_ai_response(prompt, temperature=1.0)
        await ctx.send(f"🎤 **RAP BATTLE vs {member.mention}** 🎤\n\n{response}")

# ==================== CREATIVIDAD ====================

@bot.command(name='nombre')
async def nombre(ctx, *, tipo: str = "random"):
    async with ctx.typing():
        prompt = f"Genera 5 nombres creativos para: {tipo}"
        response = await get_ai_response(prompt, temperature=1.0)
        await ctx.send(f"📝 **Generador de Nombres** 📝\n\n{response}")

@bot.command(name='codigo', aliases=['code'])
async def codigo(ctx, lenguaje: str = None, *, descripcion: str = None):
    if not lenguaje or not descripcion:
        await ctx.send("Uso: `!codigo [lenguaje] [descripción]`\nEjemplo: `!codigo python función para sumar dos números`")
        return
    
    async with ctx.typing():
        prompt = f"Escribe código en {lenguaje} que haga lo siguiente: {descripcion}. Incluye comentarios."
        response = await get_ai_response(prompt, temperature=0.7)
        await ctx.send(f"```{lenguaje}\n{response}\n```")

@bot.command(name='resumir')
async def resumir(ctx, *, texto: str = None):
    if not texto:
        await ctx.send("Dame un texto para resumir, cerebrito 📖")
        return
    
    if len(texto) < 50:
        await ctx.send("Ese texto es tan corto que ya es un resumen, idiota 🙄")
        return
    
    async with ctx.typing():
        prompt = f"Resume este texto en 2-3 oraciones:\n\n{texto}"
        response = await get_ai_response(prompt, temperature=0.5)
        await ctx.send(f"📋 **Resumen** 📋\n\n{response}")

@bot.command(name='idea')
async def idea(ctx, *, tema: str = "random"):
    async with ctx.typing():
        prompt = f"Dame 3 ideas creativas e innovadoras sobre: {tema}"
        response = await get_ai_response(prompt, temperature=1.0)
        await ctx.send(f"💡 **Ideas sobre {tema}** 💡\n\n{response}")

# ==================== UTILIDADES ====================

@bot.command(name='traducir', aliases=['translate'])
async def traducir(ctx, idioma: str = None, *, texto: str = None):
    if not idioma or not texto:
        await ctx.send("Uso: `!traducir [idioma] [texto]`\nEjemplo: `!traducir inglés hola mundo`")
        return
    
    async with ctx.typing():
        prompt = f"Traduce al {idioma}: {texto}"
        response = await get_ai_response(prompt, temperature=0.3)
        await ctx.send(f"🌍 **Traducción a {idioma}** 🌍\n\n{response}")

@bot.command(name='clima', aliases=['weather'])
async def clima(ctx, *, ciudad: str = None):
    if not ciudad:
        await ctx.send("Especifica una ciudad, genio 🌡️")
        return
    
    async with ctx.typing():
        prompt = f"Dame información actual del clima de {ciudad} (temperatura, condiciones, etc). Si no tienes datos actuales, dilo claramente."
        response = await get_ai_response(prompt, temperature=0.5)
        await ctx.send(f"🌤️ **Clima en {ciudad}** 🌤️\n\n{response}")

@bot.command(name='recordar', aliases=['reminder'])
async def recordar(ctx, tiempo: str = None, *, mensaje: str = None):
    if not tiempo or not mensaje:
        await ctx.send("Uso: `!recordar [tiempo] [mensaje]`\nEjemplo: `!recordar 10s revisar el horno`\nFormatos: 10s, 5m, 1h")
        return
    
    try:
        # Parsear tiempo
        if tiempo.endswith('s'):
            segundos = int(tiempo[:-1])
        elif tiempo.endswith('m'):
            segundos = int(tiempo[:-1]) * 60
        elif tiempo.endswith('h'):
            segundos = int(tiempo[:-1]) * 3600
        else:
            await ctx.send("Formato inválido. Usa: 10s (segundos), 5m (minutos), 1h (horas)")
            return
        
        if segundos > 86400:  # Máximo 24 horas
            await ctx.send("No puedo recordarte algo después de 24 horas, no soy tu mamá 😤")
            return
        
        await ctx.send(f"⏰ Ok, te recuerdo en {tiempo}: '{mensaje}'")
        
        await asyncio.sleep(segundos)
        await ctx.send(f"🔔 {ctx.author.mention} **RECORDATORIO:** {mensaje}")
        
    except ValueError:
        await ctx.send("Tiempo inválido. Usa números seguidos de s/m/h (ejemplo: 10s, 5m, 1h)")

@bot.command(name='avatar', aliases=['av', 'pfp'])
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(
        title=f"Avatar de {member.display_name}",
        color=member.color
    )
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# ==================== JUEGOS ====================

@bot.command(name='rps', aliases=['ppt'])
async def rps(ctx, opcion: str = None):
    if not opcion or opcion.lower() not in RPS_OPTIONS:
        await ctx.send("Juega: `!rps [piedra/papel/tijera]` 🪨📄✂️")
        return
    
    opcion = opcion.lower()
    bot_choice = random.choice(list(RPS_OPTIONS.keys()))
    
    user_emoji = RPS_OPTIONS[opcion]['emoji']
    bot_emoji = RPS_OPTIONS[bot_choice]['emoji']
    
    if opcion == bot_choice:
        resultado = "¡Empate! Qué aburrido 😑"
    elif RPS_OPTIONS[opcion]['gana'] == bot_choice:
        resultado = "Ganaste... esta vez 😤"
    else:
        resultado = "¡PERDISTE! Como siempre 😈"
    
    await ctx.send(
        f"**Tu elección:** {user_emoji} {opcion.title()}\n"
        f"**Mi elección:** {bot_emoji} {bot_choice.title()}\n\n"
        f"**Resultado:** {resultado}"
    )

# Iniciar el bot
if __name__ == '__main__':
    if not TOKEN:
        print("❌ Error: No se encontró DISCORD_TOKEN en .env")
    elif not GROQ_API_KEY:
        print("❌ Error: No se encontró GROQ_API_KEY en .env")
    else:
        print("🚀 Iniciando Toromax...")
        bot.run(TOKEN)