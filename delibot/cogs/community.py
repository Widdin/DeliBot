import asyncio
import json
import logging
import discord
from discord.ext import commands
from requests_html import AsyncHTMLSession

log = logging.getLogger()


class Community(commands.Cog):
    """
    Commands for Community-day.
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.update_community_day())

    async def update_community_day(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            # Only update if the file is older than 1 day
            if not await self.bot.get_cog("Utils").is_modified_older_than('json/community_day.json', days=1):
                log.info("Skipping update because the JSON was recently modified.")

            else:
                log.info("Updating JSON for community_day")

                asession = AsyncHTMLSession()
                res = await asession.get('https://pokemongolive.com/en/events/community-day/')
                await res.html.arender(wait=5.0, sleep=2.0)  # Execute JS
                await asession.close()

                date = res.html.find('.communityday__hero__next-event__date')
                bonuses = res.html.find('.communityday__hero__bubble__value')

                data = {'community': []}

                data['community'].append({
                    'pokemon': bonuses[0].text,
                    'bonusOne': bonuses[2].text,
                    'bonusTwo': bonuses[3].text,
                    'move': bonuses[1].text,
                    'day': date[0].text
                })

                await self.bot.get_cog("Utils").dump_json('json/community_day.json', data)

                log.info("Successfully updated.")

            await asyncio.sleep(86400)

    @commands.command(pass_context=True,
                      aliases=["cd", "Cd", "Cday", "cday", "community", "Community", "Community_day"])
    async def community_day(self, ctx):
        """Information message of the next Community-day."""
        await ctx.message.delete()

        embed = await self.get_embed_community_day(self, ctx.message.guild.id)

        await ctx.message.channel.send(embed=embed)

    @staticmethod
    async def get_embed_community_day(self, server_id: int):

        with open('json/community_day.json') as json_file:
            data = json.load(json_file)
            json_file.close()

        # Retrieve translation from JSON.
        featured_pokemon_title, exclusive_move_title, bonus_title, date_title, official_page_title, community_day_title = await self.bot.get_cog(
            "Utils").get_translation(server_id,
                                     "FEATURED_POKEMON EXCLUSIVE_MOVE BONUS DATE OFFICIAL_PAGE COMMUNITY_DAY")

        description = f"[{official_page_title}](https://pokemongolive.com/events/community-day/)"
        featured_pokemon = f":star2: __{featured_pokemon_title}__"
        exclusive_move = f":shield: __{exclusive_move_title}__"
        bonus_one = f":star: __{bonus_title}__"
        bonus_two = f":star: __{bonus_title}__"
        date = f":calendar_spiral: __{date_title}__"

        for c in data['community']:
            featured_pokemon_contents = c['pokemon']
            exclusive_move_contents = c['move']
            bonus_one_contents = c['bonusOne']
            bonus_two_contents = c['bonusTwo']
            date_contents = c['day'] + ', 11:00 AM - 5:00 PM'

        pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(featured_pokemon_contents)

        embed = discord.Embed(title=community_day_title, colour=0x0000FF, description=description)

        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + str(
                pokemon_id) + "_00_shiny.png")
        embed.set_image(url="https://storage.googleapis.com/pokemongolive/communityday/PKMN_Community-Day-logo2.png")

        embed.add_field(name=featured_pokemon, value="\u2022 " + featured_pokemon_contents + "\n\u200b")
        embed.add_field(name=exclusive_move, value="\u2022 " + exclusive_move_contents + "\n\u200b")
        embed.add_field(name=bonus_one, value="\u2022 " + bonus_one_contents + "\n\u200b")
        embed.add_field(name=bonus_two, value="\u2022 " + bonus_two_contents + "\n\u200b")
        embed.add_field(name=date, value="\u2022 " + date_contents + "\n\u200b")

        return embed


def setup(bot):
    bot.add_cog(Community(bot))
