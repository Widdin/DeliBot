import aiohttp
import discord
from discord.ext import commands


class Silphroad(commands.Cog):
    """Commands related to Silphroad."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["Silphcard", "Scard", "scard", "s-card", "S-card", "silph", "Silph", "Silphroad", "silphroad"])
    async def silphcard(self, ctx, name: str):
        """
        Shows information of a players silphcard.
        Example: *!silphcard trnrtipsnick*
        """
        await ctx.message.delete()

        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(f"https://sil.ph/{name}.json") as response:
                json = await response.json()

        try:
            json = json['data']
        except:
            embed = discord.Embed(title=f"Error", description=f"{json['error']}",
                                  color=discord.Colour.dark_red())
            await self.bot.say(embed=embed, delete_after=10)
            return

        username = json['in_game_username']
        title = json['title']
        playstyle = json['playstyle']
        goal = json['goal']

        team = json['team']

        trainer_level = json['trainer_level']
        nest_migrations = json['nest_migrations']
        avatar_url = json['avatar']
        joined = json['joined']
        total_xp = json['xp']
        home_region = json['home_region']
        pokedex_count = json['pokedex_count']
        raid_average = json['raid_average']
        handshakes = json['handshakes']
        checkins = len(json['checkins'])
        badges = json['badges']
        edited = json['modified']
        top_6_pokemon_id = json['top_6_pokemon']
        top_6_pokemon_name = ""

        try:
            for pokemon_id in top_6_pokemon_id:
                pokemon_name = await self.bot.get_cog("Utils").get_pokemon_name("%03d" % ((pokemon_id),))
                top_6_pokemon_name += "► " + pokemon_name + "\n"
        # No favorite mons
        except:
            pass

        embed = discord.Embed(title=f"{title} {username} in {home_region}", description=f"{playstyle}, {goal}",
                              color=discord.Colour.orange())
        embed.add_field(name=":iphone: In-Game",
                        value=f"**► Level:** {trainer_level}\n**► Team:** {team}\n**► Pokedex:** {pokedex_count}\n**► XP:** {total_xp}\n**► Raids:** ~{raid_average} per week\n\u200b",
                        inline=True)

        embed.add_field(name=":trophy: Silphroad",
                        value=f"**► Badges:** {len(badges)}\n**► Check-Ins:** {checkins}\n**► Handshakes:** {handshakes}\n**► Joined:** {joined[:10]}\n**► Nest-Migrations:** {nest_migrations}\n\u200b",
                        inline=True)

        embed.add_field(name=":heartpulse: Favourite Pokémon", value=f"{top_6_pokemon_name}\n\u200b", inline=True)

        embed.add_field(name=":military_medal: Latest Badge", value=f"► {badges[-1]['Badge']['name']}\n\u200b",
                        inline=False)

        embed.set_thumbnail(url=avatar_url)
        embed.set_image(url=f"{badges[-1]['Badge']['image']}")
        embed.set_footer(text=f"The Silph Road ▪ Last edit {edited}",
                         icon_url="https://assets.thesilphroad.com/img/snoo_sr_icon.png")

        await ctx.message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Silphroad(bot))
