# python3.6
# -*- coding: utf-8 -*-

import asyncio
import io
import os
import platform
import sys
import textwrap
import traceback
from contextlib import redirect_stdout
from random import randint

import discord
import psutil
from discord.ext import commands

import humanize


class Owner(object):
    """Набор команд для отладки и тестирования."""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='logout', hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        """Деавторизовать от Discord.
        """

        def message_check(m):
            return m.author.id == ctx.author.id

        await ctx.send(':hammer_pick: Хорошо-хорошо! Но... Мне правда надо деавторизоваться?...')
        msg = await self.bot.wait_for('message', check=message_check, timeout=120.0)

        if msg.content.lower() in ['да', 'ага', 'угу', 'давай уже']:
            await ctx.send('<:offline:455810041015173121> Хорошо, я деавтиризуюсь...')
        else:
            return await ctx.send('<:online:455810041002459156> Остаюсь в сети...')

        await asyncio.sleep(1.2)
        await self.bot.logout()

    @commands.command(name='checkvoice', aliases=['cv'], hidden=True)
    @commands.is_owner()
    async def check_voice_clients(self, ctx, show: bool = False):
        """Проверить, проигрывается ли где-то музыка в моем исполнении.
        """
        active_voice_clients = [x.name for x in self.bot.guilds if x.voice_client]
        if show:
            await ctx.send(f'В данный момент я проигрываю музыку на {len(active_voice_clients)} серверах:\n{", ".join(active_voice_clients)}')
        else:
            await ctx.send('В данный момент я проигрываю музыку на %s серверах.' % len(active_voice_clients))

    @commands.command(name='sysinfo', hidden=True)
    @commands.is_owner()
    async def sysinfo(self, ctx):
        """Системная информация.
        """
        pid = os.getpid()
        py = psutil.Process(pid)

        embed = discord.Embed(timestamp=ctx.message.created_at,
                              color=randint(0x000000, 0xFFFFFF),
                              title='<:naomicmds:491314340029530132> Системная статистика')

        embed.add_field(name='<:naomicpu:493341839953494031> Процессор:',
                        value=f'▫ Кол-во ядер: {psutil.cpu_count()}\n'
                              f'▫ Загрузка: {round(psutil.cpu_percent())}%\n'
                              f'▫ Загрузка ботом: {round(py.cpu_percent())}%')
        embed.add_field(name='<:naomiram:493341277966958602> Оператива:',
                        value=f'▫ Объем: {humanize.naturalsize(psutil.virtual_memory().total)}\n'
                              f'▫ Загрузка: {round(psutil.virtual_memory().percent)}%\n'
                              f'▫ Загрузка ботом: {round(py.memory_percent())}%')
        embed.add_field(name='<:naomi_python_logo:516539675628797962> Текущий модуль:',
                        value='▫ ' + os.path.basename(__file__))
        embed.add_field(name='<:naomicmds:491314340029530132> Имя процесса:',
                        value='▫ ' + py.name())
        embed.add_field(name='🖥 Платформа:',
                        value='▫ ' + platform.platform())
        embed.add_field(name='<:naomiusers:491313467962294296> Пользователь:',
                        value='▫ ' + py.username())
        embed.add_field(name='<:naomi_dir:516541796646387712> Интерпретатор тут:',
                        value='▫ ' + sys.executable)
        embed.add_field(name=f'<:naomi_discord_logo:516264528745332736> Discord.py {discord.__version__}',
                        value=chr(173))
        embed.add_field(name=f'<:naomi_python_logo:516539675628797962> Python {platform.python_version()}',
                        value=chr(173))
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f'{os.environ["PREFIX"]}{ctx.command}')

        await ctx.send(embed=embed)

    @commands.command(name='quit', aliases=['quitserver'], hidden=True)
    @commands.is_owner()
    async def quit_guild(self, ctx, guild: discord.Guild):
        """Отключить меня от сервера.

        Аргументы:
        `:guild` - имя сервера
        __                                            __
        Например:
        ```
        n!quit MyLittleGroup
        ```
        """
        try:
            await guild.leave()

        except:
            ctx.send(f'Возникла ошибка:\n{traceback.format_exc()}')

    @commands.command(name='ping', hidden=True)
    @commands.is_owner()
    async def ping(self, ctx):
        """Измерение задержки API, клиента.
        """

        resp = await ctx.send('Тестируем...')
        diff = resp.created_at - ctx.message.created_at
        await resp.edit(content=f':ping_pong: Pong!\nЗадержка API: {1000 * diff.total_seconds():.1f}мс.\nЗадержка {self.bot.user.name}: {round(self.bot.latency * 1000)}мс')

    @commands.command(hidden=True, aliases=['r'])
    @commands.is_owner()
    async def restart(self, ctx):
        """Перезагрузка.
        """
        active_voice_clients = [x.name for x in self.bot.guilds if x.voice_client]
        
        # Чтобы не перезагрузить бота во время проигрывания музыки.
        # В конце концов, бот перестает проигрывать ее при перезагрузке.
        if len(active_voice_clients) >= 1:
            alert = await ctx.send('В данный момент я проигрываю музыку на %s серверах.\n"❌" для отмена.' % len(active_voice_clients))
            for x in ['✅', '❌']:
                await alert.add_reaction(x)
            try:
                def check(r, u):
                    if not alert \
                        or r.message.id != alert.id \
                        or u.bot:
                        return False
                    return True

                r, u = await self.bot.wait_for('reaction_add', check=check)
                if str(r) == '✅':
                    pass
                else:
                    await alert.edit(content=':x: Отменено господином.')
                    await asyncio.sleep(2)
                    return await alert.delete()

            except asyncio.TimeoutError:
                return await ctx.send(':x: Отменено - время ожидания ответа вышло.')
        
        else:
            alert = await ctx.send('Сорян, мне просто нужно подтверждение...')
            for x in ['✅', '❌']:
                await alert.add_reaction(x)
            try:
                def check(r, u):
                    if not alert \
                        or r.message.id != alert.id \
                        or u.bot:
                        return False
                    return True

                r, u = await self.bot.wait_for('reaction_add', check=check)
                if str(r) == '✅':
                    pass
                else:
                    await alert.edit(content=':x: Отменено господином.')
                    await asyncio.sleep(2)
                    return await alert.delete()

            except asyncio.TimeoutError:
                return await ctx.send(':x: Отменено - время ожидания ответа вышло.')

        await self.bot.change_presence(activity=discord.Game(name='перезагрузка...'), status=discord.Status.dnd)
        await ctx.send(embed=discord.Embed(color=0x13CFEB).set_footer(text="Перезагружаемся..."))
        os.execl(sys.executable, sys.executable, * sys.argv)

    @commands.command(name='#exception', hidden=True)
    @commands.is_owner()
    async def exception(self, ctx):
        """Выдать исключение.
        """

        raise RuntimeError('Вызвано разработчиком.')

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """Загрузить модуль.

        Аргументы:
        `:cog` - имя модуля (включая директорию)
        __                                            __
        Например:
        ```
        n!load cogs.member.utils
        ```
        """

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`Ошибка при загрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`Модуль {cog} успешно загружен`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Выгрузить модуль.

        Аргументы:
        `:cog` - имя модуля (включая директорию)
        __                                            __
        Например:
        ```
        n!unload cogs.admin
        ```
        """

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`Ошибка при выгрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`Модуль {cog} успешно выгружен`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Перезагрузка модуля.

        Аргументы:
        `:cogs` - имя модуля (включая директорию)
        __                                            __
        Например:
        ```
        n!reload cogs.member.fun
        ```
        """

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`Ошибка при перезагрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`Модуль {cog} успешно перезагружен`**')

    async def on_member_join(self, member):
        if member.guild.id == 457092470472179712:
            role = discord.utils.get(member.guild.roles, id=507249626789707777)
            channel = discord.utils.get(member.guild.channels, id=457588184302485514)

            await member.add_roles(role, reason='Просто так :з')
            await channel.send(f'<:naomi_arrow_up:506078581227651098> Новый участник {member.mention} присоединился.\n◽ **Добро пожаловать на {member.guild.name}!**')

    @commands.command(name='execute', aliases=['exec', 'eval', 'run'], hidden=True)
    @commands.is_owner()
    async def execute(self, ctx, *, code: str):
        """Интерпретатор Python кода.

        Аргументы:
        `:code` - код (Python 3)
        __                                            __
        Например:
        ```
        n!exec print('Hello World')
        ```
        """

        async def v_execution():
            async with ctx.channel.typing():
                env = {
                    'channel': ctx.channel,
                    'author': ctx.author,
                    'guild': ctx.guild,
                    'message': ctx.message,
                    'client': self.bot,
                    'bot': self.bot,
                    'discord': discord,
                    'ctx': ctx
                }

                env.update(globals())
                _code = ''.join(code).replace('```python', '').replace('```', '')

                try:
                    stdout = io.StringIO()
                    interpretate = f'async def virtexec():\n{textwrap.indent(_code, "  ")}'
                    exec(interpretate, env)
                    virtexec = env['virtexec']
                    with redirect_stdout(stdout):
                        function = await virtexec()

                except:
                    stdout = io.StringIO()
                    value = stdout.getvalue()

                    msg = discord.Embed(color=0xff0000, description=f"\n:inbox_tray: Входные данные:\n```python\n{''.join(code).replace('```python', '').replace('```', '')}\n```\n:outbox_tray: Выходные данные:\n```python\n{value}{traceback.format_exc()}```".replace(self.bot.http.token, 'тип.токен.окда'))
                    msg.set_author(name='Интерпретатор Python кода.')
                    msg.set_footer(text=f'Интерпретация не удалась - Python {platform.python_version()} | {platform.system()}')
                    return await ctx.send(f'{self.bot.owner.mention}, смотри сюда!', embed=msg)
                else:
                    value = stdout.getvalue()
                    if function is None:
                        if not value:
                            value = 'None'
                        success_msg = discord.Embed(color=0x00ff00, description=f":inbox_tray: Входные данные:\n```python\n{''.join(code).replace('```python', '').replace('```', '')}```\n\n:outbox_tray: Выходные данные:\n```python\n{value}```".replace(self.bot.http.token, 'тип.токен.окда'))
                        success_msg.set_author(name='Интерпретатор Python кода.')
                        success_msg.set_footer(text=f'Интерпретация успешно завершена - Python {platform.python_version()} | {platform.system()}')
                        return await ctx.send(f'{self.bot.owner.mention}, смотри сюда!', embed=success_msg)
                    else:
                        success_msg = discord.Embed(color=0x00ff00, description=f":inbox_tray: Входные данные:\n```python\n{''.join(code).replace('```python', '').replace('```', '')}```\n\n:outbox_tray: Выходные данные:\n```python\n{value}{function}```".replace(self.bot.http.token, 'тип.токен.окда'))
                        success_msg.set_author(name='Интерпретатор Python кода.')
                        success_msg.set_footer(text=f'Интерпретация успешно завершена - Python {platform.python_version()} | {platform.system()}')
                        return await ctx.send(f'{self.bot.owner.mention}, смотри сюда!', embed=success_msg)

        self.bot.loop.create_task(v_execution())

        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass

def setup(bot):
    bot.add_cog(Owner(bot))
