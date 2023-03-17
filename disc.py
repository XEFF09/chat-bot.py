import discord
from discord.ext import commands as cmds
import os
from dotenv import load_dotenv
import openai
import pyttsx3
import speech_recognition as sr
import asyncio

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def commands():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-EN')

    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
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

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=query,
            max_tokens=1024,
            n=1,
            temperature=0.5,
        )

        say = response['choices'][0]['text']
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            f"https://tipme.in.th/api/tts/?text={say}&format=opus"))
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
