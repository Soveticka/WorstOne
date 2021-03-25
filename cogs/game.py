import asyncio
import json

import discord
import random
from discord.ext import commands, tasks
from variables import game


class Game(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.regenerateStats.start()

    @classmethod
    def getResourceAmount(cls, resource, decimal=''):

        if decimal == '-d':
            return '{:.3f}'.format(round(resource, 3))
        else:
            return resource.__round__()

    @classmethod
    def getRegen(cls, houseLevel=''):
        if houseLevel != '':
            return int(game.baseManaRefill + (6 * int(houseLevel) / 60))
        else:
            return int(game.baseLifeRefill)

    @tasks.loop(minutes=1)
    async def regenerateStats(self):
        with open("./json/user/users.json", 'r') as f:
            users = json.load(f)
        f.close()

        for user in users:
            if users[user]['stats']['mana'] < game.baseMana:
                users[user]['stats']['mana'] += self.getRegen(users[user]['tools']['House'])
            if users[user]['stats']['health'] < game.baseLife:
                users[user]['stats']['health'] += self.getRegen()

        with open("./json/user/users.json", 'w') as f:
            json.dump(users, f, indent=4)
        f.close()

    @commands.command(aliases=['i', 'inv'])
    async def inventory(self, ctx, decimal=''):

        with open("./json/user/users.json", "r") as f:
            users = json.load(f)
        f.close()

        user = users[f'{ctx.author.id}']
        userStats = user["stats"]
        userResources = user["resources"]
        userTools = user["tools"]

        embed = discord.Embed(
            colour=discord.Colour.from_rgb(r=246, g=143, b=255),
        )
        embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.avatar_url}')

        embed.add_field(name="✨ Level", value=f'{userStats["level"]} (XP: {userStats["experience"]})', inline=True)
        embed.add_field(name="<:mana:818545064576942110> Mana",
                        value=f'{userStats["mana"]} [{self.getRegen(userTools["House"])}\\m]', inline=True)
        embed.add_field(name="❤️ Level", value=f'{userStats["health"]} [{self.getRegen()}\\m]', inline=True)

        # **Resources**
        embed.add_field(
            name="Resources #1",
            value=f'<:stone:818545064321613866> Stone: {self.getResourceAmount(userResources["Stone"], decimal)}\n'
                  f'<:woodPlank:818545064313749505> Wood: {self.getResourceAmount(userResources["Wood"], decimal)}\n'
                  f'<:coal:818545064232878102> Coal: {self.getResourceAmount(userResources["Coal"], decimal)}',
            inline=True
        )

        embed.add_field(
            name="Resources #2",
            value=f'<:ironOre:818545064397635659> Iron: {self.getResourceAmount(userResources["Iron"], decimal)}\n'
                  f'<:goldOre:818545064426864712> Gold: {self.getResourceAmount(userResources["Gold"], decimal)}\n'
                  f'<:obsidianOre:818545065415933983> Obsidian: {self.getResourceAmount(userResources["Obsidian"], decimal)}',
            inline=True
        )

        embed.add_field(
            name="Resources #3",
            value=f'<:ruby:818545064656502814> Ruby: {self.getResourceAmount(userResources["Ruby"], decimal)}\n'
                  f'<:emerald:818545064514945094> Emerald: {self.getResourceAmount(userResources["Emerald"], decimal)}\n'
                  f'<:sapphire:818545064749170699> Sapphire: {self.getResourceAmount(userResources["Sapphire"], decimal)}',
            inline=True
        )

        embed.add_field(
            name="Resources #4",
            value=f'<:cobalt:818545064208629831> Cobalt: {self.getResourceAmount(userResources["Cobalt"], decimal)}\n'
                  f'<:mithril:818545064678129695> Mithril: {self.getResourceAmount(userResources["Mithril"], decimal)}\n'
                  f'<:adamantine:818545064472084511> Adamantine: {self.getResourceAmount(userResources["Adamantine"], decimal)}',
            inline=True
        )

        embed.add_field(
            name="Resources #5",
            value=f'<:titaniumOre:818545064891383828> Titan: {self.getResourceAmount(userResources["Titan"], decimal)}\n'
                  f'<:uranium:818545064582185043> Uranium: {self.getResourceAmount(userResources["Uranium"], decimal)}\n'
                  f'<:plutonium:818545065110011935> Plutonium: {self.getResourceAmount(userResources["Plutonium"], decimal)}',
            inline=True
        )

        embed.add_field(
            name="Resources #6",
            value=f'Dirt: {self.getResourceAmount(userResources["Dirt"], decimal)}\n'
                  f'Gravel: {self.getResourceAmount(userResources["Gravel"], decimal)}\n'
                  f'Sand: {self.getResourceAmount(userResources["Sand"], decimal)}\n'
                  f'Clay: {self.getResourceAmount(userResources["Clay"], decimal)}',
            inline=True
        )

        # ** Items **
        embed.add_field(
            name="Items",
            value=f'<:goldPick:818545064556101659> Pickaxe: {userTools["Pickaxe"]}\n'
                  f'<:goldAxe:818545064510357504> Axe: {userTools["Axe"]}\n'
                  f'<:goldShovel:818545064220819530> Shovel: {userTools["Shovel"]}\n'
                  f'<:ringRed:818545064418476083> Ring: {userTools["Ring"]}\n'
                  f'🏠 House: {userTools["House"]}\n'
                  f'⚙️ Generator: {userTools["Generator"]}\n'
                  f'<:sword:818545064577466422> Sword: {userTools["Sword"]}\n'
                  f'<:shieldRed:818545064581136404> Shield: {userTools["Shield"]}\n'
                  f'🎣 Fishing Rod: {userTools["FishingRod"]}',
            inline=False
        )
        message = await ctx.message.channel.send(embed=embed)
        await message.add_reaction(u"\u274C")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == u"\u274C"

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=None, check=check)
        except asyncio.TimeoutError:
            await message.delete()
        else:
            await message.delete()

    @commands.command()
    async def mine(self, ctx, manaUsedInput=None):
        with open("./json/user/users.json", 'r') as f:
            users = json.load(f)
        f.close()

        with open('./json/game/resources.json', 'r') as file:
            resourceList = json.load(file)
        file.close()

        userPick = users[f'{ctx.author.id}']['tools']['Pickaxe']
        pickLevel = 5 if userPick >= 5 else userPick
        if manaUsedInput is None:
            manaUsed = 10
        elif manaUsedInput == "all" or manaUsedInput == "a":
            manaUsed = users[f'{ctx.author.id}']['stats']['mana']
        elif int(manaUsedInput) > 0:
            manaUsed = int(manaUsedInput)
        else:
            return

        if users[f'{ctx.author.id}']['stats']['mana'] > manaUsed:

            for i in range(manaUsed):
                resource = random.choice(list(resourceList['mine'][f'{pickLevel}'].keys()))
                dropChance = random.randint(1, 100)
                baseStone = resourceList['mine']['base']['Stone']
                maxStone = resourceList['mine']['max']['Stone']
                possibleDrop = []

                if dropChance < resourceList['mine']['dropChance'][resource]:
                    amount = random.uniform((baseStone / 2) * userPick, (maxStone / 2) * userPick)
                    resourceList['mine'][f'{pickLevel}']['Stone'] += amount
                    continue

                if dropChance >= resourceList['mine']['dropChance'][resource]:
                    for drop in resourceList['mine'][f'{pickLevel}']:
                        if resourceList['mine']['rarity'][drop] >= resourceList['mine']['dropChance'][drop]:
                            possibleDrop.append(drop)

                    if len(possibleDrop) == 0:
                        continue
                    drop = random.choice(possibleDrop)
                    baseResource = resourceList['mine']['base'][drop]
                    maxResource = resourceList['mine']['max'][drop]
                    amount = random.uniform(baseResource * userPick, maxResource * userPick)
                    resourceList['mine'][f'{pickLevel}'][drop] += amount

            for resource in resourceList['mine'][f'{pickLevel}'].keys():
                if resource != 0:
                    print(resourceList['mine'][f'{pickLevel}'][resource])
                    users[f'{ctx.author.id}']['resources'][resource] += resourceList['mine'][f'{pickLevel}'][resource]

            users[f'{ctx.author.id}']['stats']['mana'] -= manaUsed
        else:
            ctx.send("Nedostatek Many vole")

        with open("./json/user/users.json", 'w') as f:
            json.dump(users, f, indent=4)
        f.close()


def setup(client):
    client.add_cog(Game(client))
