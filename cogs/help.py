import asyncio

import discord
from discord.ext import commands
from main import get_prefix
from variables import variables


class Help(commands.cog):
    def __init__(self, client):
        self.bot = client

    # @bot.command(pass_context=True)
    @commands.group(name='help')
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            channel = ctx.message.channel

            embed = discord.Embed(
                colour=discord.Colour.purple(),
                description="Help is currently WIP"
            )

            embed.set_author(name='Commands and Stuff')
            for command in self.bot.commands:
                if command.name != self.bot:
                    if command.description == "":
                        desc = "WIP"
                    else:
                        desc = command.description
                    embed.add_field(name='{}{}'.format(get_prefix(self.bot, ctx.message), command.name), value=desc,
                                    inline=True)

            await channel.send(embed=embed)

    @help.command(name='nsfw')
    async def _nsfw(self, ctx):
        normal = variables.normal
        hentai = variables.hentai

        prefix = get_prefix(self.bot, ctx.message)
        embed = discord.Embed(
            colour=discord.Colour.purple(),
            title="NSFW"
        )

        normalString = ""
        for i in range(len(normal)):
            if i == len(normal) - 1:
                normalString += f"`{normal[i]}`"
            else:
                normalString += f"`{normal[i]}`, "
        embed.add_field(name='Real Women', value=normalString, inline=False)

        hentaiString = ""
        for i in range(len(hentai)):
            if i == len(hentai) - 1:
                hentaiString += f"`{hentai[i]}`"
            else:
                hentaiString += f"`{hentai[i]}`, "
        embed.add_field(name='Hentai', value=hentaiString, inline=False)

        randomString = "`real`, `hentai`, `all`"
        embed.add_field(name='Random Modes', value=randomString, inline=False)

        examples = f"{prefix}nsfw list\n" \
                   f"{prefix}nsfw boobs\n" \
                   f"{prefix}nsfw random hentai"
        embed.add_field(name='Examples', value=examples, inline=False)

        howtouse = "```html\n" \
                   "<list>\n" \
                   "<subreddit>\n" \
                   "<random> <mode>" \
                   "```"
        embed.add_field(name="Command's signature", value=howtouse, inline=False)

        message = await ctx.message.channel.send(embed=embed)
        await message.add_reaction(u"\u274C")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == u"\u274C"

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
        except asyncio.TimeoutError:
            await message.delete()
        else:
            await message.delete()

    @help.command(name='inventory', aliases=['i', 'inv'])
    async def _inventory(self, ctx):
        prefix = get_prefix(self.bot, ctx.message)
        embed = discord.Embed(
            colour=discord.Colour.from_rgb(r=0, g=0, b=0),
            title="Inventory".upper()
        )

        embed.add_field(name='Description', value='Shows your inventory', inline=False)
        embed.add_field(name='Documentation', value='None', inline=False)

        examples = f'{prefix}inventory\n'

        embed.add_field(name='Examples', value=examples, inline=False)

        howtouse = '```html\n' \
                   '<@Any>\n' \
                   '```'
        embed.add_field(name="Command's signature", value=howtouse, inline=False)

        embed.add_field(name='Category', value='Game'.upper(), inline=True)

        command = self.bot.get_command("inventory")
        aliases = command.aliases
        separator = ', '

        embed.add_field(name='Aliases', value=f'{separator.join(aliases)}', inline=True)

        message = await ctx.message.channel.send(embed=embed)
        await message.add_reaction(u"\u274C")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == u"\u274C"

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
        except asyncio.TimeoutError:
            await message.delete()
        else:
            await message.delete()


def start(client):
    client.remove_command('help')
    client.add_cog(Help(client))
