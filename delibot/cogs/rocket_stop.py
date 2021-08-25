import asyncio
from datetime import datetime

import discord
from discord.ext import commands


class RocketStop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=["rocket"])
    async def rocket_stop(self, ctx, pokemon: str, *, location: str):
        pokemon = pokemon.title()

        # Base message
        embed = discord.Embed()
        embed.title = "Setup..."

        try:
            message = await ctx.channel.send(embed=embed)
        except discord.Forbidden:
            await ctx.author.send("DeliBot does not have the proper permissions to send messages.")
            return
        except discord.HTTPException:
            return

        # 25 Minutes
        duration = 1500
        counter = 0

        while counter < duration:

            # Amount of minutes left.
            minutes_left = (duration - counter) / 60

            pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(pokemon)
            images = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id)

            # Embed.
            embed.title = 'Rocket Stop Invasion'
            embed.colour = discord.Color.purple()
            embed.set_thumbnail(url=images['url'])
            embed.description = f'**Encounter:** {pokemon}\n\n' \
                                f'**Location:** {location.title()}\n\n' \
                                f'**Time Left:** {minutes_left} Minutes\n'
            embed.set_footer(text="Last updated: ")
            embed.timestamp = datetime.utcnow()

            try:
                await message.edit(embed=embed)
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

            await asyncio.sleep(120)
            counter += 120
        else:
            # Timer has ran out.
            try:
                await message.delete()
            except discord.NotFound:
                pass
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass


def setup(bot):
    bot.add_cog(RocketStop(bot))
