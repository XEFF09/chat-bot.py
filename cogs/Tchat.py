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

import requests

import google.generativeai as genai
import google.ai.generativelanguage as glm

load_dotenv()
googleai_key = os.getenv('GOOGLEAI_KEY')
genai.configure(api_key=googleai_key)
model = genai.GenerativeModel('gemini-pro')

# settings
directory_path = './prompts'
characters = [name[:-4] for name in os.listdir(directory_path)]
timescoped = 5

# async functions
class Tchat(cmds.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.payload = None
        self.reply_lang = 'en'
        self.char_is_set = False
        self.converIsNotExist = None
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
        self.chat = model.start_chat(history=[])
        self.personality = []

    def getSuffix(self, exist: bool):
        os.makedirs(self.save_foldername, exist_ok=True)
        base_filename = 'conversation'
        count = 0

        filename = os.path.join(f'{self.save_foldername}/conversations', f'{base_filename}_{count}.json')

        if exist == True:
            while os.path.exists(filename):
                count += 1
                filename = os.path.join(f'{self.save_foldername}/conversations', f'{base_filename}_{count}.json')
        else:
            with open(filename, 'w', encoding = 'utf-8') as file:
                json.dump(self.personality, file, indent=4, ensure_ascii=False)

        return count

    @cmds.command()
    async def stop(self, ctx):
        if self.vc_playing == False:
            self.rdy = 0
            print("\nleaving:")
            await self.payload.send("``` voice chat off ```")
            await self.payload.voice_client.disconnect(force=True)

            try:
                messages = []
                for i in self.chat.history:
                    messages.append({
                        "role": f"{i.role}",
                        "parts": f"{i.parts[0].text}"
                    })

                Memorize.memorize(
                    messages=(messages), 
                    save_foldername=f'{self.save_foldername}/conversations', 
                    suffix=self.suffix,
                    char=self.char,
                    guild_id=self.guild_id
                )
            except Exception as e:
                print(f"Memorize Failed: {e}")

    @cmds.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
                return
        
        if ctx.content.startswith('.e'):
            self.bot.add_command(self.set_tchat)
            await self.stop(ctx)
        
        elif self.rdy and ctx.content.startswith('.s'):
            if self.last_message_time is not None:
                elapsed = (ctx.created_at - self.last_message_time).total_seconds()

                if elapsed < self.SPAM_COOLDOWN:
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
                    try:
                        print("\ngenerating:")
                        img_path = None
                        if ctx.attachments:
                            if ctx.attachments[0].content_type.startswith('image'):
                                await ctx.attachments[0].save(f'{self.save_foldername}/images/image.jpg')
                                img_path = f'{self.save_foldername}/images/image.jpg'

                        say = Textgen.textGen(text=text, img_path=img_path, chat=self.chat)
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
                            await asyncio.sleep(2)
                            
                        start_time = time.time()
                    except Exception as e:
                        print(f"{e}")
                        print("Token limit exceeded")

            except:
                if time.time() - start_time > timescoped:
                    print("\n~listening:")

        self.vc_playing = False

    @cmds.hybrid_command(description=f'characters: {characters}')
    async def set_tchat(self, ctx, char: str):
        if ctx.author.id not in config.OWNER:
            return await ctx.reply("> you have no perm to use this command!")
        
        self.guild_id = ctx.guild.id

        char_history = f'history/{char}'

        if not os.path.exists(char_history) or not os.path.exists(f'{char_history}/{self.guild_id}/'):
            if os.path.exists(f'prompts/{char}.txt'):
                os.makedirs(f'{char_history}/{self.guild_id}/conversations', exist_ok=True)
                os.makedirs(f'{char_history}/{self.guild_id}/voices', exist_ok=True)
                os.makedirs(f'{char_history}/{self.guild_id}/images', exist_ok=True)
            else:
                return await ctx.send(f"> character {char} not found")

        self.save_foldername = f'{char_history}/{self.guild_id}'
        self.char = char

        

        try:
                count = 0
                filename = os.path.join(f'{self.save_foldername}/conversations', f'conversation_{count}.json')
                while os.path.exists(filename):
                    count += 1
                    filename = os.path.join(f'{self.save_foldername}/conversations', f'conversation_{count}.json')

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
            mount = f'/{guild_id}/conversations/conversation_{self.suffix}.json'

        with open(f'{self.dialogue}/{self.char}{mount}', "r", encoding='utf-8') as file:
            mode = file.read()

        if self.converIsNotExist:
            self.chat.history = [
                glm.Content(
                    role = "user",
                    parts = [
                        glm.Part(text=f"{mode}"),
                    ],
                ),
                glm.Content(
                    role = "model",
                    parts = [
                        glm.Part(text=f""),
                    ],
                )
            ]
        else:
            with open(f'{self.dialogue}/{self.char}/{self.guild_id}/conversations/conversation_{self.suffix}.json', "r", encoding='utf-8') as file:
                memory = json.load(file)
            
            for i in memory:
                self.chat.history.append(
                    glm.Content(
                        role = f"{i['role']}",
                        parts = [
                            glm.Part(text=f"{i['parts']}"),
                        ],
                    )
                )

        embed = discord.Embed(title=f"char settings: {self.char}", color=discord.Color.green())
        embed.add_field(name="index(ls)", value=f"{self.memIdx}", inline=False)
        embed.add_field(name="path", value=f"{self.dialogue}", inline=True)
        embed.add_field(name="reply_lang", value=f"{self.reply_lang}", inline=True)
        await ctx.send(embed=embed)
        self.char_is_set = True

    @cmds.hybrid_command()
    async def tchat(self, ctx):
        if self.char_is_set:

            # get bot in vc
            self.payload = ctx
            self.user_id = self.payload.author.id
            voice_channel = self.payload.author.voice.channel

            if self.voice and self.voice.is_connected():
                await self.voice.move_to(voice_channel)
            else:
                self.voice = await voice_channel.connect()

            self.bot.remove_command('set_tchat')
            self.rdy = 1
            self.reply_lang = 'en'
            await self.payload.send("``` voice chat on ```")        

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