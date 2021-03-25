import json

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.command(name='kick', hidden=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def _kick(self, ctx, *members: discord.Member, reason: str = ''):
        """ Kicks specified member(s)
            Needs to be mentioned
        """
        kickLog = f'```Reason of kick: {reason}\nMembers:\n'
        for member in members:
            await ctx.message.guild.kick(member)
            kickLog += f'{member}\n'
        kickLog += '```'
        await ctx.send(kickLog)

    @commands.command(name='ban', hidden=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def _ban(self, ctx, *members: discord.Member, reason: str = ''):
        """ Bans specified member(s)
            Needs to be mentioned
        """
        banLog = f'```Reason of ban: {reason}\nMembers:\n'
        for member in members:
            await ctx.message.guild.ban(member)
            banLog += f'{member}\n'
        banLog += '```'
        await ctx.send(banLog)

    @commands.command(name='unban', hidden=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def _unban(self, ctx, user: str):
        """ Unbans member"""
        bans = await ctx.message.guild.bans()
        member = discord.utils.get(bans, user__name=user)
        if member:
            await ctx.message.guild.unbab(member.user)
            await ctx.send(f'Member {member.user.name}#{member.user.discriminator} was unbanned!')
            return
        await ctx.send(f'Member {user} is not currently banned')

    @commands.command(name='clear', hidden=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def clear(self, ctx, amount=5):
        """ Deletes x messages
            Default amount is 5
        """
        await ctx.channel.purge(limit=amount + 1)

    @commands.command(name='prefix', hidden=True, aliases=['changeprefix', 'prefixchange'])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def changeprefix(self, ctx, p):
        await ctx.message.delete()
        if ctx.author == ctx.guild.owner:
            with open("json/guild/guilds.json", "r") as f:
                guilds = json.load(f)

            if len(p) != 1:
                p = p + " "
            guilds[f'{ctx.guild.id}']['settings']['prefix'] = p

            with open("json/guild/guilds.json", "w") as f:
                json.dump(guilds, f, indent=4)

            await ctx.send(f"{ctx.author.mention} Prefix changed to {p}")


def setup(client):
    client.add_cog(Admin(client))
