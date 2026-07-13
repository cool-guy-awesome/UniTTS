import subprocess, random, requests, os
from gtts import gTTS # type: ignore

def generate_tts(message, voice, filename):
    if message == "MI BOMBO":
        os.system("cp mibombo.mp3 "+filename)
        return
    elif message == "fish":
        os.system("cp fish.mp3 "+filename)
        return
    elif message == "Hi! I'm the Joke-Explainer 7000, and I'm here to be your guide.":
        os.system("cp welcome.mp3 "+filename)
        return
    elif message == "and i was like":
        os.system("cp andiwaslike.mp3 "+filename)
        return
    elif message == "penis":
        os.system("cp penis.mp3 "+filename)
        return
    elif message == "oh":
        os.system("cp oh.mp3 "+filename)
        return
    if voice["type"] == "gtts":
        tts = gTTS(message, lang=voice["language"])
        tts.save(filename)
    elif voice["type"] == "sam":
        pitch = str(voice["pitch"])
        speed = str(voice["speed"])
        mouth = str(voice["mouth"])
        throat = str(voice["throat"])
        randomnum = random.randint(0, 999)
        try:
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
        except FileNotFoundError:
            print("im evil.")
            pitch = str(voice["pitch"])
            speed = str(voice["speed"])
            r = requests.get(f"https://samtts.com/api/demo/sapi4-tts?text={message}&voice=Sam&pitch={str(pitch)}&speed={str(speed)}")
            open(str(randomnum)+".wav", "wb").write(r.content)
            os.system(f"ffmpeg -i {str(randomnum)}.wav -af \"volume=1.0\" -b:a 320k {filename}")
            os.system(f"rm {str(randomnum)}.wav")
    elif voice["type"] == "ms-sam":
        randomnum = random.randint(0, 999)
        pitch = str(voice["pitch"])
        speed = str(voice["speed"])
        r = requests.get(f"https://samtts.com/api/demo/sapi4-tts?text={message}&voice=Sam&pitch={str(pitch)}&speed={str(speed)}")
        open(str(randomnum)+".wav", "wb").write(r.content)
        os.system(f"ffmpeg -i {str(randomnum)}.wav -af \"volume=1.0\" -b:a 320k {filename}")
        os.system(f"rm {str(randomnum)}.wav")
