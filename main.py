import asyncio
import os

import discord

from discord.ext import commands
from dotenv import load_dotenv

import urllib
import json
import asyncpraw

import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.emojis = True


def get_prefix(client, message):
    with open("json/guild/guilds.json", 'r') as f:
        guilds = json.load(f)
    return str(guilds[f'{message.guild.id}']['settings']['prefix'])


bot = commands.Bot(command_prefix=".", description=description, intents=intents)

bot.remove_command('help')


@bot.event
async def on_ready():
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    print("Connected to: {}".format(len(bot.guilds)))
    print('------')
    await bot.change_presence(activity=discord.Game(name=".help"))


@bot.event
async def on_guild_join(guild):
    # Takes care of adding newly joined guilds into the json
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    await updateGuild(guilds, guild)

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

    # Takes care of adding emojis from newly joined guilds into the json file
    with open("json/guild/emojis.json", "r") as f:
        emojis = json.load(f)

    await updateEmoji(emojis, guild)

    with open("json/guild/emojis.json", "w") as f:
        json.dump(emojis, f, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    guilds.pop(f'{guild.id}')

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

    with open("json/guild/emojis.json", "r") as f:
        emojis = json.load(f)

    emojis.pop(f'{guild.id}')

    with open("json/guild/emojis.json", "w") as f:
        json.dump(emojis, f, indent=4)


# TODO Rewrite into JSON -> Should be done
@bot.event
async def on_guild_emojis_update(guild, before, after, ):
    with open("json/guild/emojis.json", "r") as f:
        emojis = json.load(f)

    missing = discord.Emoji
    if len(before) > len(after):
        for emojiBefore in before:
            if emojiBefore not in after:
                missing = emojiBefore
        await removeEmoji(emojis, missing)

    elif len(before) == len(after):
        for emojiBefore in before:
            for emojiAfter in after:
                if emojiBefore.id == emojiAfter.id and emojiBefore.name != emojiAfter.name:
                    missing = emojiAfter
        await editEmoji(emojis, missing, guild)

    with open("json/guild/emojis.json", "w") as f:
        json.dump(emojis, f, indent=4)


@bot.event
async def on_member_join(member):
    with open("json/user/users.json", 'r') as f:
        users = json.load(f)

    await updateUserData(users, member)

    with open("json/user/users.json", 'w') as f:
        json.dump(users, f, indent=4)


@bot.event
async def on_message(message):
    try:
        with open("json/user/users.json", 'r') as f:
            users = json.load(f)

        await updateUserData(users, message.author)
        # await addUserExperience(users, message)
        await levelUpUser(users, message.author, message)

        with open("json/user/users.json", 'w') as f:
            json.dump(users, f, indent=4)
    except ValueError:
        print("Problem with json.load()")

    await bot.process_commands(message)


async def updateUserData(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1


# TODO - Booster user should get 2times the amount of experience - Needs to check with booster user.
#   - Currently not working because message.author isn't compared correctly with the premium_subscribers
#   - Possible fix - go through the list with for, and if there is match change to true else false
#   - Probably would be great to store XP settings in the config file
#   - Would be great to have some sort of list of levels to like 10, then exponential increase in amount of experience needed

async def addUserExperience(users, message):
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    user = message.author
    booster = False
    for subscriber in message.guild.premium_subscribers:
        if user.id == subscriber.id:
            users[f'{message.author.id}']['experience'] += guilds[message.guild.id]['settings']['boosterxpgain']
            booster = True
    if not booster:
        users[f'{message.author.id}']['experience'] += guilds[f'{message.guild.id}']['settings']['xpgain']


async def levelUpUser(users, user, message):
    exp = users[f'{user.id}']['experience']
    lvStart = users[f'{user.id}']['level']
    lvEnd = int(exp ** (1 / 4))
    if (lvStart < lvEnd):
        users[f'{user.id}']['level'] += 1
        users[f'{user.id}']['experience'] = 0
        await message.channel.send(f"{user.mention} has leveled up to {users[f'{user.id}']['level']}")


async def updateGuild(guilds, guild):
    if not f'{guild.id}' in guilds:
        guilds[f'{guild.id}'] = {}
        guilds[f'{guild.id}']['members'] = guild.member_count
        guilds[f'{guild.id}']['votes'] = 0
        guilds[f'{guild.id}']['settings'] = {}
        guilds[f'{guild.id}']['settings']['prefix'] = "."
        guilds[f'{guild.id}']['settings']['xpgain'] = 1
        guilds[f'{guild.id}']['settings']['boosterxpgain'] = 2


async def updateEmoji(emojis, guild):
    if not f'{guild.id}' in emojis:
        # emojis['id'] = f'{len(emojis)}'
        emojis[f'{guild.id}'] = {}
        for emoji in guild.emojis:
            emojis[f'{guild.id}'][f'{emoji.id}'] = {}
            if emoji.animated:
                emojis[f'{guild.id}'][f'{emoji.id}']['emojiIID'] = f'<a:{emoji.name}:{emoji.id}>'
            else:
                emojis[f'{guild.id}'][f'{emoji.id}']['emojiIID'] = f'<:{emoji.name}:{emoji.id}>'
            emojis[f'{guild.id}'][f'{emoji.id}']['emojiName'] = f':{emoji.name}:'


async def removeEmoji(emojis, emoji):
    emojis.pop(f'{emoji.id}')


async def addEmoji(emojis, emoji, guild):
    emojis[f'{guild.id}'][f'{emoji.id}'] = {}
    if emoji.animated:
        emojis[f'{guild.id}'][f'{emoji.id}']['emojiIID'] = f'<a:{emoji.name}:{emoji.id}>'
    else:
        emojis[f'{guild.id}'][f'{emoji.id}']['emojiIID'] = f'<:{emoji.name}:{emoji.id}>'
    emojis[f'{guild.id}'][f'{emoji.id}']['emojiName'] = f':{emoji.name}:'


async def editEmoji(emojis, emoji, guild):
    if emoji.animated:
        emojis[f'{guild.id}'][f'{emoji.id}']['emojiIID'] = f'<a:{emoji.name}:{emoji.id}>'
    else:
        emojis[f'{guild.id}'][f'{emoji.id}']['emojiIID'] = f'<:{emoji.name}:{emoji.id}>'
    emojis[f'{guild.id}'][f'{emoji.id}']['emojiName'] = f':{emoji.name}:'


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')


@bot.command()
async def test(ctx):
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    for guild in bot.guilds:
        await updateGuild(guilds, guild)

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)


@bot.command(description="Send random Gif by query")
async def gif(ctx, *choice: str):
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


# TODO Rewrite into JSON
#   - Somewhat working, but really badly
#   - Needs to remove emojis from guild '808738863823847427'
@bot.command(pass_context=True, description="Sends random emoji from random Discord")
async def randomEmoji(ctx):
    guilds = bot.guilds
    randomGuild = guilds[random.randrange(0, len(guilds))]
    guildEmojis = randomGuild.emojis
    randomEmoji = guildEmojis[random.randrange(0, len(guildEmojis))]

    with open("json/guild/emojis.json", "r") as f:
        emojis = json.load(f)

    await ctx.message.delete()
    await ctx.send(emojis[f'{randomGuild.id}'][f'{randomEmoji.id}']['emojiIID'])

@bot.command()
async def changeprefix(ctx, p):
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    if len(p) != 1:
        p = p + " "
    guilds[f'{ctx.guild.id}']['settings']['prefix'] = p

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

    await ctx.send(f"{ctx.author.mention} Prefix changed to {p}")


@bot.command(description="Send NSFW image from Reddit")
async def nsfw(ctx, query="list", mode=""):
    normal = ["gonewild", "realgirls", "worldpacks", "celebnsfw", "asiansgonewild", "collegesluts",
              "petitegonewild", "bustypetite", "legalteens", "adorableporn", "breedingmaterial", "onlyfansgirls101",
              "milf", "porn", "tiktoknsfw", "pussy", "boobs", "tikthots", "tittydrop", "gonewild30plus",
              "onlyfans101", "biggerthanyouthought", "nsfw_japan"]
    hentai = ["hentai", "rule34", "hentai_gif", "animemilfs", "yuri"]
    all = normal + hentai
    channel = ctx.channel


    reddit = asyncpraw.Reddit(
        client_id="p18AlHfMXRP79Q",
        client_secret="HwzFCkqKIOhK2nG1lONZ6y3qFQ7tKw",
        user_agent="desktop:python.DiscordBot:v0.0.1 (by u/soveticka)"
    )

    if channel.nsfw:
        if query == "list":
            await ctx.message.delete()
            await _nsfw(ctx)
            return
        elif query == "random" or query in normal or query in hentai:
            if query in normal:
                subreddit = await reddit.subreddit(query)
                title=query
            elif query in hentai:
                subreddit = await reddit.subreddit(query)
                title=query

            elif query == "random":
                if mode == "real":
                    rnd = random.randrange(0, len(normal))
                    subreddit = await reddit.subreddit(normal[rnd])
                    title = normal[rnd]

                elif mode == "hentai":
                    rnd = random.randrange(0, len(hentai))
                    subreddit = await reddit.subreddit(hentai[rnd])
                    title = hentai[rnd]

                elif mode == "all":
                    rnd = random.randrange(0, len(all))
                    subreddit = await reddit.subreddit(all[rnd])
                    title = all[rnd]
                elif mode == "":
                    rnd = random.randrange(0, len(all))
                    subreddit = await reddit.subreddit(all[rnd])
                    title = all[rnd]
                else:
                    await ctx.message.delete()
                    await _nsfw(ctx)
                    return
            try:
                submission = await subreddit.random()
            except Exception:
                print("error")
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
                    await ctx.send(f"/r/{title}\n{submission.url}")
            except AttributeError:
                print(f"In submission were not all needed information")
                await nsfw(ctx, query, mode)
        else:
            await ctx.message.delete()
            await _nsfw(ctx)
            return
    else:
        await ctx.send("Příkaz pošli do nsfw kanálu :)")
    await reddit.close()
    try:
        await ctx.message.delete()
    except:
        print("No message to delete")


@bot.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)


#@bot.command(pass_context=True)
@bot.group()
async def help(ctx):
    if ctx.invoked_subcommand is None:
        channel = ctx.message.channel

        embed = discord.Embed(
            colour=discord.Colour.purple(),
            description="Help is currently WIP"
        )

        embed.set_author(name='Commands and Stuff')
        for command in bot.commands:
            if command.name != bot:
                if command.description == "":
                    desc = "WIP"
                else:
                    desc = command.description
                embed.add_field(name='{}{}'.format(get_prefix(bot, ctx.message), command.name), value=desc, inline=True)

        await channel.send(embed=embed)


@help.command(name="nsfw")
async def _nsfw(ctx):
    await ctx.message.delete()
    normal = ["gonewild", "realgirls", "worldpacks", "celebnsfw", "asiansgonewild", "collegesluts",
              "petitegonewild", "bustypetite", "legalteens", "adorableporn", "breedingmaterial", "onlyfansgirls101",
              "milf", "porn", "tiktoknsfw", "pussy", "boobs", "tikthots", "tittydrop", "gonewild30plus",
              "onlyfans101", "biggerthanyouthought", "nsfw_japan"]
    hentai = ["hentai", "rule34", "hentai_gif", "animemilfs", "yuri"]
    prefix = get_prefix(bot, ctx.message)
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
        reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)
    except asyncio.TimeoutError:
        await message.delete()
    else:
        await message.delete()


bot.run(TOKEN)
