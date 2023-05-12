from discord import Intents
from discord.ext import commands as cmds
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
intents = Intents().all()
intents.members = True
bot = cmds.Bot(command_prefix='>>', intents=intents)

async def load():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")

async def main():
    await load()
    await bot.start(TOKEN)

@bot.event
async def on_ready():
    print(f'{bot.user} is now ready!')

asyncio.run(main())
