# python3.6
# -*- coding: utf-8 -*-

import os
import discord
import requests
import asyncio
import io
from discord.ext import commands
from PIL import Image, ImageFilter
from utils.MemeGenerator import make_meme
from random import randint, choice

class Imaging(object):
    description_ru = "Редактор изображений."
    description_en = "Image editor."

    def __init__(self, bot):
        self.bot = bot
    
    async def get_avatar(self, member: discord.Member) -> bytes:
        async with self.bot.session.get(member.avatar_url_as(format="png")) as response:
            return await response.read()
        
    async def get_image(self, ctx, member: discord.Member, name: str):
        if not member:
            try:
                attachment = ctx.message.attachments[0]
                if attachment.filename.lower().endswith('png') or attachment.filename.lower().endswith('jpg') or attachment.filename.lower().endswith('jpeg'):
                    await attachment.save(f'{name}_{ctx.author.id}.png')
                else:
                    await ctx.send(':x: Не могу работать с этим типом файла.')
                    return None
            except:
                member = ctx.author
                data = await self.get_avatar(member)
                stream = io.BytesIO(data)
                im = Image.open(stream)
            else:
                im = Image.open(f'{name}_{ctx.author.id}.png')
        else:
            data = await self.get_avatar(member)
            stream = io.BytesIO(data)
            im = Image.open(stream)

        return im

    @commands.command(name='memegen')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def memegen(self, ctx, *, text: commands.clean_content):
        """[RU] Соорудить собственный мем
        [EN] Build your own meme"""

        string_list = text.split('%')

        templates = [f'templates/{x}' for x in os.listdir('templates/')]

        try:
            attachment = ctx.message.attachments[0]
            if attachment.filename.lower().endswith('png') or attachment.filename.lower().endswith('jpg') or attachment.filename.lower().endswith('jpeg'):
                await attachment.save(f'meme_{ctx.author.id}.png')
            else:
                await ctx.send(':x: Не могу работать с этим типом файла.')
                return False
        except:
            fn = choice(templates)
        else:
            fn = f'meme_{ctx.author.id}.png'

        if len(string_list) == 1:
            make_meme(bottomString=string_list[0],
                    topString='',
                    outputFilename='meme_' + str(ctx.author.id),
                    filename=fn)

        elif len(string_list) >= 2:
            make_meme(topString=string_list[0],
                    bottomString=string_list[1],
                    outputFilename='meme_' + str(ctx.author.id),
                    filename=fn)

        await ctx.send(file=discord.File(fp=f'meme_{ctx.author.id}.png'))
        await asyncio.sleep(1.5)
        os.remove(f'meme_{ctx.author.id}.png')
    
    @commands.command(name='filter-list', aliases=['filters'])
    async def filters(self, ctx):
        """[RU] Доступные фильтры
        [EN] Available filters"""

        await ctx.send('contour, blur, detail, edge_enhance, edge_enhance_more, emboss, find_edges, '
                       'sharpen, smooth, smooth_more, gray')
    
    @commands.command(name='filter')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def filter_blur(self, ctx, filters: str, member: discord.Member = None):
        """[RU] Применить фильтры к изображению
        [EN] Apply filters to image"""

        filters = filters.split(';')

        available = {
            'contour': ImageFilter.CONTOUR,
            'blur': ImageFilter.BLUR,
            'detail': ImageFilter.DETAIL,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'edge_enhance_more': ImageFilter.EDGE_ENHANCE_MORE,
            'emboss': ImageFilter.EMBOSS,
            'find_edges': ImageFilter.FIND_EDGES,
            'sharpen': ImageFilter.SHARPEN,
            'smooth': ImageFilter.SMOOTH,
            'smooth_more': ImageFilter.SMOOTH_MORE
        }

        im = await self.get_image(ctx, member, 'filter')
        if not im:
            return False

        not_success = []

        for x in filters:
            try:
                if x in ['fliprl', 'fliplr']:
                    im = im.transpose(Image.FLIP_LEFT_RIGHT)
                elif x in ['flipdu', 'flipud']:
                    im = im.transpose(Image.FLIP_TOP_BOTTOM)
                elif x == 'gray':
                    im = im.convert('L')
                else:
                    filter_ = available[x]
                    im = im.filter(filter_)
            except:
                not_success.append(x)
        im.save(f'filter_{ctx.author.id}.png')

        if len(not_success) > 0:
            await ctx.send(f'Не удалось применить {len(not_success)} фильтров:\n{", ".join(not_success)}',
                           file=discord.File(fp=f'filter_{ctx.author.id}.png'))
        else:
            await ctx.send(file=discord.File(fp=f'filter_{ctx.author.id}.png'))

        asyncio.sleep(1.5)
        os.remove(f'filter_{ctx.author.id}.png')
    

    @commands.command(name='trigger', aliases=['tr', 'triggered'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def triggered(self, ctx, member: discord.Member = None):
        """[RU] TRIGGERED
        [EN] TRIGGERED"""

        im = await self.get_image(ctx, member, 'trigger')
        if not im:
            return False
        im = im.resize((1024, 1024), Image.ANTIALIAS)

        triggered = Image.open('triggered.png')
        rd = Image.new('RGBA', (1024, 1024), (255, 0, 0))

        try:
            im = Image.blend(im, rd, 0.3)
        except Exception as e:
            pass

        im.paste(triggered, (0, 886))

        im.save(f'trigger_{ctx.author.id}.png', 'PNG')
        await ctx.send(file=discord.File(fp=f'trigger_{ctx.author.id}.png'))
        os.remove(f'trigger_{ctx.author.id}.png')
    
    @commands.command(name='resize')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def resize(self, ctx, size: str, member: discord.Member = None):
        """[RU] Изменить размер изображения
        [EN] Resize image"""

        im = await self.get_image(ctx, member, 'filter')
        if not im:
            return False

        size = size.lower().split('x')
        
        if len(size) != 2:
            return await ctx.send(f':x: Неверно указан новый размер ({"x".join(size)})')
        
        for x in size:
            if not x.isnumeric:
                return await ctx.send(f':x: Неверно указан новый размер ({"x".join(size)})')
            if int(x) > 2500:
                return await ctx.send(f':x: Указанный размер слишком большой ({x} > 2500)')

        X = int(size[0])
        Y = int(size[1])
        
        im = im.resize((X, Y))
        im.save(f'resize_{ctx.author.id}.png', 'PNG')
        await ctx.send(file=discord.File(fp=f'resize_{ctx.author.id}.png'))
        os.remove(f'resize_{ctx.author.id}.png')


def setup(bot):
    bot.add_cog(Imaging(bot))