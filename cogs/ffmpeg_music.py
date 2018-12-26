# python3.6
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import os
import traceback
import youtube_dl
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL

from random import randint

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so')

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.

        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'```ini\n[{data["title"]} добавлено в очередь.]\n```', delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author,
                        'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.

        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.

    This class implements a queue and loop, which allows for different guilds to
    listen to different playlists simultaneously.

    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next',
                 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'Произошла ошибка:\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source,
                        after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=source.title)
            embed.add_field(name='Запросил:', value='**%s**' % source.requester)
            self.np = await self._channel.send(embed=embed,
                                               delete_after=15)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music:
    """Команды проигрывателя музыки"""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                      title=f'**{ctx.author}**, извиняй, только на серверах...')
                return await ctx.send(embed=embed,
                                      delete_after=15)
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send(':x: Не удалось подключиться к голосовому каналу.\n'
                           ':notes: Проверьте, в доступном-ли для меня голосовом канале вы находитесь.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Подключить меня к голосовому каналу. *Просто подключить? А пати?*

        Аргументы:
        `:channel` - имя канала
        __                                            __
        Например:
        ```
        n!connect
        n!join music
        ```
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                # raise InvalidVoiceChannel(':notes: Вы не подключены к голосовому каналу.')
                embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                      title=f'**{ctx.author}**, вы не подключены к голосовому каналу.')
                return await ctx.send(embed=embed,
                                      delete_after=15)

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                # raise VoiceConnectionError(f':notes: Переход в канал <{channel}> не удался. Timeout.')
                embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                      title=f'**{ctx.author}**, мне не удалось перейти в <{channel}>.\n'
                                             'Превышено время ожидания.')
                return await ctx.send(embed=embed,
                                      delete_after=15)
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                # raise VoiceConnectionError(f':notes: Подключение к каналу <{channel}> не удалось. Timeout.')
                embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                      title=f'**{ctx.author}**, мне не удалось подключиться к <{channel}>.\n'
                                             'Превышено время ожидания.')
                return await ctx.send(embed=embed,
                                      delete_after=15)

        await ctx.send(f':notes: Голосовой канал: **{channel}**', delete_after=20)

    @commands.command(name='play')
    async def play_(self, ctx, *, search: str):
        """Запросить проигрывание музыки. *Тут слишком скучно, пора менять обстановку!*

        Аргументы:
        `:search` - название / ссылка YouTube
        __                                            __
        Например:
        ```
        n!play Nightcore - MayDay
        ```
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        try:
            source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop,
                                                    download=False)
        except youtube_dl.DownloadError:
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=f'**{ctx.author}**, мне не удалось воспроизвести полученный трек.')
            return await ctx.send(embed=embed,
                                delete_after=15)

        await player.queue.put(source)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Поставить проигрыватель на паузу. *Мне надо...отойти...*
        """
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)
        elif vc.is_paused():
            return

        vc.pause()
        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=f'**{ctx.author}** включил паузу.')
        return await ctx.send(embed=embed,
                              delete_after=15)

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Снять проигрыватель с паузы. *А? Кто-то отходил?*
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)
        elif not vc.is_paused():
            return

        vc.resume()
        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=f'**{ctx.author}** убрал паузу.')
        return await ctx.send(embed=embed,
                              delete_after=15)

    @commands.command(name='skip')
    async def skip_(self, ctx):
        """Перейти к следующему треку в очереди. *Мне надоела эта песня!*
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=f'**{ctx.author}** пропустил текущий трек.')
        return await ctx.send(embed=embed,
                              delete_after=15)

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        """Отобразить список песен в очереди. *А что дальше?...*
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: В очереди нет треков.')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'След. трек - {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)

    @commands.command(name='playing', aliases=['currentsong', 'current'])
    async def now_playing_(self, ctx):
        """Информация о проигрываемой песне. *Топ трек! Как называется?*
        """
        vc = ctx.voice_client

        player = self.get_player(ctx)

        if not vc or not vc.is_connected() or not player.current:
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=vc.source.title)
        embed.add_field(name='Запросил:', value='**%s**' % vc.source.requester)
        player.np = await ctx.send(embed=embed,
                                   delete_after=15)

    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Изменить громкость проигрывателя. *Нужно еще громче?? Пожалуйста!*

        Аргументы:
        `:vol` - процент громкости
        __                                            __
        Например:
        ```
        n!volume 50
        ```
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        if not 0 < vol < 101:
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Число от 1 до 100.\n')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=f'**{ctx.author}** установил громкость проигрывателя на **{vol}%**')
        return await ctx.send(embed=embed,
                              delete_after=15)

    @commands.command(name='stop')
    async def stop_(self, ctx):
        """Остановить проигрывание. Это так же очистит очередь песен.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                  title=':notes: Я ничего не проигрываю.')
            return await ctx.send(embed=embed,
                                  delete_after=15)

        await self.cleanup(ctx.guild)
        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                              title=':notes: Проигрыватель остановлен.')
        return await ctx.send(embed=embed,
                              delete_after=15)

    reactions = {'🔊': 'Запустить проигрыватель',
                 '⏹': 'Остановить проигрывание',
                 '⏸': 'Поставить проигрыватель на паузу',
                 '▶': 'Возобновить проигрывание',
                 '⏭': 'Перейти к следующей песне',
                 '🗂': 'Отобразить список песен в очереди',
                 '🔗': 'Подключить меня к каналу'}

    @commands.command(name='music', aliases=['muscontrol', 'menu'])
    async def call_menu_(self, ctx):
        embed = discord.Embed(title=':notes: Контроллер проигрывателя.')
        paginator = commands.Paginator(prefix='',suffix='')

        for x in self.reactions:
            paginator.add_line(f"{x}: {self.reactions[x]}")

        for page in paginator.pages:
            embed.add_field(name='Описание реакций', value=page)

        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f'{os.environ["PREFIX"]}{ctx.command}')

        m = await ctx.send(embed=embed)

        async def reaction_checker(ctx):
            for x in self.reactions:
                await m.add_reaction(x)

            def check(r, u):
                if not m \
                    or str(r) not in self.reactions \
                    or u.id == self.bot.user.id \
                    or r.message.id != m.id \
                    or u.bot:
                    return False
                return True

            while True:
                r, u = await self.bot.wait_for('reaction_add', check=check)
                if str(r) == '🔊':
                    def msg_chk(m):
                        return m.author.id == ctx.author.id

                    try:
                        await ctx.send('Введите название песни / ссылку на видео в YT...',
                                       delete_after=15)
                        msg = await self.bot.wait_for('message', check=msg_chk, timeout=15)
                        await ctx.send(':notes: Исполняю.')
                        await ctx.invoke(self.bot.get_command("play"), search=msg.content)

                    except asyncio.TimeoutError:
                        embed = discord.Embed(color=randint(0x000000, 0xFFFFFF),
                                              title=':notes: Отменено - время ожидания ответа вышло.')
                        return await ctx.send(embed=embed,
                                              delete_after=15)

                if str(r) == '⏹':
                    await ctx.invoke(self.stop_)
                if str(r) == '⏸':
                    await ctx.invoke(self.pause_)
                if str(r) == '▶':
                    await ctx.invoke(self.resume_)
                if str(r) == '⏭':
                    await ctx.invoke(self.skip_)
                if str(r) == '🗂':
                    await ctx.invoke(self.queue_info)
                if str(r) == '🔗':
                    await ctx.invoke(self.connect_)
                await m.remove_reaction(r, u)

        react_loop = self.bot.loop.create_task(reaction_checker(ctx))
        await asyncio.sleep(300)
        await m.delete()
        react_loop.cancel()


def setup(bot):
    bot.add_cog(Music(bot))