import asyncio
import json
import math
import os
import logging
import discord
import time
import pymysql
from pathlib import Path
from discord.ext import commands

from cogs.paginator import HelpPaginator

from utils import default

config = default.get_config()
log = logging.getLogger()


class Utils(commands.Cog):
    """Commands for various things."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """When delibot joins a server and the guild
        doesn't exist in the database, add it."""
        query = "INSERT INTO settings (server_id) VALUES (%s)"
        params = (str(guild.id), )

        try:
            await self.bot.db.execute(query, params)
            log.info(f'Server "{guild.name}" ({guild.id}) inserted.')
        except pymysql.err.IntegrityError:
            log.info(f'Server "{guild.name}" ({guild.id}) already exist.')
            return

    async def create_user_if_not_exist(self, guild_id: str, user_id: str):
        """If a user doesn't exist in the database, add it."""
        query = "INSERT INTO users (server_id, user_id) VALUES (%s, %s)"
        params = (str(guild_id), str(user_id))

        try:
            await self.bot.db.execute(query, params)
            log.info(f'User {user_id} and server {guild_id} inserted.')
        except pymysql.err.IntegrityError:
            log.info(f'User {user_id} and server {guild_id} already exist.')
            return

    async def get_gym(self, server_id: str, gym_name: str):
        query = "SELECT name, lat, lon FROM gyms WHERE server_id = %s AND name LIKE %s ORDER BY CHAR_LENGTH(name) ASC"
        params = (str(server_id), "%" + gym_name + "%")
        gym = await self.bot.db.execute(query, params, single=True)

        if gym is not None:
            gmaps = f'https://www.google.com/maps/place/{gym[1]},{gym[2]}'
            return f'[{gym[0].title()}]({gmaps})'
        else:
            return f'{gym_name}'

    async def get_pokestop(self, server_id: str, pokestop_name: str):
        query = "SELECT name, lat, lon FROM pokestops WHERE server_id = %s AND name LIKE %s ORDER BY CHAR_LENGTH(name) ASC"
        params = (str(server_id), "%" + pokestop_name + "%")
        pokestop = await self.bot.db.execute(query, params, single=True)

        if pokestop is not None:
            gmaps = f'https://www.google.com/maps/place/{pokestop[1]},{pokestop[2]}'
            return f'[{pokestop[0].title()}]({gmaps})'
        else:
            return f'{pokestop_name}'

    @staticmethod
    async def get_static_map_url(lat, long):
        mapquest_key = config.get('TOKEN', 'mapquest-token')
        return f'https://www.mapquestapi.com/staticmap/v5/map?key={mapquest_key}&locations={lat},{long}&zoom=15&type=map&size=400,200@2x&defaultMarker=flag-HERE-sm'

    @staticmethod
    async def message_type(message):
        """Determine which type of message it is."""
        embed_content = message.embeds[0]
        try:
            if "Field Research Quest" in embed_content.get('author')['name']:
                return "research"
            elif "⭐" in embed_content.get('author')['name']:
                return "exraid"
            elif "Valor" in embed_content.get('fields')[0]['name']:
                return "raid"
            else:
                return "none"
        except TypeError:
            if "Trade" in embed_content.get('description'):
                return "trade"
            else:
                return "none"

    async def get_translation(self, guild_id: str, keys: str):
        query = "SELECT language FROM settings WHERE server_id = %s"
        params = (guild_id, )
        (language_code, ) = await self.bot.db.execute(query, params, single=True)

        file_path = Path('json/locale.json')

        if file_path.exists():
            with open(file_path, 'r', encoding='utf8') as f:
                data = json.load(f)
        else:
            log.critical(f'Could not find the JSON file located at "{file_path.absolute()}".')

        result = ()
        for key in keys.split(" "):
            result += (data[key][language_code],)

        return result

    @commands.group(invoke_without_command=True, aliases=['Stats', 'S', 's'])
    async def stats(self, ctx, user: discord.Member = None):
        """
        Displays detailed statistics.

        Example: *!stats @user* (for a specific user)
        Example: *!stats server* (for this server)
        Example: *!stats leaderboard* (for this server)
        Example: *!stats overall* (for all servers)
        """

        # Deletes the command
        await ctx.message.delete()

        if user is None:
            user_to_check = ctx.message.author
        else:
            user_to_check = user

        await self.create_user_if_not_exist(ctx.message.guild.id, ctx.message.author.id)

        query = "SELECT * FROM users WHERE server_id = %s AND user_id = %s"
        params = (ctx.message.guild.id, user_to_check.id)
        found_user = await self.bot.db.execute(query, params, single=True)

        # Retrieve translation from JSON.
        name_not_found, name_not_found_desc, stats, raids_joined, raids_created, research_created, contributor, leaderboard = await self.get_translation(
            ctx.message.guild.id,
            "NAME_NOT_FOUND NAME_NOT_FOUND_DESC STATS RAIDS_JOINED RAIDS_CREATED RESEARCH_CREATED CONTRIBUTOR Leaderboard")

        if found_user is None:
            embed = discord.Embed(title=name_not_found,
                                  description=name_not_found_desc,
                                  color=discord.Colour.dark_red())

            await ctx.message.channel.send(embed=embed, delete_after=10)
        else:
            embed = discord.Embed(title=f"{stats} {user_to_check.display_name}",
                                  color=user_to_check.color)
            embed.add_field(name=raids_created, value=f":medal: {found_user[2]}", inline=True)
            embed.add_field(name=raids_joined, value=f":medal: {found_user[3]}", inline=True)
            embed.add_field(name=research_created, value=f":medal: {found_user[4]}", inline=True)
            embed.add_field(name=contributor, value=f"<a:spin_coin:481038937666748418> {found_user[5]}", inline=True)
            embed.set_footer(text=f"{user_to_check.display_name}", icon_url=f"{user_to_check.avatar_url}")

            await ctx.message.channel.send(embed=embed)

    @stats.command()
    async def server(self, ctx):
        await ctx.message.delete()

        query = 'SELECT SUM(raids_created), SUM(raids_joined), SUM(research_created) FROM users WHERE server_id = %s'
        params = (ctx.message.guild.id, )
        raids_created_count, raids_joined_count, research_created_count = await self.bot.db.execute(query, params, single=True)

        # Retrieve translation from JSON.
        stats, raids_joined, raids_created, research_created, contributor, leaderboard = await self.get_translation(
            ctx.message.guild.id, "STATS RAIDS_JOINED RAIDS_CREATED RESEARCH_CREATED CONTRIBUTOR Leaderboard")

        embed = discord.Embed(title=f"{stats} {ctx.message.guild.name}", color=discord.Colour.purple())
        embed.add_field(name=raids_created, value=f"{raids_created_count}", inline=True)
        embed.add_field(name=raids_joined, value=f"{raids_joined_count}", inline=True)
        embed.add_field(name=research_created, value=f"{research_created_count}", inline=True)
        embed.set_footer(text=f"Requested by: {ctx.message.author.display_name}")
        await ctx.message.channel.send(embed=embed)

    @stats.command()
    async def leaderboard(self, ctx):
        await ctx.message.delete()

        query = 'SELECT * FROM users WHERE server_id = %s ORDER BY raids_created desc limit 5;'
        params = (ctx.message.guild.id, )
        raids_created_list = await self.bot.db.execute(query, params)

        query = 'SELECT * FROM users WHERE server_id = %s ORDER BY raids_joined desc limit 5;'
        params = (ctx.message.guild.id, )
        raids_joined_list = await self.bot.db.execute(query, params)

        query = 'SELECT * FROM users WHERE server_id = %s ORDER BY research_created desc limit 5;'
        params = (ctx.message.guild.id, )
        research_created_list = await self.bot.db.execute(query, params)

        embed = discord.Embed(title=f"Leaderboard for {ctx.message.guild.name}", color=discord.Colour.purple())
        emojis = [':first_place:', ':second_place:', ':third_place:', ':medal:', ':medal:', ':medal:', ':medal:',
                  ':medal:', ':medal:', ':medal:']

        raids_created_text = ""
        emoji_counter = 0
        for user in raids_created_list:
            member = ctx.message.guild.get_member(int(user[1]))
            raids_created_text += f"{emojis[emoji_counter]} **{member.display_name}** | {user[2]} \n"
            emoji_counter += 1

        raids_joined_text = ""
        emoji_counter = 0
        for user in raids_joined_list:
            member = ctx.message.guild.get_member(int(user[1]))
            raids_joined_text += f"{emojis[emoji_counter]} **{member.display_name}** | {user[3]} \n"
            emoji_counter += 1

        research_created_text = ""
        emoji_counter = 0
        for user in research_created_list:
            member = ctx.message.guild.get_member(int(user[1]))
            research_created_text += f"{emojis[emoji_counter]} **{member.display_name}** | {user[4]} \n"
            emoji_counter += 1

        # Retrieve translation from JSON.
        stats, raids_joined, raids_created, research_created, contributor, leaderboard = await self.bot.get_cog(
            "Utils").get_translation(
            ctx.message.guild.id, "STATS RAIDS_JOINED RAIDS_CREATED RESEARCH_CREATED CONTRIBUTOR Leaderboard")

        embed.add_field(name=f":trophy: {raids_created}", value=f"{raids_created_text} \n\u200b", inline=True)
        embed.add_field(name=f":trophy: {raids_joined}", value=f"{raids_joined_text}\n\u200b", inline=True)
        embed.add_field(name=f":trophy: {research_created}", value=f"{research_created_text}", inline=True)
        embed.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/commons/8/85/Hand_Gesture_-_Raising_a_Trophy.gif")
        embed.set_footer(text=f"Requested by: {ctx.message.author.display_name}")

        await ctx.message.channel.send(embed=embed)

    @stats.command()
    async def overall(self, ctx):
        await ctx.message.delete()

        query = "SELECT SUM(raids_created), SUM(raids_joined), SUM(research_created) FROM users"
        raids_created_count, raids_joined_count, research_created_count = await self.bot.db.execute(query, single=True)

        # Retrieve translation from JSON.
        stats, raids_joined, raids_created, research_created, contributor, leaderboard = await self.bot.get_cog(
            "Utils").get_translation(
            ctx.message.guild.id, "STATS RAIDS_JOINED RAIDS_CREATED RESEARCH_CREATED CONTRIBUTOR Leaderboard")

        embed = discord.Embed(title=f"{stats} Delibot", color=discord.Colour.purple())
        embed.add_field(name=raids_created, value=f"{raids_created_count}", inline=True)
        embed.add_field(name=raids_joined, value=f"{raids_joined_count}", inline=True)
        embed.add_field(name=research_created, value=f"{research_created_count}", inline=True)
        embed.set_footer(text=f"Requested by: {ctx.message.author.display_name}")

        await ctx.message.channel.send(embed=embed)

    @commands.group(invoke_without_command=True, name='find', aliases=['Find', 'f', 'F'])
    async def mysqlfinder(self, ctx, *, gym_name: str):
        """
        Retrieves the location of a created gym with a image and hyperlink.
        """
        await ctx.message.delete()

        embed = discord.Embed(title=f"Gym Information for {ctx.message.guild.name}", color=discord.Colour.purple())
        embed.set_thumbnail(url="https://obihoernchen.net/pokemon/core/img/rocket.png")

        # Retrieve gym location.
        gym_loc = await self.get_gym(ctx.message.guild.id, gym_name.lower())

        query = "SELECT name, lat, lon FROM gyms WHERE server_id = %s AND name LIKE %s"
        params = (ctx.message.guild.id, "%" + gym_name.lower() + "%")
        response = await self.bot.db.execute(query, params, single=True)

        if len(response) > 0:
            name, lat, lon = response

            if name is None:
                embed.add_field(name=f"Sorry, {gym_name} was not found.",
                                value=f"Are you sure the gym exist? Try finding it with '!list gym'", inline=False)
            else:
                embed.add_field(name=f"{gym_name.title()}", value=f"{gym_loc}", inline=False)
                try:

                    url = await self.get_static_map_url(lat, lon)
                    embed.set_image(url=url)
                except IndexError:
                    pass
            try:
                await ctx.message.author.send(embed=embed)
            except discord.Forbidden:
                embed = discord.Embed(title=f"Insufficient permissions.",
                                      description=f"{ctx.message.author.mention} You have either blocked me, or messages from strangers.\nEnable: Settings > Privacy & Safety > Allow direct messages from server members.",
                                      color=discord.Colour.dark_red())
                embed.set_footer(text="Auto-deleting in 20 seconds..")
                await ctx.message.channel.send(embed=embed, delete_after=20)
        else:
            embed.add_field(name=f"Sorry, {gym_name} was not found.",
                            value=f"Are you sure the gym exist? Try finding it with '!list gym'", inline=False)

            await ctx.message.author.send(embed=embed)
            return

    @commands.group(invoke_without_command=True, aliases=['List', 'l', 'L'])
    async def list(self, ctx):
        """
        Displays a list of all the created gyms.
        Usage: !list gym
        """
        embed = discord.Embed(title=f"List of available subcommands:",
                              color=discord.Colour.green())
        embed.add_field(name="list gyms", value="To view all gym locations.", inline=False)
        embed.add_field(name="list pokestops", value="To view all pokestop locations.", inline=False)
        # embed.add_field(name="list raids", value="To view all the active raids.", inline=False)
        # embed.add_field(name="list quests", value="To view today's quests.", inline=False)
        await ctx.message.channel.send(embed=embed, delete_after=20)

    @list.command(aliases=['Pokestop', 'pokestops', 'Pokestops', 'stops', 'Stops'])
    async def pokestop(self, ctx):

        query = 'SELECT * FROM pokestops WHERE server_id = %s ORDER BY name;'
        params = (ctx.message.guild.id, )
        pokestops = await self.bot.db.execute(query, params)

        total_embeds = math.ceil(len(pokestops) / 25)
        embed_dict = {}
        counter = 1

        for i in range(0, total_embeds):

            embed = discord.Embed(title=f'Page Nr.{counter} - Pokestops in {ctx.guild.name}',
                                  color=discord.Color.dark_green())
            embed.set_footer(text=f'Page {counter}/{total_embeds}')

            max_25_counter = 1
            for pokestop in pokestops:

                if max_25_counter == 25:
                    break

                gmaps = f'https://www.google.com/maps/place/{pokestop[2]},{pokestop[3]}'

                embed.add_field(name=f'{pokestop[1].title()}', value=f'[Location]({gmaps})', inline=True)
                pokestops = pokestops[1:]

                max_25_counter += 1

            embed_dict[counter] = embed
            counter += 1

        message = await ctx.message.channel.send(embed=embed_dict[1])
        await message.add_reaction('\U00002b05')
        await message.add_reaction('\U000027a1')

        counter = 1

        while True:

            def check(reaction, user):
                return reaction.message.id == message.id and user.id == ctx.message.author.id

            try:
                waited_reaction, waited_user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                return

            if str(waited_reaction.emoji) == '➡':
                counter += 1

                if counter > total_embeds:
                    counter = 1

                await message.remove_reaction('➡', waited_user)
                await message.edit(embed=embed_dict[counter])

            elif str(waited_reaction.emoji) == '⬅':
                counter -= 1

                if counter == 0:
                    counter = total_embeds

                await message.remove_reaction('⬅', waited_user)
                await message.edit(embed=embed_dict[counter])

    @list.command(aliases=['Gym', 'gyms', 'Gyms'])
    async def gym(self, ctx):

        query = 'SELECT * FROM gyms WHERE server_id = %s ORDER BY name;'
        params = (ctx.message.guild.id, )
        gyms = await self.bot.db.execute(query, params)

        total_embeds = math.ceil(len(gyms) / 25)
        embed_dict = {}
        counter = 1

        for i in range(0, total_embeds):

            embed = discord.Embed(title=f'Page Nr.{counter} - Gyms in {ctx.guild.name}',
                                  color=discord.Color.dark_green())
            embed.set_footer(text=f'Page {counter}/{total_embeds}')

            max_25_counter = 1
            for gym in gyms:

                if max_25_counter == 25:
                    break

                gmaps = f'https://www.google.com/maps/place/{gym[2]},{gym[3]}'

                embed.add_field(name=f'{gym[1].title()}', value=f'[Location]({gmaps})', inline=True)
                gyms = gyms[1:]

                max_25_counter += 1

            embed_dict[counter] = embed
            counter += 1

        message = await ctx.message.channel.send(embed=embed_dict[1])
        await message.add_reaction('\U00002b05')
        await message.add_reaction('\U000027a1')

        counter = 1

        while True:

            def check(reaction, user):
                return reaction.message.id == message.id and user.id == ctx.message.author.id

            try:
                waited_reaction, waited_user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                return

            if str(waited_reaction.emoji) == '➡':
                counter += 1

                if counter > total_embeds:
                    counter = 1

                await message.remove_reaction('➡', waited_user)
                await message.edit(embed=embed_dict[counter])

            elif str(waited_reaction.emoji) == '⬅':
                counter -= 1

                if counter == 0:
                    counter = total_embeds

                await message.remove_reaction('⬅', waited_user)
                await message.edit(embed=embed_dict[counter])

    @staticmethod
    async def get_pokemon_name(pokemon_id: str):
        file_path = Path('json/pokemon_id.json')

        if file_path.exists():
            with open(file_path, 'r', encoding='utf8') as f:
                data = json.load(f)
                return data.get(pokemon_id)

        log.critical(f'Could not find the JSON file located at "{file_path.absolute()}".')

    @staticmethod
    async def get_pokemon_id(pokemon_name: str):
        file_path = Path('json/pokemon_en_fr_de.json')

        if file_path.exists():
            with open(file_path, 'r', encoding='utf8') as f:
                data = json.load(f)
                return data.get(pokemon_name.title())

        log.critical(f'Could not find the JSON file located at "{file_path.absolute()}".')

    @staticmethod
    async def get_unown_id(pokemon_name: str):
        file_path = Path('json/unown.json')

        if file_path.exists():
            with open(file_path, 'r', encoding='utf8') as f:
                data = json.load(f)
                return data.get(pokemon_name.title())

        log.critical(f'Could not find the JSON file located at "{file_path.absolute()}".')

    @staticmethod
    async def get_pika_id(pokemon_name: str):
        file_path = Path('json/pikachu.json')

        if file_path.exists():
            with open(file_path, 'r', encoding='utf8') as f:
                data = json.load(f)
                return data.get(pokemon_name.title())

        log.critical(f'Could not find the JSON file located at "{file_path.absolute()}".')

    async def get_log_channel(self, server_id):
        query = "SELECT log_channel_id FROM settings WHERE server_id = %s"
        params = (server_id, )
        (channel_id, ) = await self.bot.db.execute(query, params, single=True)

        if channel_id is None:
            return None

        return int(channel_id)

    @staticmethod
    async def dump_json(path, data):
        with open(Path(path), 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    async def is_modified_older_than(path, days):
        try:
            date_modified = os.path.getmtime(path)
        except FileNotFoundError:
            log.info(f'{path} was not found. Creating it...')
            return True

        return (time.time() - date_modified) / 3600 > 24 * days

    @staticmethod
    async def get_pokemon_image_url(pokemon_id: int, shiny: bool, alola: bool, other: str = ""):
        url = f"https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_{pokemon_id}"

        # Giratina Origin Forme
        if pokemon_id == "487" and "o" in other.lower():
            url += "_12"

        # Deoxys Defense Forme
        elif pokemon_id == "386":
            url += "_14"

        # Therium forms for Tornadus / Thundurus / Landorus
        elif pokemon_id in ["641", "642", "645"]:
            url += "_12"

        elif pokemon_id == "150":
            url = "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_150_00_shiny.png"
            return url

        elif pokemon_id in ["487", "641", "642", "645", "646", "647", "648", "649"]:
            url += "_11"
        elif alola:
            url += "_61"
        else:
            url += "_00"

        if shiny:
            url += "_shiny"

        url += ".png"

        # Normal = pokemon_id_00.png
        # Alola = pokemon_id_61.png
        # Shiny = pokemon_id_00_shiny.png

        return url

    @commands.command()
    async def fusion(self, ctx, mon_one: str, mon_two: str):
        """
        Combines two Pokémon images and creates a single one.
        """
        await ctx.message.delete()

        try:
            mon_one_id = (await self.get_pokemon_id(mon_one)).lstrip("0")
            mon_two_id = (await self.get_pokemon_id(mon_two)).lstrip("0")
        except AttributeError:
            embed = discord.Embed(title="Error",
                                  description="Keep in mind that only generation 1 exists, and you have to spell the pokémon correctly.",
                                  color=discord.Color.red())
            embed.set_footer(text="Auto-deleting in 15 seconds..")
            await ctx.send(embed=embed, delete_after=15)
            return

        url = f'https://images.alexonsager.net/pokemon/fused/{mon_two_id}/{mon_two_id}.{mon_one_id}.png'

        embed = discord.Embed(title=f'{mon_one.title()} + {mon_two.title()} = ',
                              color=discord.Color.gold())
        embed.set_image(url=url)

        await ctx.send(embed=embed)

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot."""

        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @staticmethod
    async def days_hours_minutes(td):
        return td.days, td.seconds // 3600, (td.seconds // 60) % 60


def setup(bot):
    bot.add_cog(Utils(bot))
