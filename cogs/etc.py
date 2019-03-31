# usr/bin/python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord

class Etc(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('chkgm', aliases=['checkgame'])
    @commands.has_permission(manage_roles=True)
    async def chkgm(self, ctx):
        """Тупо проверка участников на игру в статусе"""
        r = bot.get_role(428649381659541507)

        i = 0

        for x in ctx.guild.members:
            if x.activity is not None:
                if x.activity.name == 'Spotify':
                    continue
                else:
                    try:
                        await x.add_roles(r)
                    except:
                        pass
                    else:
                        i += 1

        await ctx.send(f':white_check_mark: Роль добавлена {i} участникам.')


def setup(bot):
    bot.add_cog(Etc(bot))
