import asyncio

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from numpy.random import choice


class Pokebox(commands.Cog):
    """
    Commands for Pokebox.
    """

    def __init__(self, bot):
        self.bot = bot
        self.items = {"common": ["500 XP", "500 Stardust", "100 Pokecoins"],
                      "uncommon": ["2000 XP", "2000 Stardust", "2x Rare Candy", "550 Pokecoins"],
                      "rare": ["10x Rare Candy", "2x Premium Raid Passes", "5200 Pokecoins", "1200 Pokecoins",
                               "2500 Pokecoins"],
                      "super rare": ["10x Premium Raid Passes", "10000 Stardust", "14500 Pokecoins"]}

        self.probabilities = {"rare": 0.1,
                              "super rare": 0.05,
                              "common": 0.5,
                              "uncommon": 0.35
                              }

    @commands.command(name="pokebox", aliases=['gift', 'box', 'reward'])
    @commands.cooldown(1, 10, BucketType.user)
    async def pokebox(self, ctx):
        """
        Totally useless but fun command.
        Opens a box with a random reward.
        (Common, Uncommon, Rare, Super Rare)
        """
        await ctx.message.delete()

        rarity = choice(list(self.probabilities.keys()), p=list(self.probabilities.values()))
        item = choice(self.items[rarity])

        embed = discord.Embed(color=discord.Colour.dark_gold())
        embed.set_image(
            url="https://ksr-ugc.imgix.net/assets/014/214/330/9a141a9f5afb1e9c574ccf9175245b3a_original.gif?w=680&fit=max&v=1477105838&auto=format&gif-q=50&q=92&s=f40b4e1c03523310915c079c7ecda4a4")
        sent_embed = await ctx.message.channel.send(embed=embed)

        await asyncio.sleep(3.4)

        embed = discord.Embed(color=discord.Colour.dark_gold())
        img_url = await self.get_image(item)
        embed.set_thumbnail(url=img_url)
        embed.add_field(name=f"Wow, {rarity} item!", value=f"{ctx.message.author.mention} opened {item}!")
        await sent_embed.edit(embed=embed)

    @staticmethod
    async def get_image(msg):
        if "XP" in msg:
            return "https://vignette.wikia.nocookie.net/boss-fighting-stages-rebirth/images/f/f9/XPIcon.png/revision/latest?cb=20160711213320"
        elif "Stardust" in msg:
            return "https://vignette.wikia.nocookie.net/pokemongo/images/6/65/Stardust.png/revision/latest?cb=20160801135301"
        elif "Rare Candy" in msg:
            return "https://vignette.wikia.nocookie.net/pokemongo/images/a/a2/Rare_Candy.png/revision/latest/scale-to-width-down/200?cb=20170620212431"
        elif "Premium Raid" in msg:
            return "https://pokemongohub.net/wp-content/uploads/2017/06/item_prem_pass.png"
        elif "100 Pokecoins" in msg:
            return "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Item_COIN_HANDFUL_01.png"
        elif "550 Pokecoins" in msg:
            return "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Item_COIN_STACK_01.png"
        elif "1200 Pokecoins" in msg:
            return "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Item_COIN_POUCH_01.png"
        elif "2500 Pokecoins" in msg:
            return "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Item_COIN_BUCKET_01.png"
        elif "5200 Pokecoins" in msg:
            return "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Item_COIN_HEAP_01.png"
        elif "14500 Pokecoins" in msg:
            return "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Item_COIN_BOX_01.png"


def setup(bot):
    bot.add_cog(Pokebox(bot))
