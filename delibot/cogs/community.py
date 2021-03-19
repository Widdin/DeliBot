import json

import discord
from discord.ext import commands
from requests_html import AsyncHTMLSession


class Community(commands.Cog):
    """
    Commands for Community-day.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    async def update_cday(self, ctx):

        if ctx.author.id != 306926179074703362:
            return

        await ctx.message.delete()

        asession = AsyncHTMLSession()
        res = await asession.get('https://pokemongolive.com/en/events/community-day/')
        await res.html.arender(wait=5.0, sleep=2.0)  # this call executes the js in the page
        await asession.close()

        date = res.html.find('.communityday__hero__next-event__date')
        bonuses = res.html.find('.communityday__hero__bubble__value')

        for bonus in bonuses:
            print(bonus.text)

        data = {'community': []}

        data['community'].append({
            'pokemon': bonuses[0].text,
            'bonusOne': bonuses[2].text,
            'bonusTwo': bonuses[3].text,
            'move': bonuses[1].text,
            'day': date[0].text
        })

        with open('json/data.json', 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
            outfile.close()

        await ctx.message.channel.send("Updated", delete_after=10)

    @commands.command(pass_context=True,
                      aliases=["cd", "Cd", "Cday", "cday", "community", "Community", "Community_day"])
    async def community_day(self, ctx, region: str = None, GMT=None):
        """
        Information message of the next Community-day.
        """
        await ctx.message.delete()

        data = []
        with open('json/data.json') as json_file:
            data = json.load(json_file)
            json_file.close()

        # Retrieve translation from JSON.
        featured_pokemon_title, exclusive_move_title, bonus_title, date_title, official_page_title, community_day_title = await self.bot.get_cog(
            "Utils").get_translation(ctx.message.guild.id,
                                     "FEATURED_POKEMON EXCLUSIVE_MOVE BONUS DATE OFFICIAL_PAGE COMMUNITY_DAY")

        description = (f"[{official_page_title}](https://pokemongolive.com/events/community-day/)")

        featured_pokemon = f":star2: __{featured_pokemon_title}__"
        featured_pokemon_contents = " "

        exclusive_move = f":shield: __{exclusive_move_title}__"
        exclusive_move_contents = " "

        bonus_one = f":star: __{bonus_title}__"
        bonus_one_contents = " "

        bonus_two = f":star: __{bonus_title}__"
        bonus_two_contents = " "

        date = f":calendar_spiral: __{date_title}__"

        date_contents = "Aug 11 & 12, 11:00 AM - 2:00 PM"

        for c in data['community']:
            featured_pokemon_contents = c['pokemon']
            exclusive_move_contents = c['move']
            bonus_one_contents = c['bonusOne']
            bonus_two_contents = c['bonusTwo']
            date_contents = c['day']

        date_contents += ', 11:00 PM - 2:00 PM'

        embed = discord.Embed(colour=0x0000FF, description=description)
        embed.title = community_day_title

        utils = self.bot.get_cog("Utils")
        pokemon_id = await utils.get_pokemon_id(featured_pokemon_contents)
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + str(
                pokemon_id) + "_00_shiny.png")
        embed.set_image(url="https://storage.googleapis.com/pokemongolive/communityday/PKMN_Community-Day-logo2.png")

        embed.add_field(name=featured_pokemon, value="\u2022 " + featured_pokemon_contents + "\n\u200b")
        embed.add_field(name=exclusive_move, value="\u2022 " + exclusive_move_contents + "\n\u200b")
        embed.add_field(name=bonus_one, value="\u2022 " + bonus_one_contents + "\n\u200b")
        embed.add_field(name=bonus_two, value="\u2022 " + bonus_two_contents + "\n\u200b")
        embed.add_field(name=date, value="\u2022 " + date_contents + "\n\u200b")

        await ctx.message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Community(bot))
