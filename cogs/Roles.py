import discord
from discord.ext import commands as cmds
from typing import Optional, Literal
from dotenv import load_dotenv
import aiohttp
import config

load_dotenv()

class Roles(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.place = {}
        self.session = aiohttp.ClientSession()
        self.ls = {}

    @cmds.hybrid_command(description="make a selector section")
    async def roles(self, ctx, types: Optional[Literal['yr', 'fav']] = None):
        if ctx.author.id not in config.OWNER:
            return await ctx.reply("> you have no perm to use this command!")
        
        guild = ctx.guild
        guild_id = ctx.guild.id
        role_names = [role.name for role in guild.roles]
        emoji_names = [emoji.name for emoji in guild.emojis]
        common_names = list(set(role_names) & set(emoji_names))

        if types == 'yr':
            for_yr = [i for i in common_names if i.startswith("ku")]
            self.ls[guild_id] = for_yr
        elif types == 'fav':
            for_fav = [i for i in common_names if i.startswith("fav")]
            self.ls[guild_id] = for_fav
        else:
            types = "role"
            self.ls[guild_id] = common_names

        if self.ls[guild_id]:
            message = await ctx.send(f"select ur {types} here :)")
            if guild_id not in self.place:
                self.place[guild_id] = []
            self.place[guild_id].append(message.id)
            for i in self.ls[guild_id]:
                emoji = discord.utils.get(self.bot.emojis, name=i)
                await message.add_reaction(emoji)

        else:
            await ctx.reply("> no roles found")
        
    async def handle_reaction(self, payload, add_role):
        guild_id = payload.guild_id
        if self.place[guild_id] is not None:
            message_id = payload.message_id
            if message_id in self.place[guild_id]:
                guild = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, name=payload.emoji.name)

                if role is not None:
                    member = guild.get_member(payload.user_id)

                    if member is not None:
                        if add_role:
                            await member.add_roles(role)
                            print(f"added {role.name} to {member.name}")
                        else:
                            await member.remove_roles(role)
                            print(f"removed {role.name} from {member.name}")
                    else:
                        print("member not found")

                else:
                    print("role not found")

    @cmds.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.handle_reaction(payload, add_role=True)

    @cmds.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.handle_reaction(payload, add_role=False)
                
    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @cmds.hybrid_command(description="add/remove a role")
    @cmds.has_permissions(manage_roles=True, manage_emojis=True)
    async def manage_role(self, ctx: cmds.Context, name_txt: str, *, emoji_url = None, spec: Optional[Literal['add', 'rem']] = 'add'):
        if ctx.author.id not in config.OWNER:
            return await ctx.reply("> you have no perm to use this command!")
        
        guild = ctx.guild
        guild_id = ctx.guild.id
        emoji_names = [emoji.name for emoji in guild.emojis]
        role_names = [role.name for role in guild.roles]
        pfp = ctx.author.display_avatar

        if spec == 'add':
            if name_txt not in emoji_names and name_txt not in role_names:

                if guild_id not in self.ls:
                    self.ls[guild_id] = []

                async with ctx.typing():
                    try:
                        async with self.session.get(emoji_url) as resp:
                            emoji_image = await resp.read()
                    except:
                        return await ctx.reply("> failed to fetch image")

                    try:
                        role = await guild.create_role(name=name_txt)
                        emoji = await guild.create_custom_emoji(name=role.name, image=emoji_image)
                        self.ls[guild_id].append(emoji.name)
                    except discord.HTTPException:
                        await ctx.reply("> failed to create role/emoji")

                embed = discord.Embed(
                    title=f"ROLE: {role.name} added", 
                    description=f"> use /roles to create a field",
                    color=discord.Color.random()
                )

                embed.set_author(name=ctx.author.name, icon_url=pfp)
                embed.add_field(name="emoji", value=f"{emoji}", inline=True)
                embed.add_field(name="role", value=f"{role.name}", inline=True)
                
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    title=f"ERR: {name_txt} already exists",
                    description="> there are 2 methods in order to solve this",
                    color=discord.Color.red()
                )

                embed.set_author(name=ctx.author.name, icon_url=pfp)
                embed.add_field(name="1.check", value=f"try to check if the {name_txt} already exists in the role/emoji", inline=False)
                embed.add_field(name="2.remove", value=f"try to remove it by using /manage_role name_txt:{name_txt} spec:rem", inline=False)
                
                await ctx.send(embed=embed)

        elif spec == 'rem':
            guild = ctx.guild
            emoji = discord.utils.get(guild.emojis, name=name_txt)
            role = discord.utils.get(guild.roles, name=name_txt)

            if emoji is not None or role is not None:

                if emoji is not None:
                    await emoji.delete()

                if role is not None:
                    await role.delete()
                
                await ctx.send(f"> role/emoji: '{name_txt}' deleted.")
                
            else:
                await ctx.send(f"> role/emoji: '{name_txt}' not found.")

    @manage_role.error
    async def create_emoji_error(ctx, error):
        if isinstance(error, cmds.MissingPermissions):
            await ctx.reply("> you have no perm to create emojis!")

async def setup(bot):
    await bot.add_cog(Roles(bot))