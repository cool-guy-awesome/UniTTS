import discord, json, os, re, subprocess, random, sys, time, traceback, requests
import dotenv # type: ignore
from collections import deque
from gtts import gTTS # type: ignore
from discord import app_commands

dotenv.load_dotenv()
bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)
voice_channel = None
vc = None
queue = deque()
language_choices = []
langs = {"de":"German","en":"English","es":"Spanish","fi":"Finnish","fr":"French","hu":"Hungarian","id":"Indonesian","is":"Icelandic","it":"Italian","ja":"Japanese","ko":"Korean","lt":"Lithuanian","ne":"Nepali","nl":"Dutch","no":"Norwegian","pa":"Punjabi (Gurmukhi)","pl":"Polish","pt-PT":"Portuguese (Portugal)","ro":"Romanian","ru":"Russian","sv":"Swedish","tr":"Turkish","uk":"Ukrainian","vi":"Vietnamese","zh-CN":"Chinese (Simplified)"}
for lang_code, lang_name in langs.items():
    language_choices.append(app_commands.Choice(name=lang_name, value=lang_code))

class KillEveryoneError(Exception):
    """Kill Everyone"""
    pass

def read_data():
    return json.load(open("data.json", "rb"))

def write_data(data):
    return open("data.json", "w").write(json.dumps(data))

def generate_tts(message, voice, filename):
    if voice["type"] == "gtts":
        tts = gTTS(message, lang=voice["language"])
        tts.save(filename)
    elif voice["type"] == "sam":
        pitch = str(voice["pitch"])
        speed = str(voice["speed"])
        mouth = str(voice["mouth"])
        throat = str(voice["throat"])
        randomnum = random.randint(0, 999)
        if os.name == "nt":
            subprocess.run([
                "sam.exe",
                "-wav", str(randomnum)+".wav",
                message,
                "-pitch", str(pitch),
                "-speed", str(speed),
                "-mouth", str(mouth),
                "-throat", str(throat),
            ])
        else:
            subprocess.run([
                "./sam",
                "-wav", str(randomnum)+".wav",
                message,
                "-pitch", str(pitch),
                "-speed", str(speed),
                "-mouth", str(mouth),
                "-throat", str(throat),
            ])
        os.system(f"ffmpeg -i {str(randomnum)}.wav -af \"volume=0.5\" -b:a 320k {filename}")
        os.system(f"rm {str(randomnum)}.wav")
    elif voice["type"] == "ms-sam":
        randomnum = random.randint(0, 999)
        pitch = str(voice["pitch"])
        speed = str(voice["speed"])
        r = requests.get(f"https://samtts.com/api/demo/sapi4-tts?text={message}&voice=Sam&pitch={str(pitch)}&speed={str(speed)}")
        open(str(randomnum)+".wav", "wb").write(r.content)
        os.system(f"ffmpeg -i {str(randomnum)}.wav -af \"volume=1.0\" -b:a 320k {filename}")
        os.system(f"rm {str(randomnum)}.wav")

def _play_next(error=None):
    if queue:
        msg = queue.popleft()
        filename = f"{msg.id}.mp3"
        voice = read_data()["user_settings"][str(msg.author.id)]["voice"]
        message = msg.content[1:].strip() if msg.content.startswith("$") else msg.content.strip()
        if message.startswith("https://"): return
        for mention in msg.mentions:
            name = mention.nick or mention.global_name
            message = re.sub(rf"<@!?{mention.id}>", name, message)
        message = re.sub(r"<t:\d+:\w+>", "", message)
        message = re.sub(r"<:\w+:\d+>", "", message)
        message = message.encode("ascii", "ignore").decode("ascii")
        if not message: return
        generate_tts(message, voice, filename)
        def after(error):
            os.remove(filename)
            _play_next()
        vc.play(discord.FFmpegPCMAudio(source=filename), after=after)

@bot.event
async def on_ready():
    global vc, voice_channel
    await tree.sync()
    print("UniTTS is online!")
    guild = bot.get_guild(1437258836896514212)
    voice_channel = guild.get_channel(1437271857140076606)
    vc = await voice_channel.connect()

@bot.event
async def on_error(event, *args, **kwargs):
    exc_type, exc_value, _ = sys.exc_info()
    filename = str(time.time_ns())+".txt"
    if not "logs" in os.listdir():
        os.mkdir("logs")
    traceback.print_exc(file=open(f"logs/{filename}", "w"))
    await voice_channel.send(f"<@932666698438418522> yo twin, {exc_type.__name__}: {exc_value}\ni printed a log in logs/{filename} if you want\nalso heres a burger", file=discord.File("burger.png"))

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    exc = error.original if isinstance(error, discord.app_commands.CommandInvokeError) else error
    if type(exc).__name__ != "KillEveryoneError":
        filename = str(time.time_ns()) + ".txt"
        os.makedirs("logs", exist_ok=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=open(f"logs/{filename}", "w"))
        await voice_channel.send(
            f"<@932666698438418522> yo twin, {type(exc).__name__}: {exc}\n"
            f"i printed a log in logs/{filename} if you want\nalso heres a burger",
            file=discord.File("burger.png"),
        )
    else:
        await voice_channel.send(
            "i killed everyone\nalso heres a burger",
            file=discord.File("burger.png"),
        )

@bot.event
async def on_message(msg):
    if msg.author.bot or msg.channel.id != 1437271857140076606 or not vc:
        return
    data = read_data()
    if str(msg.author.id) not in data["user_settings"]:
        data["user_settings"][str(msg.author.id)] = {
            "always_speak": False,
            "voice": {
                "type": "gtts",
                "language": "en",
                "pitch": 64,
                "speed": 72,
                "mouth": 128,
                "throat": 128
            }
        }
        write_data(data)

    always_speak = data["user_settings"][str(msg.author.id)]["always_speak"]
    if msg.content == "MI BOMBO":
        vc.play(discord.FFmpegPCMAudio(source="mibombo.mp3"))
    elif msg.content.startswith("$") or always_speak:
        if len(msg.content) > 500:
            await msg.channel.send(f"<@{msg.author.id}> Your message is too long! (Max 500 Characters)")
            return
        if vc.is_playing():
            queue.append(msg)
        else:
            filename = f"{msg.id}.mp3"
            voice = data["user_settings"][str(msg.author.id)]["voice"]
            message = msg.content[1:].strip() if msg.content.startswith("$") else msg.content.strip()
            if message.startswith("https://"): return
            for mention in msg.mentions:
                name = mention.nick or mention.global_name or mention.name
                message = re.sub(rf"<@!?{mention.id}>", name, message)
            message = re.sub(r"<t:\d+:\w+>", "", message)
            message = re.sub(r"<:\w+:\d+>", "", message)
            message = message.encode("ascii", "ignore").decode("ascii")
            if not message or not any(c.isalpha() for c in message): return
            generate_tts(message, voice, filename)
            def after(error):
                os.remove(filename)
                _play_next()
            if not vc.is_playing(): # the fuck? this can happen sometimes, idk why.
                vc.play(discord.FFmpegPCMAudio(source=filename), after=after)
            else:
                queue.append(msg)

@tree.command(name="ping", description="Ping...")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency*1000)}ms")

@tree.command(name="killeveryone", description="KillEveryone")
async def killeveryone(interaction: discord.Interaction):
    await interaction.response.send_message("Killed everyone", ephemeral=True)
    raise KillEveryoneError("Everyone died")

@tree.command(name="skip-tts", description="Skip the current TTS.")
async def ping(interaction: discord.Interaction):
    if vc.is_playing():
        vc.stop()
        await interaction.response.send_message("Skipped the TTS")
    else:
        await interaction.response.send_message("no TTS is playing you dummy dum dum")

@tree.command(name="set-voice", description="Sets your voice settings")
@app_commands.describe(
    always_speak="Always speak when you send a message",
    tts="Text To Speech system",
    language="Google TTS Voice Language (optional)",
    pitch="Voice Pitch (max 192) (optional)",
    speed="Voice Speed (max 192) (optional)",
    mouth="SAM Voice Mouth (max 192) (optional)",
    throat="SAM Voice Throat (max 192) (optional)"
)
@app_commands.choices(
    tts=[
        app_commands.Choice(name="Google TTS", value="gtts"),
        app_commands.Choice(name="SAM (C64)", value="sam"),
        app_commands.Choice(name="Microsoft SAM", value="ms-sam")
    ],
    language=language_choices
)
async def set_voice(
    interaction: discord.Interaction,
    always_speak: bool,
    tts: app_commands.Choice[str],
    language: app_commands.Choice[str] = "en",
    pitch: int = 255,
    speed: int = 255,
    mouth: int = 128,
    throat: int = 128
):
    if pitch == 255:
        match tts.value:
            case "sam":
                pitch = 64
            case "ms-sam":
                pitch = 100
    if speed == 255:
        match tts.value:
            case "sam":
                speed = 72
            case "ms-sam":
                speed = 150
    data = read_data()
    data["user_settings"][str(interaction.user.id)] = {
        "always_speak": always_speak,
        "voice": {
            "type": tts.value,
            "language": language.value if language != "en" else "en",
            "pitch": min(pitch, 192),
            "speed": min(speed, 192),
            "mouth": min(mouth, 192),
            "throat": min(throat, 192)
        }
    }
    write_data(data)
    await interaction.response.send_message("Updated settings!", ephemeral=True)

bot.run(os.getenv("BOT_TOKEN"))
