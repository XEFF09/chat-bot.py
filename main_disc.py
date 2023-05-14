from typing import Optional, Literal
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

@bot.command()
@cmds.is_owner()
async def sync(ctx: cmds.Context, spec: Optional[Literal['add', 'rem']] = None) -> None:
    if spec == 'add':
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f'total synced: {len(fmt)}')
    elif spec == 'rem':
        ctx.bot.tree.clear_commands(guild=None)
        await ctx.bot.tree.sync(guild=None)
        await ctx.send(f'total unsynced: all')

asyncio.run(main())
