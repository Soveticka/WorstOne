import os
from itertools import cycle

import discord

from discord.ext import commands
from dotenv import load_dotenv
from variables import game

import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.emojis = True

cogsLoad = ['owner.py', 'admin.py', 'game.py', 'fun.py', 'help.py']


def get_prefix(client, message):
    with open("json/guild/guilds.json", 'r') as f:
        guilds = json.load(f)
    return str(guilds[f'{message.guild.id}']['settings']['prefix'])


picturelist = os.listdir("./img/profile/")
pictures = cycle(picturelist)
bot = commands.Bot(command_prefix=get_prefix, description=description, intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    print("Connected to: {}".format(len(bot.guilds)))
    print('------')
    await bot.change_presence(activity=discord.Game(name=".help"))


async def errormessage(ctx):
    await ctx.send(f"{ctx.author.mention} You don't have permissions to use {ctx.message.content}")


for filename in cogsLoad:
    if filename.endswith('.py'):
        if 'help' not in filename:
            bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_guild_join(guild):
    # Takes care of adding newly joined guilds into the json
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    await updateGuild(guilds, guild)

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open("json/guild/guilds.json", "r") as f:
        guilds = json.load(f)

    guilds.pop(f'{guild.id}')

    with open("json/guild/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)


@bot.event
async def on_member_join(member):
    with open("json/user/users.json", 'r') as f:
        users = json.load(f)

    await updateUserData(users, member)

    with open("json/user/users.json", 'w') as f:
        json.dump(users, f, indent=4)


@bot.event
async def on_message(message):
    await bot.process_commands(message)


async def updateUserData(users, userToAdd):
    if f'{userToAdd.id}' not in users:
        user = users[f'{userToAdd.id}'] = {}

        userStats = user['stats'] = {}
        userStats['level'] = 1
        userStats['experience'] = 0
        userStats['mana'] = game.baseMana
        userStats['health'] = game.baseLife

        userResources = user['resources'] = {}
        userResources['Stone'] = 0
        userResources['Iron'] = 0
        userResources['Gold'] = 0
        userResources['Coal'] = 0
        userResources['Obsidian'] = 0
        userResources['Ruby'] = 0
        userResources['Emerald'] = 0
        userResources['Sapphire'] = 0
        userResources['Cobalt'] = 0
        userResources['Mithril'] = 0
        userResources['Adamantine'] = 0
        userResources['Titan'] = 0
        userResources['Uranium'] = 0
        userResources['Plutonium'] = 0
        userResources['Wood'] = 0
        userResources['Dirt'] = 0
        userResources['Gravel'] = 0
        userResources['Sand'] = 0
        userResources['Clay'] = 0

        userTools = user['tools'] = {}
        userTools['Pickaxe'] = 1
        userTools['Axe'] = 0
        userTools['Shovel'] = 0
        userTools['House'] = 0
        userTools['Ring'] = 0
        userTools['Generator'] = 0
        userTools['FishingRod'] = 0
        userTools['Sword'] = 0
        userTools['Shield'] = 0


async def updateGuild(guilds, guildToAdd):
    if f'{guildToAdd.id}' not in guilds:
        guild = guilds[f'{guildToAdd.id}'] = {}

        guild['members'] = guildToAdd.member_count

        guildSettings = guild['settings'] = {}
        guildSettings['prefix'] = "."
        guildSettings['nsfwChannel'] = ""
        guildSettings['commandsChannel'] = ""
        guildSettings['gameChannel'] = ""

        guildMemberStatus = guild['memberStatus'] = {}


bot.run(TOKEN)
