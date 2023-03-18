import discord
from discord.ext import commands as cmds
import os
from dotenv import load_dotenv
import openai
import pyttsx3
import speech_recognition as sr
import asyncio
import requests
import json
import urllib.parse

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def voice(data):
    url = "https://ttsmp3.com/makemp3_new.php"
    word = data
    encoded_word = urllib.parse.quote(word, encoding='utf-8')
    payload=f'msg={encoded_word}&lang=Mizuki&source=ttsmp3'
    headers = {
    'Accept': '*/*',
    'Accept-Language': 'en,th-TH;q=0.9,th;q=0.8',
    'Connection': 'keep-alive',
    'Content-type': 'application/x-www-form-urlencoded',
    'Cookie': '_ga=GA1.2.1856036508.1679137284; _gid=GA1.2.1028617805.1679137284; _gat_gtag_UA_28351091_23=1',
    'Origin': 'https://ttsmp3.com',
    'Referer': 'https://ttsmp3.com/text-to-speech/Japanese/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)['URL']
    return data

def commands():
    query = ">>"
    r = sr.Recognizer()
    r.energy_threshold = 4000 # set the energy threshold

    timeout = 5
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=timeout)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-EN')

    except sr.WaitTimeoutError:
        print("Sorry, I didn't hear anything within", timeout, "seconds.")

    return query

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
guld_ids = (os.getenv('GUILD_IDS')).split(', ')
ids = [int(x) for x in guld_ids]
key = os.getenv('OPENAI_KEY')

bot = discord.Bot()
openai.api_key = key

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
        query = commands().lower()
        if "stop" in query:
            break
        if ">>" in query:
            continue
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=query,
            max_tokens=1024,
            n=1,
            temperature=0.5,
        )

        say = response['choices'][0]['text']

        url = "https://translated-mymemory---translation-memory.p.rapidapi.com/get"

        querystring = {"langpair":"en|ja","q":say,"mt":"1","onlyprivate":"0","de":"a@b.c"}

        headers = {
            "X-RapidAPI-Key": "1f678aafcdmshd6d45bc81882a00p18750djsnefc88f21f555",
            "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        data = json.loads(response.text).get('responseData').get('translatedText')
        

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(voice(data)))
        interaction.voice_client.play(source)

        while interaction.voice_client.is_playing():
            await asyncio.sleep(1)

    await interaction.send("oke bye~ 👋")
    await interaction.voice_client.disconnect(force=True)

@bot.slash_command(guild_ids=ids)
async def type(interaction: discord.Interaction, message: str):

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message,
        max_tokens=60
    )   
    say = response['choices'][0]['text']
    await interaction.respond(say)

bot.run(TOKEN)

