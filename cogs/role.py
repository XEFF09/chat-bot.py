import discord
from discord.ext import commands as cmds
from dotenv import load_dotenv
import os

load_dotenv()

guld_ids = (os.getenv('GUILD_IDS')).split(', ')
ids = [int(x) for x in guld_ids]

place = 1106522326499078185

class role(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        if message_id == place:
            guld_id = self.bot.get_guild(payload.guild_id)
            role = discord.utils.get(guld_id.roles, name=payload.emoji.name)

            if role is not None:
                member = discord.utils.get(guld_id.members, id=payload.user_id)

                if member is not None:
                    await member.add_roles(role)
                    print(f"Added {role.name} to {member.name}")
                else:
                    print("Member not found.")

            else:
                print("Role not found.")

    @cmds.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        if message_id == place:
            guld_id = self.bot.get_guild(payload.guild_id)
            role = discord.utils.get(guld_id.roles, name=payload.emoji.name)

            if role is not None:
                member = discord.utils.get(guld_id.members, id=payload.user_id)

                if member is not None:
                    await member.remove_roles(role)
                    print(f"Removed {role.name} to {member.name}")
                else:
                    print("Member not found.")

            else:
                print("Role not found.")
                

async def setup(bot):
    await bot.add_cog(role(bot))