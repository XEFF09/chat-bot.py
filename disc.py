import discord
from discord.ext import commands as cmds
from dotenv import load_dotenv
import speech_recognition as sr
import urllib.parse
import openai
import pyttsx3
import asyncio
import requests
import json
import os

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
guld_ids = (os.getenv('GUILD_IDS')).split(', ')
ids = [int(x) for x in guld_ids]
key = os.getenv('OPENAI_KEY')
bot = discord.Bot()
openai.api_key = key

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
    "voiceName": "ja-JP-Standard-B",
    "gender": "FEMALE"
    })
    headers = {
    'authority': 'freetts.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en,th-TH;q=0.9,th;q=0.8',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjI1NDM3NTcxNjQsImlhdCI6MTY3OTc1NzE1NCwiaXNzIjoia2VuIiwiZGF0YSI6eyJ1c2VybmFtZSI6IjE3Mi42OC4xODkuMTQ1IiwiaWQiOiIxNzIuNjguMTg5LjE0NSIsImxvZ2luX3RpbWUiOjE2Nzk3NTcxNTR9fQ.6-5FqmngwbhtgIfheFipCoXCK_TAQPZCgmMPMh5SZ9I',
    'content-type': 'application/json',
    'cookie': '_ga=GA1.2.1262120938.1679757155; _gid=GA1.2.1619799717.1679757155',
    'origin': 'https://freetts.com',
    'referer': 'https://freetts.com/Text-to-Speech/JapaneseTTS',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)['data']['audiourl']
    return res

def stt():
    query = ">>"
    r = sr.Recognizer()
    r.energy_threshold = 4000 # set the energy threshold
    timeout = 10
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            print("Sorry, I didn't hear anything within", timeout, "seconds. Please try again.")
            return query
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-EN')
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said. Please try again.")
    except sr.RequestError as e:
        print("Sorry, there was an error with the speech recognition service. Please try again later.")
        print(e)
    return query

async def text_gen(param):
    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=param,
    max_tokens=1024,
    n=1,
    temperature=0.5,
    )
    return response['choices'][0]['text']

@bot.event
async def on_ready():
    print(f"{bot.user} ready")

@bot.slash_command(guild_ids=ids)
async def join(ctx: cmds.Context, channel: discord.VoiceChannel):
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)

    await channel.connect()
    await ctx.respond(f"Joined {channel}")

@bot.slash_command(guild_ids=ids)
async def chat(interaction: discord.Interaction):
    await interaction.respond("I'm listening...")
    while True:
        query = stt().lower()
        if "stop" in query:
            break
        if ">>" in query:
            continue
        
        say = await text_gen(query)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(voice(trans(say))))
        await interaction.respond(say)
        interaction.voice_client.play(source)

        while interaction.voice_client.is_playing():
            await asyncio.sleep(1)

    await interaction.send("oke bye~ 👋")
    await interaction.voice_client.disconnect(force=True)

@bot.slash_command(guild_ids=ids)
async def type(interaction: discord.Interaction, message: str):
    say = await text_gen(message)
    await interaction.respond(say)

bot.run(TOKEN)

