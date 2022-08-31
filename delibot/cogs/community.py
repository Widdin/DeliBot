import asyncio
import json
import logging

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger()


class Community(commands.Cog):
    """
    Commands for Community-day.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.loop.create_task(self.update_community_day())

    async def update_community_day(self):
        while not self.bot.is_closed():
            if not await self.bot.get_cog("Utils").is_modified_older_than('json/community_day.json', days=1):
                log.info("Skipping update because the JSON was recently modified. Sleeping for 1 day.")
            else:
                log.info("Updating JSON for community_day")

                url = 'https://raw.githubusercontent.com/ccev/pogoinfo/v2/active/events.json'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            json = await response.json(content_type='text/plain')
                        else:
                            return

                for event in json:
                    if event['type'] == "community-day":
                        await self.bot.get_cog("Utils").dump_json('json/community_day.json', event)
                        log.info("Successfully updated.")
                        break

            await asyncio.sleep(86400)

    @app_commands.command(name="community_day", description='Information message of the next Community-day')
    async def community_day(self, interaction: discord.Interaction):
        """Information message of the next Community-day."""
        embed = await self.get_embed_community_day(self, interaction.guild_id)

        await interaction.response.send_message(embed=embed)

    @staticmethod
    async def get_embed_community_day(self, server_id: int):

        with open('json/community_day.json') as json_file:
            data = json.load(json_file)

        # Retrieve translation from JSON.
        featured_pokemon_title, exclusive_move_title, bonus_title, date_title, official_page_title, community_day_title = await self.bot.get_cog(
            "Utils").get_translation(server_id,
                                     "FEATURED_POKEMON EXCLUSIVE_MOVE BONUS DATE OFFICIAL_PAGE COMMUNITY_DAY")

        embed = discord.Embed(title=data["name"],
                              colour=0x0000FF,
                              description=f':calendar_spiral: **Starts:** {data["start"]}\n\n:calendar_spiral: **Ends:** {data["end"]}')

        if data["shinies"]:
            embed.set_thumbnail(
                url=f'https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_{data["shinies"][0]["id"]}_00_shiny.png')

        embed.set_image(url="https://storage.googleapis.com/pokemongolive/communityday/PKMN_Community-Day-logo2.png")

        for bonus in data["bonuses"]:
            embed.add_field(name=f":star: {bonus_title}", value=bonus['text'] + "\n\u200b", inline=False)

        return embed


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
