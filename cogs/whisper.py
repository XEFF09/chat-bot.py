import discord
import typing
from typing import Literal
from discord.ext import commands as cmds
from dotenv import load_dotenv
import random as rand
import os

load_dotenv()

guld_ids = (os.getenv('GUILD_IDS')).split(', ')
ids = [int(x) for x in guld_ids]

class whisper(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.hybrid_command()
    async def whisper(self, ctx, *, text: str, to: discord.Member = None):
        if to is None:
            to = rand.choice(ctx.guild.members)
        
        await ctx.send(f"> {ctx.author.mention} wanted to tell {to.mention} that '{text}'")

async def setup(bot):
    await bot.add_cog(whisper(bot))