import asyncio
from random import randint

import os
import discord
from discord.ext import commands


async def HelpSetup(ctx, bot, command):
    if command is None:
        embed = discord.Embed(timestamp=ctx.message.created_at,
                        color=randint(0x000000, 0xFFFFFF),
                        title='Справочник по командам')
        __slots__ = []

        for cog in bot.cogs:
            __slots__.append(bot.get_cog(cog))

        for cog in __slots__:
            cog_commands = len([x for x in bot.commands if x.cog_name == cog.__class__.__name__ and not x.hidden])
            if cog_commands == 0:
                pass
            else:
                embed.add_field(name=cog.__class__.__name__,
                                value=', '.join([f'`{x}`' for x in bot.commands if x.cog_name == cog.__class__.__name__ and not x.hidden]),
                                inline=False)

    else:
        entity = bot.get_cog(command) or bot.get_command(command)

        if entity is None:
            clean = command.replace('@', '@\u200b')
            embed = discord.Embed(timestamp=ctx.message.created_at,
                            color=randint(0x000000, 0xFFFFFF),
                            title='Справочник по командам',
                            description=f'Команда или категория "{clean}" не найдена.')

        elif isinstance(entity, commands.Command):
            embed = discord.Embed(timestamp=ctx.message.created_at,
                            color=randint(0x000000, 0xFFFFFF),
                            title='Справочник по командам')
            embed.add_field(name=f'{os.environ["PREFIX"]}{entity.signature}',
                            value=entity.help,
                            inline=False)

        else:
            embed = discord.Embed(timestamp=ctx.message.created_at,
                            color=randint(0x000000, 0xFFFFFF),
                            title='Справочник по командам')
            embed.add_field(name=entity.__class__.__name__,
                            value=', '.join([f'`{x}`' for x in bot.commands if x.cog_name == entity.__class__.__name__ and not x.hidden]) or chr(173),
                            inline=False)

    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f'{os.environ["PREFIX"]}help [команда/категория] для получения доп.информации.')

    return embed
