import os

import discord

from discord.ext import commands
from dotenv import load_dotenv

import urllib
import json

import random

import database

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.emojis = True

bot = commands.Bot(command_prefix='.', description=description, intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    print("Connected to: {}".format(len(bot.guilds)))
    print('------')


@bot.event
async def on_guild_join(guild):
    database.registerToDB(guild)
    await on_ready()


@bot.event
async def on_guild_remove(guild):
    database.removeFromGuild(guild)


@bot.event
async def on_guild_emojis_update(guild, before, after, ):
    if len(before) > len(after):
        missing = discord.Emoji
        for emojiBefore in before:
            if emojiBefore not in after:
                missing = emojiBefore
        database.removeEmoji(missing)
    elif len(before) == len(after):
        missing = discord.Emoji
        for emojiBefore in before:
            for emojiAfter in after:
                if emojiBefore.id == emojiAfter.id and emojiBefore.name != emojiAfter.name:
                    missing = emojiAfter
        database.addEmoji(guild, missing)


@bot.event
async def on_member_join(member):
    with open("json/user/users.json", 'r') as f:
        users = json.load(f)

    await updateUserData(users, member)

    with open("json/user/users.json", 'w') as f:
        json.dump(f)
    database.addUser(member)


@bot.event
async def on_message(message):
    with open("json/user/users.json", 'r') as f:
        users = json.load(f)

    await updateUserData(users, message.author)
    await addUserExperience(users, message.author)
    await levelUpUser(users, message.author, message)

    with open("json/user/users.json", 'w') as f:
        json.dump(users, f)


async def updateUserData(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1


async def addUserExperience(users, user):
    users[f'{user.id}']['experience'] += 1


async def levelUpUser(users, user, message):
    exp = users[f'{user.id}']['experience']
    lvStart = users[f'{user.id}']['level']
    lvEnd = int(exp ** (1/4))
    if(lvStart < lvEnd):
        users[f'{user.id}']['level'] += 1
        users[f'{user.id}']['experience'] = 0
        await message.channel.send(f"{user.mention} has leveled up to {users[f'{user.id}']['level']}")


async def updateGuild(guilds, guild):
    if not f'{guild.id}' in guilds:
        guilds[f'{guild.id}'] = {}

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
    database.registerToDB(ctx.message.guild)


@bot.command(description="Send random Gif by query")
async def gif(ctx, *choice: str):
    await ctx.message.delete()
    url = "http://api.giphy.com/v1/gifs/search"
    limit = 25
    separator = "-"
    if len(choice) == 0:
        gifUrl = "https://giphy.com/gifs/confused-travolta-poor-wallet-3o6UB5RrlQuMfZp82Y"

        await ctx.send("Next time add some query text ❤️")
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
                gifUrl = data['data'][rnd]['url']
                await ctx.send(gifUrl)
            else:
                print("invalid gif query")
                await(ctx.send("Invalid Query or non-existing gif"))


@bot.command(pass_context=True, description="Sends random emoji from random Discord")
async def randomEmoji(ctx):
    emojis = database.query("SELECT * FROM Emoji WHERE NOT Guild_id=4")
    rndNumber = random.randrange(0, len(emojis))
    await ctx.message.delete()
    await ctx.send(emojis[rndNumber][1])


@bot.command(pass_context=True)
async def help(ctx):
    channel = ctx.message.channel

    embed = discord.Embed(
        colour=discord.Colour.purple()
    )

    embed.set_author(name='Commands and Stuff')
    for command in bot.commands:
        if command.name != bot:
            if command.description == "":
                desc = "WIP"
            else:
                desc = command.description
            embed.add_field(name='{}{}'.format(bot.command_prefix, command.name), value=desc, inline=True)

    await channel.send(embed=embed)


bot.run(TOKEN)
