import discord
from discord.ext import commands as cmds
from dotenv import load_dotenv
from typing import Optional, Literal
import asyncio
import json
import time
import os
import config

from additionals import Textgen, Voicegen, Memorize

load_dotenv()

# settings
directory_path = './prompts'
characters = [name[:-4] for name in os.listdir(directory_path)]
timescoped = 5

# async functions
class Tchat(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rdy = 0
        self.payload = None
        self.reply_lang = 'en'
        self.char_is_set = False
        self.converIsNotExist = None
        self.messages = None
        self.save_foldername = None
        self.char = None
        self.dialogue = 'prompts'
        self.memIdx = None
        self.voice = None
        self.user_id = None
        self.suffix = None
        self.vc_playing = False
        self.SPAM_COOLDOWN = 6
        self.last_message_time = None
        self.guild_id = None

    def getSuffix(self, exist: bool):
        os.makedirs(self.save_foldername, exist_ok=True)
        base_filename = 'conversation'
        count = 0

        filename = os.path.join(f'{self.save_foldername}/conversations', f'{base_filename}_{count}.txt')

        if exist == True:
            while os.path.exists(filename):
                count += 1
                filename = os.path.join(f'{self.save_foldername}/conversations', f'{base_filename}_{count}.txt')
        else:
            with open(filename, 'w', encoding = 'utf-8') as file:
                json.dump(self.messages, file, indent=4, ensure_ascii=False)

        return count

    @cmds.command()
    async def stop(self, ctx):
        if self.vc_playing == False:
            self.rdy = 0
            print("\nleaving:")
            await ctx.channel.send("> leaving..")
            await self.payload.send("``` voice chat off ```")
            await self.payload.voice_client.disconnect(force=True)

            try:
                self.messages.append({"role" : "assistant", "content" : "yes"})
                Memorize.memorize(messages=self.messages, save_foldername=f'{self.save_foldername}/conversations', suffix=self.suffix)
            except:
                print("memorize failed")
                pass

    @cmds.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
                return
        
        if ctx.content.startswith('.e'):
            self.bot.add_command(self.set_tchat)
            await self.stop(ctx)
        
        if self.rdy and ctx.content.startswith('.s'):
            if self.last_message_time is not None:
                time_diff = (ctx.created_at - self.last_message_time).total_seconds()

                if time_diff < self.SPAM_COOLDOWN:
                    self.vc_playing = False
                    self.last_message_time = ctx.created_at
                    return
                
            self.last_message_time = ctx.created_at
            await  self.bot.process_commands(ctx)
            self.vc_playing = True
            
            start_time = time.time()
            text = ctx.content.replace('.s', '')

            print("\nlistening:")

            try:
                channel_id = ctx.channel.id
                if ctx.channel.id == channel_id:
                    self.messages.append({"role" : "user", "content" : text})

                    try:
                        print("\ngenerating:")
                        say = Textgen.textGen(self.messages)
                        embed = discord.Embed(title=f"char: {self.char}", color=discord.Color.purple(), description=say)
                        await ctx.reply(embed=embed)
                
                        # audio_stream = f'https://api.streamelements.com/kappa/v2/speech?voice=Brian&text={say}'
                        # source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_stream))

                        Voicegen.voicegen(text=say, save_foldername=f'{self.save_foldername}/voices')

                        audio_path = f'history/{self.char}/{self.guild_id}/voices/'
                        audio_file = f'output.mp3'
                        full_audio_path = os.path.join(audio_path, audio_file)

                        try:
                            source = discord.FFmpegPCMAudio(full_audio_path)
                            self.payload.voice_client.play(source)
                        except FileNotFoundError:
                            print(f"Error: File not found - {audio_file}")
                        except Exception as e:
                            print(f"Error: {e}")

                        while self.payload.voice_client.is_playing():
                            await asyncio.sleep(1)
                            
                        start_time = time.time()
                    except Exception as e:
                        print(f"{e}")
                        print("Token limit exceeded")

            except:
                if time.time() - start_time > timescoped:
                    await ctx.channel.send("> ~listening")
                    print("\n~listening:")

        self.vc_playing = False

    @cmds.hybrid_command(description=f'characters: {characters}')
    async def set_tchat(self, ctx, char: str):
        if ctx.author.id not in config.OWNER:
            return await ctx.reply("> you have no perm to use this command!")
        
        self.guild_id = ctx.guild.id

        if not os.path.exists(f'history/{char}') or not os.path.exists(f'history/{char}/{self.guild_id}/'):
            if os.path.exists(f'prompts/{char}.txt'):
                os.makedirs(f'history/{char}/{self.guild_id}/conversations', exist_ok=True)
                os.makedirs(f'history/{char}/{self.guild_id}/voices', exist_ok=True)
            else:
                return await ctx.send(f"> character {char} not found")

        self.save_foldername = f'history/{char}/{self.guild_id}'
        self.char = char

        embed = discord.Embed(title=f"char settings: {self.char}", description=f'> index can be any within the list' if not self.converIsNotExist else f'> index can be None', color=discord.Color.green())
        embed.add_field(name="index(ls)", value=f"{self.memIdx}", inline=False)
        embed.add_field(name="path", value=f"{self.dialogue}", inline=True)
        embed.add_field(name="reply_lang", value=f"{self.reply_lang}", inline=True)
        await ctx.send(embed=embed)
        self.char_is_set = True

    @cmds.hybrid_command(description=f'please remind that the command is still WIP')
    async def tchat(self, ctx):
        if self.char_is_set:
            try:
                count = 0
                filename = os.path.join(f'{self.save_foldername}/conversations', f'conversation_{count}.txt')
                while os.path.exists(filename):
                    count += 1
                    filename = os.path.join(f'{self.save_foldername}/conversations', f'conversation_{count}.txt')

                if count == 0:
                    self.converIsNotExist = 1
                    self.dialogue = 'prompts'
                else:
                    self.converIsNotExist = 0
                    self.dialogue = 'history'
                
                self.memIdx = list(range(count))
            except:
                self.memIdx = [0]

            if self.converIsNotExist:
                self.suffix = self.getSuffix(exist=False)
                mount = '.txt'
            else:
                guild_id = ctx.guild.id
                self.suffix = self.getSuffix(exist=True) - 1
                mount = f'/{guild_id}/conversations/conversation_{self.suffix}.txt'

            # whether prompos/REM.txt or history/char/guild_id/conversation_index.txt
            with open(f'{self.dialogue}/{self.char}{mount}', "r", encoding='utf-8') as file:
                mode = file.read()

            if self.converIsNotExist:
                self.messages  = [{"role": "system", "content": f"{mode}"}]
            else:
                self.messages = json.loads(mode)

            # get bot in vc
            self.user_id = ctx.author.id
            voice_channel = ctx.author.voice.channel
            if self.voice and self.voice.is_connected():
                await self.voice.move_to(voice_channel)
            else:
                self.voice = await voice_channel.connect()

            await ctx.send("``` voice chat on ```")        
            self.bot.remove_command('set_tchat')
            self.rdy = 1
            self.payload = ctx
            self.reply_lang = 'en'

        else:
            embed = discord.Embed(title=f"ERR: tchat is not set", description="> it seems like you've not set the character yet", color=discord.Color.red())
            embed.add_field(name="follow the process", value=f"try to use /set_char char:<in the desc> path:<choices>", inline=False)
            await ctx.send(embed=embed)

    @cmds.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.user_id is not None and self.rdy:

            #bot itself changed
            if member == self.bot.user:
                if not after.channel:
                    self.voice = None

            #user changed
            elif member.id == self.user_id:
                if before.channel != after.channel:
                    if self.voice:
                        await self.voice.disconnect()
                    if after.channel:
                        voice_channel = await self.bot.fetch_channel(after.channel.id)
                        self.voice = await voice_channel.connect()
                        print(f"Joined {after.channel}")

                elif before.channel.guild.voice_client != after.channel.guild.voice_client:
                    if self.voice:
                        await self.voice.disconnect()
                    
async def setup(bot):
    await bot.add_cog(Tchat(bot))