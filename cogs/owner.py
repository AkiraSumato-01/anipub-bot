# python3.6
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

import asyncio
import io
import os
import platform
import sys
import textwrap
import traceback
import humanize
import psutil
import json
from contextlib import redirect_stdout
from random import randint

from utils.HastebinPoster import *
from utils.ShellExecutor import *

from utils.Checks import *


class OwnerCommands(object):
    description_ru = "Набор команд для отладки и тестирования."
    description_en = "Commands for debugging & testing."

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='+update', hidden=True)
    @commands.is_owner()
    async def send_update(self, ctx, qreload: bool = True, *, message):
        """[RU] Оповестить участников нашего сервера об обновлении (и перезагрузить все модули)
        [EN] Notify our server members about the update (and reload all modules)
        """
        if qreload:
            self.bot.load()
            self.bot.load_config()

        c = discord.utils.get(discord.utils.get(self.bot.guilds, id=457092470472179712).text_channels, id=459609715693846528)
        await c.send(message)
        await ctx.message.add_reaction('✅')



    @commands.command(name='owncleanup', hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def owner_cleanup(self, ctx, member: discord.Member, count: int):
        """[RU] Удалить сообщения конкретного участника (разработчик)
        [EN] Delete messages from a specific member (for my developer)
        """

        if count > 100:
            await ctx.send(f'<:naomi_tick_no:525026037868789783> {count} > 100.')
        else:
            def is_member(m):
                return m.author.id == member.id
            await ctx.channel.purge(limit=count, check=is_member)


    
    @commands.command('block', hidden=True, aliases=['+blacklist', '+black'])
    @commands.is_owner()
    async def block_user(self, ctx, user: discord.Member):
        """[RU] Заблокировать юзера.
        [EN] Block user.
        """
        if user.id == self.bot.owner.id:
            return await ctx.send(f'{self.bot.no} Я не могу добавить Вас, '
                                  'мой великий разработчик, в свой черный список. Так нельзя!')
        elif user.id == self.bot.user.id:
            return await ctx.send(f'{self.bot.no} Не могу заблокировать себя же ._.')

        self.bot.blacklist.append(user.id)
        json.dump(self.bot.blacklist,
                  io.open('database/blacklist.json', 'w', encoding='utf-8-sig'))
        await ctx.send(f'{self.bot.yes} Успешно.')


    @commands.command('unblock', hidden=True, aliases=['-blacklist', '-block'])
    @commands.is_owner()
    async def unblock_user(self, ctx, user: discord.Member):
        """[RU] Разблокировать юзера
        [EN] Unblock user
        """
        try:
            self.bot.blacklist.remove(user.id)
            json.dump(self.bot.blacklist,
                      io.open('database/blacklist.json', 'w', encoding='utf-8-sig'))
            await ctx.send(f'{self.bot.yes} Успешно.')
        except:
            await ctx.send(f'{self.bot.no} Этот пользователь не находится в моем черном списке.')


    @commands.command('allow', hidden=True, aliases=['+whitelist', '+white'])
    @commands.is_owner()
    async def whitelist_user(self, ctx, user: discord.Member):
        """[RU] Добавить в белый список
        [EN] Add to whitelist
        """
        self.bot.whitelist.append(user.id)
        json.dump(self.bot.whitelist,
                  io.open('database/whitelist.json', 'w', encoding='utf-8-sig'))
        await ctx.send(f'{self.bot.yes} Успешно.')


    @commands.command('deny', hidden=True, aliases=['-whitelist', '-white'])
    @commands.is_owner()
    async def de_whitelist_user(self, ctx, user: discord.Member):
        """[RU] Убрать из белого списка
        [EN] Remove from a whitelist
        """
        try:
            self.bot.whitelist.remove(user.id)
            json.dump(self.bot.whitelist,
                      io.open('database/whitelist.json', 'w', encoding='utf-8-sig'))
            await ctx.send(f'{self.bot.yes} Успешно.')
        except:
            await ctx.send(f'{self.bot.no} Этот пользователь не находится в моем белом списке.')


    @commands.command('del-cog', hidden=True, aliases=['-cog'])
    @commands.is_owner()
    async def del_cog(self, ctx, path: str):
        """[RU] Удалить модуль
        [EN] Delete module
        """
        try:
            os.remove(path.replace('.', '/') + '.py')
            await ctx.send(f'<:naomi_tick_yes:525026013663723540> Успешно удален >> `{path}``')
        except Exception as e:
            await ctx.send(f'<:naomi_tick_no:525026037868789783> Не удалось >> `{path}``\n{type(e).__name__}: {e}')

    @commands.command('del-cmd', hidden=True, aliases=['-cmd'])
    @commands.is_owner()
    async def del_command(self, ctx, cmd: str):
        """[RU] Удалить команду
        [EN] Delete command
        """
        try:
            self.bot.remove_command(cmd)
            await ctx.send(f'<:naomi_tick_yes:525026013663723540> Успешно удален >> `{cmd}``')
        except Exception as e:
            await ctx.send(f'<:naomi_tick_no:525026037868789783> Не удалось >> `{cmd}``\n{type(e).__name__}: {e}')

    @commands.command(name='logout', hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        """[RU] Деавторизовать меня от Discord
        [EN] Logout me from Discord
        """
        def message_check(m):
            return m.author.id == ctx.author.id

        await ctx.send('Хорошо-хорошо! Но... Мне правда надо деавторизоваться?...')
        msg = await self.bot.wait_for('message', check=message_check, timeout=120.0)

        if msg.content.lower() in ['да', 'ага', 'угу', 'давай уже']:
            await ctx.send('<:offline:455810041015173121> Хорошо, я деавтиризуюсь...')
        else:
            return await ctx.send('<:online:455810041002459156> Остаюсь в сети...')

        await asyncio.sleep(1.2)
        await self.bot.logout()

    @commands.command(name='sysinfo', hidden=True)
    @commands.is_owner()
    async def sysinfo(self, ctx):
        """[RU] Системная информация
        [EN] System statistics
        """
        pid = os.getpid()
        py = psutil.Process(pid)

        embed = discord.Embed(timestamp=ctx.message.created_at,
                              color=randint(0x000000, 0xFFFFFF),
                              title='<:naomi_cmds:491314340029530132> Системная статистика')

        embed.add_field(name='<:naomi_cpu:493341839953494031> Процессор:',
                        value=f'▫ Кол-во ядер: {psutil.cpu_count()}\n'
                              f'▫ Загрузка: {round(psutil.cpu_percent())}%\n'
                              f'▫ Загрузка ботом: {round(py.cpu_percent())}%')
        embed.add_field(name='<:naomi_ram:493341277966958602> Оператива:',
                        value=f'▫ Объем: {humanize.naturalsize(psutil.virtual_memory().total)}\n'
                              f'▫ Загрузка: {round(psutil.virtual_memory().percent)}%\n'
                              f'▫ Загрузка ботом: {round(py.memory_percent())}%')
        embed.add_field(name='<:naomi_python_logo:516539675628797962> Текущий модуль:',
                        value='▫ ' + os.path.basename(__file__))
        embed.add_field(name='<:naomi_cmds:491314340029530132> Имя процесса:',
                        value='▫ ' + py.name())
        embed.add_field(name='🖥 Платформа:',
                        value='▫ ' + platform.platform())
        embed.add_field(name='<:naomi_users:491313467962294296> Пользователь:',
                        value='▫ ' + py.username())
        embed.add_field(name='<:naomi_dir:516541796646387712> Интерпретатор тут:',
                        value='▫ ' + sys.executable)
        embed.add_field(name=f'<:naomi_discord_logo:516264528745332736> Discord.py {discord.__version__}',
                        value=chr(173))
        embed.add_field(name=f'<:naomi_python_logo:516539675628797962> Python {platform.python_version()}',
                        value=chr(173))
        
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f'{ctx.command}')

        await ctx.send(embed=embed)

    @commands.command(name='quit', aliases=['quitserver'], hidden=True)
    @commands.is_owner()
    async def quit_guild(self, ctx, guild: discord.Guild):
        """[RU] Отключить меня от сервера
        [EN] Disconnect me from a server
        """
        try:
            await guild.leave()

        except:
            await ctx.send(f'Возникла ошибка:\n```{traceback.format_exc()}```')

    @commands.command(name='ping', hidden=True)
    @commands.is_owner()
    async def ping(self, ctx):
        """[RU] Client & API latency
        [EN] Задержка API и клиента
        """

        resp = await ctx.send('Тестируем...')
        diff = resp.created_at - ctx.message.created_at
        await resp.edit(content=f':ping_pong: Pong!\nЗадержка API: {1000 * diff.total_seconds():.1f}мс.\nЗадержка {self.bot.user.name}: {round(self.bot.latency * 1000)}мс')

    @commands.command(hidden=True, aliases=['r'])
    @commands.is_owner()
    async def restart(self, ctx):
        """[RU] Перезапуск
        [EN] Restart
        """
        await self.bot.change_presence(activity=discord.Game(name='перезагрузка...'), status=discord.Status.dnd)
        await ctx.send(embed=discord.Embed(color=0x13CFEB).set_footer(text="Перезагружаемся..."))
        os.execl(sys.executable, sys.executable, * sys.argv)

    @commands.command(name='#exception', hidden=True)
    @commands.is_owner()
    async def exception(self, ctx):
        """[RU] Выдать исключение
        [EN] Raise an exception
        """
        raise RuntimeError('Вызвано разработчиком.')

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """[RU] Загрузить модуль
        [EN] Load module
        """

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**<:naomi_tick_no:525026037868789783> `Ошибка при загрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
        else:
            await ctx.send(f'**<:naomi_tick_yes:525026013663723540> `Модуль {cog} успешно загружен`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """[RU] Выгрузить модуль
        [EN] Unload module
        """

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**<:naomi_tick_no:525026037868789783> `Ошибка при выгрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
        else:
            await ctx.send(f'**<:naomi_tick_yes:525026013663723540> `Модуль {cog} успешно выгружен`**')

    async def on_member_join(self, member):
        if member.guild.id == 457092470472179712:
            role = discord.utils.get(member.guild.roles, id=507249626789707777)
            channel = discord.utils.get(member.guild.channels, id=457588184302485514)

            await member.add_roles(role, reason='Просто так :з')
            await channel.send(f'<:naomi_arrow_up:506078581227651098> Новый участник {member.mention} присоединился.\n◽ **Добро пожаловать на {member.guild.name}!**')

    @commands.command(name='usage', aliases=['cmd-usage', 'cmdusage'], hidden=True)
    @commands.is_owner()
    async def usage(self, ctx, command_name: commands.clean_content = None):
        """[RU] Кол-во использований команд
        [EN] Commands usage coung
        """
        if not command_name:
            commands = "\n".join([f'# {x}: {self.bot.cmd_usage[x]}' for x in self.bot.cmd_usage])
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                description=f'```markdown\n{commands}```')

        else:
            command = self.bot.get_command(command_name)
            if not command:
                return await ctx.send('<:naomi_tick_no:525026037868789783> Я не нашла такой команды ._.')
            else:
                try:
                    count = self.bot.cmd_usage[command.name]
                except:
                    count = 0

                embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                    description=f'```markdown\n# {command_name} ({command}): {count}```')
        embed.set_author(name='Кол-во выполненных команд:', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='shell', aliases=['sh', 'bash'], hidden=True)
    @commands.is_owner()
    async def shell(self, ctx, *, code: str):
        """[RU] Терминал Bash (теперь асинхронный!)
        [EN] Bash terminal (now async!)
        """

        loading = discord.utils.get(discord.utils.get(self.bot.guilds,
                                    id=347635213670678528).emojis,
                                    id=525602942242390046)

        await ctx.message.add_reaction(loading)

        async with ctx.channel.typing():
            code_strings = code.replace('```python', '') \
                            .replace('```bash', '') \
                            .replace('```', '') \
                            .split('\n')
            output = []

            for string in code_strings:
                cmd = await self.bot.loop.run_in_executor(None, shell, string)
                if cmd == '':
                    cmd = 'ℹ | Нет выходных данных.'

                output.append(cmd)
            
            output = "\n".join(output)

            embed = discord.Embed(color=0x42A2EC,
                                  title=f'{self.bot.yes} Bash Терминал | Команда выполнена:',
                                   description=f"```bash\n{output}```")
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

            try:
                await ctx.send(f'{ctx.author.mention}, получен ответ!', embed=embed)
            except:
                try:
                    content = await post(output)
                except:
                    await ctx.send(f'Мне не удалось отправить ответ в чат... И на Hastebin тоже... Извиняюсь!')
                else:
                    await ctx.send(f'Мне не удалось отправить ответ в чат.\nОн здесь >> {content}')
            
            await ctx.message.remove_reaction(loading, self.bot.user)

    @commands.command(name='add-cog', hidden=True, aliases=['+cog'])
    @commands.is_owner()
    async def add_cog(self, ctx):
        """[RU] Добавить модуль
        [EN] Add module
        """
        if len(ctx.message.attachments) < 1:
            return await ctx.send('<:naomi_tick_no:525026037868789783> Вы не вложили к сообщению файл с кодом...')
        if len(ctx.message.attachments) > 1:
            return await ctx.send('<:naomi_tick_yes:525026013663723540> К сообщению вложено более одного файла... Ок, загружу все.')

        for ext in ctx.message.attachments:
            full_path = f'cogs/{ext.filename}'
            await ext.save(full_path)
            new_path = ''

            for x in full_path:
                if x != '.':
                    new_path += x
                else:
                    break
            try:
                self.bot.unload_extension(new_path.replace('/', '.'))
                self.bot.load_extension(new_path.replace('/', '.'))
            except:
                await ctx.send(f'<:naomi_tick_no:525026037868789783> Модуль `{new_path.replace("/", ".")}` не удалось загрузить. Удаляю с хоста...\n```python\n{traceback.format_exc()}```', delete_after=15)
                os.remove(full_path)
            else:
                await ctx.send(f'<:naomi_tick_yes:525026013663723540> Успешно загружен >> `{new_path.replace("/", ".")}``', delete_after=10)
            await ctx.message.delete()

    @commands.command(name='execute', aliases=['exec', 'eval', 'run'], hidden=True)
    @commands.is_owner()
    async def execute(self, ctx, *, code: str):
        """[RU] Интерпретатор Python
        [EN] Python interpreter
        """

        loading = discord.utils.get(discord.utils.get(self.bot.guilds,
                                    id=347635213670678528).emojis,
                                    id=525602942242390046)

        await ctx.message.add_reaction(loading)

        async def v_execution():
            async with ctx.channel.typing():
                env = {
                    'channel': ctx.channel,
                    'author': ctx.author,
                    'guild': ctx.guild,
                    'message': ctx.message,
                    'client': self.bot,
                    'bot': self.bot,
                    'Naomi': self.bot,
                    'naomi': self.bot,
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

                    try:
                        msg = discord.Embed(color=0xff0000,
                                            title='<:naomi_tick_no:525026037868789783> Интерпретатор Python:',
                                            description=f"```python\n{value}{traceback.format_exc()}```".replace(self.bot.http.token, '••••••••••'))
                        msg.set_footer(text=f'Интерпретация не удалась - Python {platform.python_version()} | {platform.system()}')
                        await ctx.message.remove_reaction(loading, self.bot.user)
                        return await ctx.send(f'{ctx.author.mention}, что-то пошло не так...', embed=msg)
                    except:
                        try:
                            content = await post(f'{value}{traceback.format_exc()}')
                        except:
                            await ctx.message.remove_reaction(loading, self.bot.user)
                            return await ctx.send(f'Мне не удалось отправить ответ в чат... И на Hastebin тоже... Извиняюсь!')
                        await ctx.message.remove_reaction(loading, self.bot.user)
                        return await ctx.send('<:naomi_tick_no:525026037868789783> Произошла ошибка, но ее код составляет более 2048 символов.\n'
                                              f'Я отправила код ошибки сюда -> <{content}>')
                else:
                    value = stdout.getvalue()
                    if not function:
                        if not value:
                            value = 'ℹ | Нет выходных данных.'
                        try:
                            success_msg = discord.Embed(color=0x00ff00,
                                                        title='<:naomi_tick_yes:525026013663723540> Интерпретатор Python:',
                                                        description=f"```python\n{value}```".replace(self.bot.http.token, '••••••••••'))
                            success_msg.set_footer(text=f'Интерпретация успешно завершена - Python {platform.python_version()} | {platform.system()}')
                            await ctx.message.remove_reaction(loading, self.bot.user)
                            return await ctx.send(f'{ctx.author.mention}, все готово!', embed=success_msg)
                        except:
                            try:
                                content = await post(value)
                            except:
                                await ctx.message.remove_reaction(loading, self.bot.user)
                                return await ctx.send(f'Мне не удалось отправить ответ в чат... И на Hastebin тоже... Извиняюсь!')
                            await ctx.message.remove_reaction(loading, self.bot.user)
                            return await ctx.send('<:naomi_tick_yes:525026013663723540> Все выполнено, но у меня не получается отправить результат сюда...\n'
                                                  f'Я оставила результат здесь >> <{content}>')
                    else:
                        try:
                            success_msg = discord.Embed(color=0x00ff00,
                                                        title='<:naomi_tick_yes:525026013663723540> Интерпретатор Python:',
                                                        description=f"```python\n{value}{function}```".replace(self.bot.http.token, '••••••••••'))
                            success_msg.set_footer(text=f'Интерпретация успешно завершена - Python {platform.python_version()} | {platform.system()}')
                            await ctx.message.remove_reaction(loading, self.bot.user)
                            return await ctx.send(f'{ctx.author.mention}, вот! Я все выполнила c:', embed=success_msg)
                        except:
                            try:
                                content = await post(f'{value}{function}')
                            except:
                                await ctx.message.remove_reaction(loading, self.bot.user)
                                return await ctx.send(f'Мне не удалось отправить ответ в чат... И на Hastebin тоже... Извиняюсь!')
                            await ctx.message.remove_reaction(loading, self.bot.user)
                            return await ctx.send('<:naomi_tick_yes:525026013663723540> Интерпретация прошла успешно, но, я не могу отправить результат в чат...\n'
                                                  f'Он тут >> <{content}>')

        self.bot.loop.create_task(v_execution())

def setup(bot):
    bot.add_cog(OwnerCommands(bot))
