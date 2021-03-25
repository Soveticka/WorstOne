import asyncio
import json
import urllib

import discord
from discord.ext import commands
from discord.ext.commands import errors
import main
from os import remove

import asyncpraw
import random
import requests

from variables import variables

reddit = asyncpraw.Reddit(client_id="p18AlHfMXRP79Q", client_secret="HwzFCkqKIOhK2nG1lONZ6y3qFQ7tKw",
                          user_agent="desktop:python.DiscordBot:v0.0.1 (by u/soveticka)")

normal = variables.normal
hentai = variables.hentai
everything = normal + hentai


def increaseUsed(query, title=""):
    with open("./variables/commandUsage.json", "r") as f:
        used = json.load(f)

    if query in used:
        if title == "":
            used[query] += 1
        else:
            if title in used[query]:
                used[query][title] += 1
            else:
                used[query][title] = 1
    else:
        used[query] = 1

    with open("./variables/commandUsage.json", "w") as f:
        json.dump(used, f, indent=4)


async def sendSubmission(ctx, subreddit, title):
    try:
        submission = await subreddit.random()
    except AttributeError:
        return await sendSubmission(ctx, subreddit, title)
    try:
        if "i.imgur.com" in submission.url and (".jpg" in submission.url or ".png" in submission.url):
            await ctx.send(f"/r/{title}")
            r = requests.get(submission.url, allow_redirects=True)
            name = submission.url.split('/')
            path = "./tempFiles/" + name[3]
            open(path, "wb").write(r.content)

            with open(path, "rb") as f:
                picture = discord.File(f)
                await ctx.send(file=picture)
            remove(path)

        elif ".png" in submission.url or ".gif" in submission.url or ".jpg" in submission.url or ".gifv" in submission.url:
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"/r/{title}"
            )
            embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.message.author.avatar_url)
            embed.set_image(url=submission.url)
            permalink = "https://reddit.com" + submission.permalink
            embed.set_author(name="Clickable link", url=permalink)

            if ".gifv" in submission.url:
                await ctx.send(f"/r/{title}\r"
                               f"{submission.url}")
            else:
                await ctx.send(embed=embed)
        else:
            if "redgifs" in submission.url:
                await ctx.send(f"/r/{title}\r"
                               f"{submission.url}")
            else:
                return await sendSubmission(ctx, subreddit, title)
    except AttributeError:
        return await sendSubmission(ctx, subreddit, title)
    try:
        await ctx.message.delete()
    except commands.errors.MessageNotFound:
        return


class Fun(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.group(invoke_without_command=True)
    async def nsfw(self, ctx, query="", mode=""):
        if ctx.invoked_subcommand is None:

            if ctx.channel.nsfw:
                if query in everything:
                    increaseUsed(query)
                    await sendSubmission(ctx, await reddit.subreddit(query), query)
                elif query == "":
                    await self._nsfw_list(ctx)
                else:
                    await ctx.message.delete()
                    await main._nsfw(ctx)
                    return
            else:
                await ctx.send(
                    f"\u274C{ctx.author.mention} - {ctx.message.content} can be called only in nsfw channel!")

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

            increaseUsed("random", title)
            await sendSubmission(ctx, await reddit.subreddit(title), title)
            return
        else:
            await ctx.send(f"\u274C{ctx.author.mention} - {ctx.message.content} can be called only in nsfw channel!")

    @nsfw.command(name="list")
    async def _nsfw_list(self, ctx):
        if ctx.channel.nsfw:
            await ctx.message.delete()
            await main._nsfw(ctx)
        else:
            await ctx.send(f"\u274C{ctx.author.mention} - {ctx.message.content} can be called only in nsfw channel!")

    @commands.command(description="Send random Gif by query")
    async def gif(self, ctx, *choice: str):
        """ Sends gif by query """
        await ctx.message.delete()
        embed = discord.Embed(
            colour=discord.Colour.random()
        )
        embed.set_footer(text=f"Requested by: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        url = "http://api.giphy.com/v1/gifs/search"
        limit = 25
        separator = "-"
        if len(choice) == 0:
            embed.set_image(url="https://giphy.com/gifs/confused-travolta-poor-wallet-3o6UB5RrlQuMfZp82Y")

            await ctx.channel.send(embed=embed)
        else:
            choice = separator.join(choice) if len(choice) >= 2 else choice[0]
            params = urllib.parse.urlencode({
                "q": choice,
                "api_key": "IycawWLHRSj5jSHw2VSIQbp8SyJ0WpqZ",
                "limit": limit,
                "rating": "r"
            })

            rnd = random.randrange(00, limit)
            with urllib.request.urlopen(url + "?" + params) as response:
                data = json.loads(response.read())
                if len(data['data']) > 0:
                    gifUrl = f"https://media1.giphy.com/media/{data['data'][rnd]['id']}/giphy.gif"
                    embed.set_image(url=gifUrl)
                    await ctx.channel.send(embed=embed)
                else:
                    print("invalid gif query")
                    await(ctx.send("Invalid Query or non-existing gif"))

    @commands.command(name='testing')
    async def testing(self, ctx, input="10"):
        print(input)


def setup(client):
    client.add_cog(Fun(client))
