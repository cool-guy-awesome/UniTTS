import discord
import dotenv
import os
import re
from collections import deque
from gtts import gTTS

dotenv.load_dotenv()
bot = discord.Client(intents=discord.Intents.all())
vc = None
queue = deque()

def _play_next(error=None):
    if queue:
        text = queue.popleft()
        filename = f"{hash(text)}.mp3"
        tts = gTTS(text)
        tts.save(filename)
        def after(error):
            os.remove(filename)
            _play_next()
        vc.play(discord.FFmpegPCMAudio(source=filename), after=after)

@bot.event
async def on_ready():
    global vc
    print("UniTTS is online!")
    guild = bot.get_guild(1437258836896514212)
    voice_channel = guild.get_channel(1437271857140076606)
    vc = await voice_channel.connect()

@bot.event
async def on_message(msg):
    if msg.author.bot or msg.channel.id != 1437271857140076606:
        return

    if msg.content.startswith("$"):
        message = msg.content[1:].strip()
        for mention in msg.mentions:
            name = mention.nick or mention.global_name
            message = re.sub(rf"<@!?{mention.id}>", name, message)
        message = re.sub(r"<t:\d+:\w+>", "", message)
        if vc.is_playing():
            queue.append(message)
        else:
            filename = f"{msg.id}.mp3"
            tts = gTTS(message)
            tts.save(filename)
            def after(error):
                os.remove(filename)
                _play_next()
            vc.play(discord.FFmpegPCMAudio(source=filename), after=after)
    elif msg.content == "MI BOMBO":
        vc.play(discord.FFmpegPCMAudio(source="mibombo.mp3"))

bot.run(os.getenv("BOT_TOKEN"))