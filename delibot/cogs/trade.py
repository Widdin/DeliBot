import time

import discord
from discord.ext import commands


class Trade(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=["Want", "W", "w"])
    async def want(self, ctx, *, left: str):

        await ctx.message.delete()

        left = left.lower()

        left_list = left.split()

        left_pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(left_list[-1])

        if left_pokemon_id is None:
            await ctx.channel.send(
                ctx.message.author.mention + "That pokémon was not found. Some examples:\n\n``!want b unown``\n``!want shiny aron``\n``!want shiny ash pikachu``\n``!want snorlax``",
                delete_after=10)
            return

        left_link = "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + left_pokemon_id

        if 'unown' in left:
            left_link += "_" + await self.bot.get_cog("Utils").get_unown_id(left_list[0])
        else:
            if 'alola' in left:
                left_link += "_61"
            else:
                left_link += "_00"

            if 'pikachu' in left or 'pichu' in left:
                if any((True for x in left_list if x in ['ash', 'halloween', 'party', 'santa', 'safari'])):
                    if left_list[0] == 'shiny':
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(left_list[1])
                        left_link += "_" + pika_id
                    else:
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(left_list[0])
                        left_link += "_" + pika_id

            if 'shiny' in left:
                left_link += "_shiny"

        left_link += ".png"

        embed = discord.Embed(color=discord.Colour(0x0083ff))
        embed.set_author(name='Pokémon Trade',
                         icon_url='https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/trade_icon_small.png')
        embed.description = "**Trade with: ** " + ctx.message.author.mention + "\n\n**Looking for:** " + left.title()
        embed.set_thumbnail(url=left_link)
        embed.set_footer(text=str(ctx.message.author) + " | Created: " + time.strftime("%d/%m/%Y"),
                         icon_url=ctx.message.author.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command(pass_context=True, aliases=["Offer", "O", "o"])
    async def offer(self, ctx, *, left: str):

        await ctx.message.delete()

        left = left.lower()

        left_list = left.split()

        left_pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(left_list[-1])

        if left_pokemon_id is None:
            await ctx.channel.send(
                ctx.message.author.mention + "That pokémon was not found. Some examples:\n\n``!offer b unown``\n``!offer shiny aron``\n``!offer shiny ash pikachu``\n``!offer snorlax``",
                delete_after=10)
            return

        left_link = "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + left_pokemon_id

        if 'unown' in left:
            left_link += "_" + await self.bot.get_cog("Utils").get_unown_id(left_list[0])
        else:
            if 'alola' in left:
                left_link += "_61"
            else:
                left_link += "_00"

            if 'pikachu' in left or 'pichu' in left:
                if any((True for x in left_list if x in ['ash', 'halloween', 'party', 'santa', 'safari'])):
                    if left_list[0] == 'shiny':
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(left_list[1])
                        left_link += "_" + pika_id
                    else:
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(left_list[0])
                        left_link += "_" + pika_id

            if 'shiny' in left:
                left_link += "_shiny"

        left_link += ".png"

        embed = discord.Embed(color=discord.Colour(0xffae00))
        embed.set_author(name='Pokémon Trade',
                         icon_url='https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/trade_icon_small.png')
        embed.description = "**Trade with: ** " + ctx.message.author.mention + "\n\n**Offer:** " + left.title()
        embed.set_thumbnail(url=left_link)
        embed.set_footer(text=str(ctx.message.author) + " | Created: " + time.strftime("%d/%m/%Y"),
                         icon_url=ctx.message.author.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command(pass_context=True, aliases=["Trade", "T", "t"])
    async def trade(self, ctx, *, info: str):

        await ctx.message.delete()

        try:
            left, right = info.split(',')
        except ValueError:
            await ctx.channel.send('Missing arguments, correct usage: ``!trade {pokémon have*} , {pokémon want*}``', delete_after=15)
            return

        left = left.lower()
        right = right.lower()

        left_list = left.split()
        right_list = right.split()

        left_pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(left_list[-1])
        right_pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(right_list[-1])

        # TODO: Replace with get_pokemon_image_url
        left_link = "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + left_pokemon_id
        right_link = "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + right_pokemon_id

        # LEFT-SIDE
        if 'unown' in left:
            left_link += "_" + await self.bot.get_cog("Utils").get_unown_id(left_list[0])
        else:
            if 'alola' in left:
                left_link += "_61"
            else:
                left_link += "_00"

            if 'pikachu' in left or 'pichu' in left:
                if any((True for x in left_list if x in ['ash', 'halloween', 'party', 'santa', 'safari'])):
                    if left_list[0] == 'shiny':
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(left_list[1])
                        left_link += "_" + pika_id
                    else:
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(left_list[0])
                        left_link += "_" + pika_id

            if 'shiny' in left:
                left_link += "_shiny"

        # RIGHT-SIDE
        if 'unown' in right:
            right_link += "_" + await self.bot.get_cog("Utils").get_unown_id(right_list[0])
        else:
            if 'alola' in right:
                right_link += "_61"
            else:
                right_link += "_00"

            if 'pikachu' in right or 'pichu' in right:
                if any((True for x in right_list if x in ['ash', 'halloween', 'party', 'santa', 'safari'])):
                    if right_list[0] == 'shiny':
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(right_list[1])
                        right_link += "_" + pika_id
                    else:
                        pika_id = await self.bot.get_cog("Utils").get_pika_id(right_list[0])
                        right_link += "_" + pika_id

            if 'shiny' in right:
                right_link += "_shiny"

        left_link += ".png"
        right_link += ".png"

        embed = discord.Embed(color=discord.Colour(0xff00ff))
        embed.set_author(name='Pokémon Trade',
                         icon_url='https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/trade_icon_small.png')
        embed.description = "**Trade with: " + ctx.message.author.mention + "**\n\n**Offering:** " + left.title() + "\n\n**For:** " + right.title()
        embed.set_thumbnail(url=left_link)
        embed.set_image(url=right_link)
        embed.set_footer(text=str(ctx.message.author) + " | Created: " + time.strftime("%d/%m/%Y"),
                         icon_url=ctx.message.author.avatar_url)
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Trade(bot))
