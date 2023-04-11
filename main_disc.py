import discord
from discord import Intents
from discord.ext import commands as cmds
from dotenv import load_dotenv
import speech_recognition as sr
import requests
import pyttsx3
import asyncio
import openai
import json
import os
import time

with open('prompts/Rem.txt', "r") as file:
    mode = file.read()

messages  = [
    {"role": "system", "content": f"{mode}"}
]
    
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
guld_ids = (os.getenv('GUILD_IDS')).split(', ')
ids = [int(x) for x in guld_ids]
key = os.getenv('OPENAI_KEY')
intents = Intents().all()
bot = cmds.Bot(command_prefix='>>', intents=intents)
openai.api_key = key

save_foldername = 'history'
keyword = 'hey'
timescoped = 5

def trans(say):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/get"
    querystring = {"langpair":"en|ja","q":say,"mt":"1","onlyprivate":"0","de":"a@b.c"}
    headers = {
        "X-RapidAPI-Key": "1f678aafcdmshd6d45bc81882a00p18750djsnefc88f21f555",
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text).get('responseData').get('translatedText')
    return data       

def voice(data):
    url = "https://freetts.com/api/TTS/SynthesizeText"
    payload = json.dumps({
    "text": data,
    "type": 0,
    "ssml": 0,
    "isLoginUser": 0,
    "country": "Japanese (Japan)",
    "voiceType": "Standard",
    "languageCode": "ja-JP",
    "voiceName": "ja-JP-Standard-A",
    "gender": "FEMALE"
    })
    headers = {
    'authority': 'freetts.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en,th-TH;q=0.9,th;q=0.8',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjI1NDUyNDIwOTksImlhdCI6MTY4MTI0MjA4OSwiaXNzIjoia2VuIiwiZGF0YSI6eyJ1c2VybmFtZSI6IjE3Mi42OC4yNDIuMjQ4IiwiaWQiOiIxNzIuNjguMjQyLjI0OCIsImxvZ2luX3RpbWUiOjE2ODEyNDIwODl9fQ.btWVQw4ygWKTBjJ9nBhX2txZ6jlipIB49EYDNeEXZmU',
    'content-type': 'application/json',
    'cookie': '_ga=GA1.2.1262120938.1679757155; _gid=GA1.2.1415340467.1681226232; _gat=1',
    'origin': 'https://freetts.com',
    'referer': 'https://freetts.com/',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)['data']['audiourl']
    return res
    
def textGen(messages):
    url = "https://api.openai.com/v1/chat/completions"
    payload = json.dumps({
    "model": "gpt-3.5-turbo",
    "messages": messages,
    "max_tokens": 50
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {key}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text).get('choices')[0].get('message').get('content')
    messages.append({"role": "system", "content": f"{data}"})
    return data

def memorize(suffix, save_foldername, messages):
    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')
    with open(filename, 'w', encoding = 'utf-8') as file:
        json.dump(messages, file, indent=4, ensure_ascii=False)

def waitHey(keyword='hey'):
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("\ninitiated:")
    while True:
        with mic as source:
            try:
                r.pause_threshold = 1
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source)
                query = r.recognize_google(audio).lower()
                if keyword in query:
                    break

            except sr.UnknownValueError:
                print("voice cracked")
                continue
            except sr.RequestError as e:
                print(f"GSR service issued; {e}")
                continue

def listenFor(timeout:int=30):
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=timeout)

    return audio

def getSuffix(save_foldername:str):
    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    suffix = 0
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')
    while os.path.exists(filename):
        suffix += 1
        filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')
    with open(filename, 'w', encoding = 'utf-8') as file:
        json.dump(messages, file, indent=4, ensure_ascii=False)
    return suffix

@bot.event
async def on_ready():
    print(f"{bot.user} ready")

@bot.hybrid_command(guild_ids=ids)
async def join(ctx, channel: discord.VoiceChannel):
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    
    await channel.connect()
    await ctx.send(f"``` {bot.user} has joined '{channel}' ```")
    await ctx.send("``` voice chat on ```")
    messages = [{"role": "system", "content": f"{mode}"}]


    while True:
        waitHey(keyword=keyword)
        suffix = getSuffix(save_foldername)
        start_time = time.time()
        while True:
            await ctx.send("> listening")
            print("\nlistening:")
            audio = listenFor()
            try:
                r = sr.Recognizer()
                query = r.recognize_google(audio, language="en-US")
                messages.append({"role" : "user", "content" : query})
            except :
                if time.time() - start_time > timescoped:
                    await ctx.send("> ~listening")
                    print("\n~listening:")
                    break
                continue
            
            if "quit" in query.lower() or "quit." in query.lower():
                messages.append({"role" : "system", "content" : "yes"})
                memorize(suffix=suffix, save_foldername=save_foldername, messages=messages)
                await ctx.channel.send("> leaving..")
                await ctx.send("``` voice chat off ```")
                await ctx.voice_client.disconnect(force=True)
                raise SystemExit
            
            try:
                await ctx.channel.send("> generating")
                print("\ngenerating:")
                say = textGen(messages)
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(voice(trans(say))))
                ctx.voice_client.play(source)
                await ctx.channel.send(say)
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)
                start_time = time.time()
            except Exception as e:
                print(f"{e}")
                print("Token limit exceeded, clearing messsages list and restarting")
                suffix = getSuffix(save_foldername)

bot.run(TOKEN)