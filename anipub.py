# python3.6
# coding: utf-8

import asyncio
import io
import json
import os
import sys
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

token = os.environ['TOKEN']
modules = ['cogs.owner', 'cogs.basic', 'cogs.imaging', 'cogs.ffmpeg_music', 'cogs.etc']

prefix = commands.when_mentioned_or('r!')

class AniPub(commands.Bot):
    def __init__(self, token, prefix, modules):
        commands.Bot.__init__(self, command_prefix=prefix)
        self.modules = modules
        self.load()
        self.run(token, bot=True, reconnect=True)

    def load(self):
        self.remove_command('help')
        for module in self.modules:
            try:
                self.load_extension(module)
            except Exception as e:
                print(f'<!> Не удалось загрузить модуль {module}.\n{type(e).__name__}: {e}', file=sys.stderr)
            else:
                print(f'<!> Модуль {module} успешно загружен.')

    async def on_ready(self):
        print(f'<?> Подключение к {self.user} успешно.')
        await self.launch_session()
        await self.change_presence(activity=discord.Streaming(name='r!help', url='https://www.twitch.tv/%none%'))

    async def launch_session(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.owner = (await self.application_info()).owner

if __name__ == '__main__':
    AniPub(token, prefix, modules)
