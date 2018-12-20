import discord
from discord.ext import commands
import json
import io
import os
import random

from utils.HelpUtility import HelpSetup

class Basic(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['commands', 'cmds'])
    async def thelp(self, ctx, *, command: str = None):
        '''Справочник по командам.'''
        data = await HelpSetup(ctx, self.bot, command)
        await ctx.send(embed=data)

    def manage_embed(self, member):
        embed = discord.Embed(title='Новый участник прибыл!',
                              description=f'**Привет, {member.mention}, добро пожаловать на {member.guild.name}!**',
                              color=0x59C7FF)

        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_footer(text=f'Приветствуем на сервере {member.guild.name}!',
                         icon_url=member.guild.icon_url)
        return embed

    async def on_member_join(self, member):
        guild = discord.utils.get(self.bot.guilds, id=327110418457690112)
        channel = discord.utils.get(guild.text_channels, id=431879758347894815)

        await channel.send(embed=self.manage_embed(member))

    @commands.command(name='view-welcome', aliases=['welcome'])
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        await ctx.send(embed=self.manage_embed(ctx.author))
    
    @commands.command(name='say')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def say(self, ctx, *, text: str):
        '''Отправка сообщения от моего имени.'''
        await ctx.message.delete()
        await ctx.send(text)
    
    async def on_message(self, m):
        if m.author.bot:
            return False
        if m.content.lower() == 'привет':
            await m.channel.send(f'***{m.author.mention}, приветствую тебя на сервере {m.channel.guild.name}!***')
        if m.content.lower() == 'пока':
            await m.channel.send(f'***{m.author.mention}, пока. Спасибо за то, что вы с нами на {m.channel.guild.name}!***')
        if m.content.lower().split(' ')[0] == 'бан':
            try:
                user = m.content.lower().split(' ')[1]

            except:
                await m.channel.send(file=discord.File(fp='ban/' + random.choice(os.listdir('ban'))))
                return False

            try:
                user = discord.utils.get(m.guild.members, mention=user).mention
            except:
                try:
                    user = discord.utils.get(m.guild.members, id=user).mention
                except:
                    try:
                        user = discord.utils.get(m.guild.members, name=user).mention
                    except:
                        pass

            await m.channel.send(f'{m.author.mention} банит {user}',
                file=discord.File(fp='ban/' + random.choice(os.listdir('ban'))))

def setup(bot):
    bot.add_cog(Basic(bot))