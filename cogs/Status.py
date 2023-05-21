import discord
from discord.ext import commands as cmds
from dotenv import load_dotenv
import os

load_dotenv()

class Status(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.hybrid_command(description="shows the status of a member")
    async def status(self, ctx: cmds.Context, member: discord.Member) -> None:
        mem = ctx.guild.get_member(member.id)

        usr_name = mem.name
        activity = mem.activity
        pfp = mem.display_avatar
        ison_type = getattr(mem.activity.type, 'name', 'unknown')
        auth = getattr(
            mem.activity, 
            'artist', 
            'unknown'
        )
        activity_img = getattr(
            mem.activity, 
            'album_cover_url', 
            'https://st4.depositphotos.com/14953852/24787/v/450/depositphotos_247872612-stock-illustration-no-image-available-icon-vector.jpg'
        )
        activity_name = getattr(activity, 'name', 'unknown')

        if activity_name == 'Spotify':
            activity_name = auth
        elif activity_name == 'Visual Studio Code':
            activity_img = 'https://logowik.com/content/uploads/images/visual-studio-code7642.jpg'

        embed = discord.Embed(
            title=f"** ~ STATUS (now) ~ **", 
            description=f"> {ison_type}: {activity_name}",
            color=discord.Color.random()
        )

        embed.set_author(name=usr_name, icon_url=pfp)
        embed.set_thumbnail(url=f"{activity_img}")
        
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Status(bot))

