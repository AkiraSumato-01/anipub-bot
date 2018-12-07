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

os.environ['TOKEN'] = 'NTE5ODUxMjA0NDQ1MDc3NTA0.DulU3w.s9IBLJOo8GKC3tfG5s7kqevT6Cs'
os.environ['PREFIX'] = 'anipub!'
os.environ['ACTIVITY'] = 'streaming'

token = os.environ['TOKEN']
modules = ['cogs.owner', 'cogs.basic', 'cogs.imaging']
prefix = commands.when_mentioned_or(os.environ['PREFIX'])

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
        await self.change_presence(activity=discord.Streaming(name='ANIPUB!', url='https://www.twitch.tv/%none%'))

    async def launch_session(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.owner = (await self.application_info()).owner

if __name__ == '__main__':
    AniPub(token, prefix, modules)
