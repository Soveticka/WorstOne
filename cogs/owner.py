import json

import git
from discord import errors
from discord.ext import commands
import main


class Owner(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def _load(self, ctx, cog: str):
        """ Command for loading module
        """
        try:
            if '.py' not in cog:
                self.bot.load_extension(f'cogs.{cog}')
            else:
                self.bot.load_extension(f'cogs.{cog[:-3]}')
        except (AttributeError, ImportError) as error:
            await ctx.message.add_reaction("❌")
            print(error)
        else:
            await ctx.message.add_reaction('✅')

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def _unload(self, ctx, cog: str):
        """ Command for unloading module
        """
        try:
            if '.py' not in cog:
                self.bot.unload_extension(f'cogs.{cog}')
            else:
                self.bot.unload_extension(f'cogs.{cog[:-3]}')
        except (AttributeError, ImportError) as error:
            await ctx.message.add_reaction("❌")
            print(error)
        else:
            await ctx.message.add_reaction('✅')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, cog: str):
        """ Reloads specified module
        """
        try:
            if '.py' not in cog:
                self.bot.unload_extension(f'cogs.{cog}')
                self.bot.load_extension(f'cogs.{cog}')
            else:
                self.bot.load_extension(f'cogs.{cog[:-3]}')
                self.bot.unload_extension(f'cogs.{cog[:-3]}')
        except (AttributeError, ImportError) as error:
            await ctx.message.add_reaction("❌")
            print(error)
        else:
            await ctx.message.add_reaction('✅')

    @commands.command(name='stop', hidden=True, aliases=['exit', 'close'])
    @commands.is_owner()
    async def _stop(self, ctx):
        """ "Safely" stops the bot
        """
        await ctx.send('*Turning Off, Cya*')
        await self.bot.logout()

    # TODO - Add git pull with optional cog loading
    #      - If cog is not specified, pull data and do nothing.
    @commands.command(name='pull', hidden=True)
    @commands.is_owner()
    async def _pull(self, ctx, cog: str = ''):
        """ Pulls github origin
            If cog is specified, reload the cog
        """
        try:
            g = git.cmd.Git('./')
            g.pull()
        except Exception as error:
            print(error)
            await ctx.message.add_reaction("❌")
            await ctx.message.add_reaction("🔥")
            return
        if cog != '':
            await self._reload(ctx, cog)

    @commands.command(name='globalmessage')
    @commands.is_owner()
    async def _globalmessage(self, ctx, message):
        for guild in self.bot.guilds:
            await guild.owner.send(message)

    @commands.command(name='rebuild')
    @commands.is_owner()
    async def _rebuild(self, ctx):
        with open('./json/guild/guilds.json', 'r') as fi:
            guilds = json.load(fi)

        with open("./json/user/users.json", "r") as f:
            users = json.load(f)

        for guild in self.bot.guilds:
            await main.updateGuild(guilds, guild)
            for member in guild.members:
                await main.updateUserData(users, member)

        with open("./json/user/users.json", "w") as f:
            json.dump(users, f, indent=4)

        with open("./json/guild/guilds.json", "w") as fi:
            json.dump(guilds, fi, indent=4)




def setup(client):
    client.add_cog(Owner(client))
