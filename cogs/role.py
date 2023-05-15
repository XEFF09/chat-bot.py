import discord
from discord.ext import commands as cmds
from dotenv import load_dotenv
import os

load_dotenv()

guld_ids = (os.getenv('GUILD_IDS')).split(', ')
ids = [int(x) for x in guld_ids]

class Role(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.place = None

    @cmds.hybrid_command(guld_ids=ids)
    async def role(self, ctx):
        message = await ctx.send("select ur role here :)")
        self.place = message.id
        emoji = discord.utils.get(self.bot.emojis, name='10s')
        await message.add_reaction(emoji)

    @cmds.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.place is not None:
            message_id = payload.message_id
            if message_id == self.place:
                guld_id = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guld_id.roles, name=payload.emoji.name)

                if role is not None:
                    member = discord.utils.get(guld_id.members, id=payload.user_id)
                    
                    if member is not None:
                        await member.add_roles(role)
                        print(f"added {role.name} to {member.name}")
                    else:
                        print("member not found.")

                else:
                    print("role not found.")

    @cmds.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if self.place is not None:
            message_id = payload.message_id
            if message_id == self.place:
                guld_id = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guld_id.roles, name=payload.emoji.name)
                
                if role is not None:
                    member = discord.utils.get(guld_id.members, id=payload.user_id)
        
                    if member is not None:
                        await member.remove_roles(role)
                        print(f"removed {role.name} to {member.name}")
                    else:
                        print("member not found.")

                else:
                    print("role not found.")
                


async def setup(bot):
    await bot.add_cog(Role(bot))