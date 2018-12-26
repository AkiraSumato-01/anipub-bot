import discord
from discord.ext import commands

class IsNSFW(commands.CheckFailure):
    pass

class NotOwner(commands.CheckFailure):
    pass

class Blacklisted(commands.CheckFailure):
    pass

class NotPremium(commands.CheckFailure):
    pass

class NotVoted(commands.CheckFailure):
    pass

class DisabledHere(commands.CheckFailure):
    pass



def nsfw():
    async def predicate(ctx):
        if type(ctx.channel) == discord.channel.DMChannel:
            raise IsNSFW()
        elif ctx.channel.is_nsfw():
            return True
        else:
            raise IsNSFW()

    return commands.check(predicate)



def owner():
    async def predicate(ctx):
        if ctx.author.id in ctx.bot.whitelist or ctx.author.id == ctx.bot.owner.id:
            return True
        else:
            raise NotOwner()

    return commands.check(predicate)



def premium():
    async def predicate(ctx):
        if ctx.author.id in ctx.bot.premium:
            return True
        else:
            raise NotPremium()

    return commands.check(predicate)



def is_voted():
    async def predicate(ctx):
        users = await ctx.bot.dblpy.get_upvote_info()
        if ctx.author.id in [int(x['id']) for x in users]:
            return True
        else:
            return NotVoted

    return commands.check(predicate)