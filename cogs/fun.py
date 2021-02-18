import json

import discord
from discord.ext import commands
import main

import asyncpraw
import random

from variables import variables

reddit = asyncpraw.Reddit(client_id="p18AlHfMXRP79Q", client_secret="HwzFCkqKIOhK2nG1lONZ6y3qFQ7tKw",
                          user_agent="desktop:python.DiscordBot:v0.0.1 (by u/soveticka)")

normal = variables.normal
hentai = variables.hentai
everything = normal + hentai


def increaseUsed(query):
    with open("./variables/commandUsage.json", "r") as f:
        used = json.load(f)

    used[query] += 1

    with open("./variables/commandUsage.json", "w") as f:
        json.dump(used, f, indent=4)


async def sendSubmission(ctx, subreddit, title):
    submission = await subreddit.random()

    increaseUsed(title)
    try:
        if ".png" in submission.url or ".gif" in submission.url or ".jpg" in submission.url or ".gifv" in submission.url:
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"/r/{title}"
            )
            embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.message.author.avatar_url)
            embed.set_image(url=submission.url)
            permalink = "https://reddit.com" + submission.permalink
            embed.set_author(name="Clickable link", url=permalink)

            if ".gifv" in submission.url:
                await ctx.send(f"/r/{title}\n{submission.url}")
            else:
                await ctx.send(embed=embed)
        else:
            if "youtube" in submission.url:
                await sendSubmission(ctx, subreddit, title)
            else:
                await ctx.send(f"/r/{title}\n{submission.url}")
    except AttributeError:
        print(AttributeError)
        await sendSubmission(ctx, subreddit, title)


class Fun(commands.Cog):
    def __init__(self, client):
        self.bot = client

    # @commands.group(description="Send NSFW image from Reddit")
    # async def nsfw(self, ctx, query="list", mode=""):
    #     channel = ctx.channel
    #     normal = variables.normal
    #     hentai = variables.hentai
    #     everything = normal + hentai
    #
    #     if channel.nsfw:
    #         if query == "list":
    #             await ctx.message.delete()
    #             await main._nsfw(ctx)
    #             return
    #         elif query == "random" or query in normal or query in hentai:
    #             if query in normal:
    #                 subreddit = await reddit.subreddit(query)
    #                 title = query
    #             elif query in hentai:
    #                 subreddit = await reddit.subreddit(query)
    #                 title = query
    #
    #             elif query == "random":
    #                 if mode == "real":
    #                     rnd = random.randrange(0, len(normal))
    #                     subreddit = await reddit.subreddit(normal[rnd])
    #                     title = normal[rnd]
    #
    #                 elif mode == "hentai":
    #                     rnd = random.randrange(0, len(hentai))
    #                     subreddit = await reddit.subreddit(hentai[rnd])
    #                     title = hentai[rnd]
    #
    #                 elif mode == "all":
    #                     rnd = random.randrange(0, len(everything))
    #                     subreddit = await reddit.subreddit(everything[rnd])
    #                     title = everything[rnd]
    #                 elif mode == "":
    #                     rnd = random.randrange(0, len(everything))
    #                     subreddit = await reddit.subreddit(everything[rnd])
    #                     title = everything[rnd]
    #                 else:
    #                     await ctx.message.delete()
    #                     await main._nsfw(ctx)
    #                     return
    #             try:
    #                 submission = await subreddit.random()
    #             except Exception:
    #                 print("error")
    #
    #             increseUsed(query)
    #             try:
    #                 if ".png" in submission.url or ".gif" in submission.url or ".jpg" in submission.url or ".gifv" in submission.url:
    #                     embed = discord.Embed(
    #                         colour=discord.Colour.random(),
    #                         title=f"/r/{title}"
    #                     )
    #                     embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.message.author.avatar_url)
    #                     embed.set_image(url=submission.url)
    #                     permalink = "https://reddit.com" + submission.permalink
    #                     embed.set_author(name="Clickable link", url=permalink)
    #
    #                     if ".gifv" in submission.url:
    #                         await ctx.send(f"/r/{title}\n{submission.url}")
    #                     else:
    #                         await ctx.send(embed=embed)
    #                 else:
    #                     if "youtube" in submission.url:
    #                         await self.nsfw(ctx, query, mode)
    #                     else:
    #                         await ctx.send(f"/r/{title}\n{submission.url}")
    #
    #             except AttributeError:
    #                 print(f"In submission were not all needed information")
    #                 await self.nsfw(ctx, query, mode)
    #         else:
    #             await ctx.message.delete()
    #
    #             return
    #     else:
    #         await ctx.send("Příkaz pošli do nsfw kanálu :)")
    #     try:
    #         await ctx.message.delete()
    #     except:
    #         print("No message to delete")

    @commands.group(invoke_without_command=True)
    async def nsfw(self, ctx, query="", mode=""):
        if ctx.invoked_subcommand is None:

            if ctx.channel.nsfw:
                if query in everything:
                    await sendSubmission(ctx, await reddit.subreddit(query), query)
                elif query == "":
                    await self._nsfw_list(ctx)
                else:
                    await ctx.message.delete()
                    await main._nsfw(ctx)
                    return
            else:
                await ctx.send(f"\u274C{ctx.author.mention} - {ctx.message.content} can be called only in nsfw channel!")

    @nsfw.command(name="random")
    async def _nsfw_random(self, ctx, query=""):
        if ctx.channel.nsfw:
            if query == "real":
                title = random.choice(normal)
            elif query == "hentai":
                title = random.choice(hentai)
            elif query == "" or query == "all":
                title = random.choice(everything)
            else:
                await ctx.message.delete()
                await main._nsfw(ctx)
                return

            await sendSubmission(ctx, await reddit.subreddit(title), title)
        else:
            await ctx.send(f"\u274C{ctx.author.mention} - {ctx.message.content} can be called only in nsfw channel!")

    @nsfw.command(name="list")
    async def _nsfw_list(self, ctx):
        if ctx.channel.nsfw:
            await ctx.message.delete()
            await main._nsfw(ctx)
        else:
            await ctx.send(f"\u274C{ctx.author.mention} - {ctx.message.content} can be called only in nsfw channel!")


def setup(client):
    client.add_cog(Fun(client))
