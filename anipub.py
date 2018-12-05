# python3.6
# coding: utf-8

import asyncio
import io
import json
import os
import sys
from datetime import datetime

import discord
from discord.ext import commands

os.environ['TOKEN'] = 'NTE5ODUxMjA0NDQ1MDc3NTA0.DulU3w.s9IBLJOo8GKC3tfG5s7kqevT6Cs'
os.environ['PREFIX'] = 'anipub!'
os.environ['ACTIVITY'] = 'streaming'

token = os.environ['TOKEN']
modules = ['cogs.owner', 'cogs.basic']
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
        await self.change_presence(activity=discord.Game(name='ANIPUB'))

        async def name_change():
            while not self.is_closed():
                data = json.load(io.open('config.json', 'r', encoding='utf-8-sig'))
                server = discord.utils.get(self.guilds, id=data['guild_id'])
                awaiting = data['sleep']

                print('Цикл выполняется..')

                await server.edit(name=data['name_first'])
                print('1')
                await asyncio.sleep(awaiting)
                await server.edit(name=data['name_second'])
                print('2')
                await asyncio.sleep(awaiting)
                await server.edit(name=data['name_three'])
                print('3')

                await asyncio.sleep(awaiting)

        await self.loop.create_task(name_change())

    async def launch_session(self):
        self.owner = (await self.application_info()).owner

if __name__ == '__main__':
    AniPub(token, prefix, modules)
