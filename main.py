from typing import Optional, Literal
from discord import Intents
from discord.ext import commands as cmds
from dotenv import load_dotenv
import asyncio
import os
import config

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents().all()
bot = cmds.Bot(command_prefix='>> ', intents=intents)

async def load():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")

async def main():
    await load()
    await bot.start(TOKEN)

@bot.event
async def on_ready():
    print(f'{bot.user} bot: ready')

@bot.command()
@cmds.guild_only()
async def sync(ctx: cmds.Context, spec: Optional[Literal['add', 'rem']] = None) -> None:
    if ctx.author.id not in config.OWNER:
        return
    
    if spec == 'add':
        synced = await ctx.bot.tree.sync()
    elif spec == 'rem':
        ctx.bot.tree.clear_commands(guild=None)
        await ctx.bot.tree.sync(guild=None)
        synced = []

    await ctx.channel.send(f"total synced: {len(synced)}")

asyncio.run(main())
