import discord
from discord.ext import commands
import json
import io

from utils.HelpUtility import HelpSetup

class Basic(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['commands', 'cmds'])
    async def thelp(self, ctx, *, command: str = None):
        data = await HelpSetup(ctx, self.bot, command)
        await ctx.send(embed=data)
    
    @commands.command(name='set_first')
    @commands.has_permissions(manage_guild=True)
    async def set_first(self, ctx, *, name: str):
        if ctx.author.id not in [347432332208373760, 297421244402368522]:
            return False
        data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
        data['name_first'] = name
        json.dump(data, io.open('config.json', 'w', encoding='utf-8-sig'), indent=2)
        await ctx.send(':ok_hand:')
    
    @commands.command(name='set_second')
    @commands.has_permissions(manage_guild=True)
    async def set_second(self, ctx, *, name: str):
        if ctx.author.id not in [347432332208373760, 297421244402368522]:
            return False
        data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
        data['name_second'] = name
        json.dump(data, io.open('config.json', 'w', encoding='utf-8-sig'), indent=2)
        await ctx.send(':ok_hand:')
    
    @commands.command(name='set_three')
    @commands.has_permissions(manage_guild=True)
    async def set_three(self, ctx, *, name: str):
        if ctx.author.id not in [347432332208373760, 297421244402368522]:
            return False
        data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
        data['name_three'] = name
        json.dump(data, io.open('config.json', 'w', encoding='utf-8-sig'), indent=2)
        await ctx.send(':ok_hand:')

    @commands.command(name='set_four')
    @commands.has_permissions(manage_guild=True)
    async def set_three(self, ctx, *, name: str):
        if ctx.author.id not in [347432332208373760, 297421244402368522]:
            return False
        data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
        data['name_three'] = name
        json.dump(data, io.open('config.json', 'w', encoding='utf-8-sig'), indent=2)
        await ctx.send(':ok_hand:')
    
    @commands.command(name='set_guild')
    @commands.has_permissions(manage_guild=True)
    async def set_guild(self, ctx, *, id: int):
        if ctx.author.id not in [347432332208373760, 297421244402368522]:
            return False
        data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
        data['guild_id'] = id
        json.dump(data, io.open('config.json', 'w', encoding='utf-8-sig'), indent=2)
        await ctx.send(':ok_hand:')
    
    @commands.command(name='set_sleeping')
    @commands.has_permissions(manage_guild=True)
    async def set_awaiting(self, ctx, *, time: int):
        if ctx.author.id not in [347432332208373760, 297421244402368522]:
            return False
        data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
        data['sleep'] = time
        json.dump(data, io.open('config.json', 'w', encoding='utf-8-sig'), indent=2)
        await ctx.send(':ok_hand:')

def setup(bot):
    bot.add_cog(Basic(bot))