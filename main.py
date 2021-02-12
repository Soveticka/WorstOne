import os

import discord

from discord.ext import commands
from dotenv import load_dotenv

import urllib
import json

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
    with open("json/guild/settings.json", 'r') as f:
        settings = json.load(f)
    return str(settings[f'{message.guild.id}']['prefix'])

bot = commands.Bot(command_prefix=get_prefix, description=description, intents=intents)

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
        json.dump(guilds, f)

    # Take care of adding emojis from newly joined guilds into the json file
    with open("json/guild/emojis.json", "r") as f:
        emojis = json.load(f)

    await updateEmoji(emojis, guild)

    with open("json/guild/emojis.json", "w") as f:
        json.dump(emojis, f)



@bot.event
async def on_guild_remove(guild):
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    guilds.pop(f'{guild.id}')

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f)

    with open("json/guild/settings.json", "r") as f:
        settings = json.load(f)

    settings.pop(f'{guild.id}')

    with open("json/guild/settings.json", "w") as f:
        json.dump(settings, f)

    with open("json/guild/emojis.json", "r") as f:
        emojis = json.load(f)

    emojis.pop(f'{guild.id}')

    with open("json/guild/settings.json", "w") as f:
        json.dump(emojis, f)

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
        json.dump(emojis, f)

    # if len(before) > len(after):
    #     missing = discord.Emoji
    #     for emojiBefore in before:
    #         if emojiBefore not in after:
    #             missing = emojiBefore
    #     database.removeEmoji(missing)
    # elif len(before) == len(after):
    #     missing = discord.Emoji
    #     for emojiBefore in before:
    #         for emojiAfter in after:
    #             if emojiBefore.id == emojiAfter.id and emojiBefore.name != emojiAfter.name:
    #                 missing = emojiAfter
    #     database.addEmoji(guild, missing)


@bot.event
async def on_member_join(member):
    with open("json/user/users.json", 'r') as f:
        users = json.load(f)

    await updateUserData(users, member)

    with open("json/user/users.json", 'w') as f:
        json.dump(f)


@bot.event
async def on_message(message):
    if message.content.startswith(get_prefix(bot, message)) and not message.author.bot:
        with open("json/user/users.json", 'r') as f:
             users = json.load(f)

        await updateUserData(users, message.author)
        await addUserExperience(users, message.author)
        await levelUpUser(users, message.author, message)

        with open("json/user/users.json", 'w') as f:
             json.dump(users, f)

    await bot.process_commands(message)



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


async def updateSettings(settings, guild):
    if not f'{guild.id}' in settings:
        settings[f'{guild.id}'] = {}
        settings[f'{guild.id}']['prefix'] = "."


async def updateGuild(guilds, guild):
    with open("json/guild/settings.json", 'r') as f:
        settings = json.load(f)

    await updateSettings(settings, guild)

    with open("json/guild/settings.json", 'w') as f:
        json.dump(settings, f)

    if not f'{guild.id}' in guilds:
        guilds[f'{guild.id}'] = {}
        guilds[f'{guild.id}']['members'] = guild.member_count
        guilds[f'{guild.id}']['votes'] = 0


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
    guilds = bot.guilds
    print(guilds)

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

    # emojis = database.query("SELECT * FROM Emoji WHERE NOT Guild_id=4")
    # rndNumber = random.randrange(0, len(emojis))
    # await ctx.message.delete()
    # await ctx.send(emojis[rndNumber][1])


@bot.command(pass_context=True)
async def help(ctx):
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


@bot.command()
async def changeprefix(ctx, p):
    with open("json/guild/settings.json", "r") as f:
        settings = json.load(f)

    settings[f'{ctx.guild.id}']['prefix'] = p

    with open("json/guild/settings.json", "w") as f:
        json.dump(settings, f)

    await ctx.send(f"Prefix changed to {p}")

bot.run(TOKEN)
