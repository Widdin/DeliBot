import asyncio
import datetime
import json
import logging
import aiohttp
import discord
from discord.ext import commands
from requests_html import AsyncHTMLSession

log = logging.getLogger()


class Admin(commands.Cog):
    """
    Commands for the Server Owner / Admins
    """

    def __init__(self, bot):
        self.bot = bot

        # Start background tasks
        self.bot.loop.create_task(self._init_update_raid_overview())
        self.bot.loop.create_task(self._init_update_ex_overview())
        self.bot.loop.create_task(self._init_update_event())
        self.bot.loop.create_task(self._init_update_community_day())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_community_day(self, ctx):
        """
        This will post a message that updates continuously with on-going / up-coming community days.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to display community day?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = await self.bot.get_cog("Community").get_embed_community_day(self, ctx.message.guild.id)
        embed.set_footer(text="Updates every day.")
        embed.timestamp = datetime.datetime.utcnow()
        event_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET community_day_channel_id = %s, community_day_message_id = %s WHERE server_id = %s"
        params = (channel_id, event_msg.id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

    async def _init_update_community_day(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            query = "SELECT * FROM settings WHERE community_day_channel_id IS NOT NULL AND community_day_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            log.info(f'Updating community day for {len(servers)} server(s)')

            with open('json/community_day.json') as json_file:
                data = json.load(json_file)
                json_file.close()

            for server in servers:
                server_id = server[0]
                channel_id = server[16]
                message_id = server[17]

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
                    date_contents = c['day'] + ', 11:00 PM - 2:00 PM'

                pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(featured_pokemon_contents)

                embed = discord.Embed(title=community_day_title, colour=0x0000FF, description=description)

                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + str(
                        pokemon_id) + "_00_shiny.png")
                embed.set_image(
                    url="https://storage.googleapis.com/pokemongolive/communityday/PKMN_Community-Day-logo2.png")

                embed.add_field(name=featured_pokemon, value="\u2022 " + featured_pokemon_contents + "\n\u200b")
                embed.add_field(name=exclusive_move, value="\u2022 " + exclusive_move_contents + "\n\u200b")
                embed.add_field(name=bonus_one, value="\u2022 " + bonus_one_contents + "\n\u200b")
                embed.add_field(name=bonus_two, value="\u2022 " + bonus_two_contents + "\n\u200b")
                embed.add_field(name=date, value="\u2022 " + date_contents + "\n\u200b")
                embed.set_footer(text="Updates every day | Last updated: ")
                embed.timestamp = datetime.datetime.utcnow()

                try:
                    await self.bot.http.edit_message(int(channel_id), int(message_id), embed=embed.to_dict())
                except discord.errors.NotFound:
                    query = "UPDATE settings SET community_day_channel_id = NULL, community_day_message_id = NULL WHERE server_id = %s"
                    params = (server_id,)
                    await self.bot.db.execute(query, params)
                except discord.errors.Forbidden:
                    pass

            await asyncio.sleep(86400)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unset_role_permission(self, ctx):
        """
        The role set with "set_role_permission" will become none.
        """
        await ctx.message.delete()

        query = "UPDATE settings SET role_permission = NULL WHERE server_id = %s"
        params = (ctx.message.guild.id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Permission role has been unset.",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_role_permission(self, ctx):
        """
        The role will be granted permissions to edit and delete any Raid and also use create/delete gym.
        You will be asked to tag a role by using @.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="What role would you like to give permission to edit/delete raids & add gyms?",
                              description="Please tag the role below by using @",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed)

        def check(message):
            return ctx.author.id == message.author.id

        try:
            wait_for_role = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        query = "UPDATE settings SET role_permission = %s WHERE server_id = %s"
        params = (wait_for_role.content[3:-1], ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Permission role has been set.",
                              description=f"{wait_for_role.content} is the chosen role for additional permissions.",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed, delete_after=20)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unset_ex_scan(self, ctx):
        """
        The channel set with "set_ex_scan" will become none.
        """
        await ctx.message.delete()

        query = "UPDATE settings SET exraid_channel_id = NULL WHERE server_id = %s"
        params = (ctx.message.guild.id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="EX-Pass Scanning Channel has been unset.",
                              description="EX-Pass Scanning is now offline!",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_ex_scan(self, ctx):
        """
        The channel will be continuously checked for EX-Raid-pass images and create EX-raids based on the text on the image.
        You will be asked to tag a channel by using #.
        """

        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to scan for EX-Pass screenshots?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(m):
            return m.author.id == ctx.message.author.id

        try:
            channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET exraid_channel_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="EX-Pass Scanning has been set.",
                              description="This is the chosen channel for scanning EX-Pass screenshots!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unset_profile_scan(self, ctx):
        """
        The channel set with "set_profile_scan" will become none.
        """
        await ctx.message.delete()

        query = "UPDATE settings SET profile_channel_id = NULL WHERE server_id = %s"
        params = (ctx.message.guild.id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Profile Scanning Channel has been unset.",
                              description="Profile Scanning is now offline!",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed, delete_after=20)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_profile_scan(self, ctx):
        """
        The channel will be continuously checked for Team images and give the player that posts an image a role based on their color.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to assign teams?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET profile_channel_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Profile Scanning has been set.",
                              description="This is the chosen channel for auto-assigning teams!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unset_raid_channel(self, ctx):
        """
        The channel set with "set_raid_channel" will become none.
        """
        await ctx.message.delete()

        query = "UPDATE settings SET default_raid_id = NULL WHERE server_id = %s"
        params = (ctx.message.guild.id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Raid Channel has been unset.",
                              description="Raids will be posted in the channel they are invoked.",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed, delete_after=20)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_raid_channel(self, ctx):
        """
        Any Raid that gets created will be automagically posted in this channel.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to post Raids?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET default_raid_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Raid Channel has been set.",
                              description="This is the chosen channel for posting Raids!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unset_ex_channel(self, ctx):
        """
        The channel set with "set_ex_channel" will become none.
        """
        await ctx.message.delete()

        query = "UPDATE settings SET default_exraid_id = NULL WHERE server_id = %s"
        params = (ctx.message.guild.id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="EX-Raid Channel has been unset.",
                              description="EX-Raids will be posted in the channel they are invoked.",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed, delete_after=20)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_ex_channel(self, ctx):
        """
        Any EX-Raid that gets created will be automagically posted in this channel.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to post EX-Raids?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET default_exraid_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="EX-Raid Channel has been set.",
                              description="This is the chosen channel for posting EX-Raids!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_language(self, ctx):
        """
        This will change the language on most of the commands.
        You will be asked to click on one of the emojis once they all have shown up.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="Which language would you like?",
                              description="Wait for all reactions to appear!",
                              color=discord.Colour.dark_magenta())
        embed.set_footer(text="Please react with an Emoji below:")
        embed.set_thumbnail(url="https://www.unitedwebworks.com/hs-fs/hubfs/earth-gif.gif")
        flag_msg = await ctx.channel.send(embed=embed, delete_after=20)

        reactions_dict = {'🇺🇸': 'US',
                          '🇸🇪': 'SE',
                          '🇩🇪': 'DE',
                          '🇫🇷': 'FR',
                          '🇬🇷': 'GR',
                          '🇳🇱': 'NL',
                          '🇪🇸': 'ES'}

        for reaction in reactions_dict:
            await  flag_msg.add_reaction(reaction)

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.emoji in reactions_dict.keys() and reaction.message.id == flag_msg.id

        try:
            wait_for_reaction, wait_for_user = await self.bot.wait_for("reaction_add", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        embed = discord.Embed(title="Thank you!",
                              description=f"The language will be changed to: {reactions_dict[wait_for_reaction.emoji]} - {wait_for_reaction.emoji}",
                              color=discord.Colour.dark_magenta())
        await ctx.channel.send(embed=embed, delete_after=20)

        query = "UPDATE settings SET language = %s WHERE server_id = %s"
        params = (reactions_dict[wait_for_reaction.emoji], ctx.message.guild.id)
        await self.bot.db.execute(query, params)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_gmt(self, ctx):
        """
        Sets the GMT for your timezone so research-quests gets deleted on the correct time.
        You will be asked to enter a GMT, such as +1, 0, -1
        """
        await ctx.message.delete()

        embed = discord.Embed(title="What is your GMT?",
                              description="[(Greenwich Mean Time)](https://whatismytimezone.com/)\nUse the format ``+0`` or ``-0``",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://americanaddictioncenters.org/wp-content/uploads/2017/02/moving_clock_icon.gif")
        embed.set_footer(text="Type below:")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_message = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        if "+" in wait_for_message.content or "-" in wait_for_message.content:
            embed = discord.Embed(title="Thank you!",
                                  description=f"The GMT will be changed to: {wait_for_message.content}",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)

            query = "UPDATE settings SET timezone = %s WHERE server_id = %s"
            params = (wait_for_message.content, ctx.guild.id)
            await self.bot.db.execute(query, params)

        else:
            embed = discord.Embed(title="Error",
                                  description="You didn't use ``+`` or ``-``, please try again.",
                                  color=discord.Colour.dark_red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unset_log_channel(self, ctx):
        """
        The channel set with "set_log_channel" will become none.
        """
        await ctx.message.delete()

        query = "UPDATE settings SET log_channel_id = NULL WHERE server_id = %s"
        params = (ctx.message.guild.id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Log Channel has been unset.",
                              description="Logging is now Offline!",
                              color=discord.Colour.green())
        await ctx.channel.send(embed=embed, delete_after=20)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx):
        """
        Any Raid created / edited / deleted will be posted in this channel.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to post Logs?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://mbtskoudsalg.com/images/log-in-button-png-6.png")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET log_channel_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title="Log Channel has been set.",
                              description="This is the chosen channel for posting Logs!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

    @commands.command(aliases=['Set_event_overview', 'set-event-overview', 'Set-event-overview'])
    @commands.has_permissions(administrator=True)
    async def set_event_overview(self, ctx):
        """
        This will post a message that updates continuously with on-going / up-coming events.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to display events?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = discord.Embed(title="Events:",
                              color=discord.Colour.gold())
        embed.set_thumbnail(
            url="https://img15.deviantart.net/5a53/i/2016/277/8/f/pikachu_go_by_ry_spirit-dajx7us.png")
        embed.set_footer(text="Updates every hour.")
        embed.timestamp = datetime.datetime.utcnow()
        event_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET event_overview_channel_id = %s, event_overview_message_id = %s WHERE server_id = %s"
        params = (channel_id, event_msg.id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

    async def _init_update_event(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            log.info("Updating event overview")

            query = "SELECT * FROM settings WHERE event_overview_channel_id IS NOT NULL AND event_overview_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            url = 'https://raw.githubusercontent.com/ccev/pogoinfo/v2/active/events.json'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        json = await response.json(content_type='text/plain')
                    else:
                        return

            embed = discord.Embed(title="Events", color=discord.Colour.gold())
            embed.set_thumbnail(
                url="https://img15.deviantart.net/5a53/i/2016/277/8/f/pikachu_go_by_ry_spirit-dajx7us.png")
            embed.set_footer(text="Updates every hour | Last updated: ")
            embed.timestamp = datetime.datetime.utcnow()

            date_now = datetime.datetime.now()

            ongoing = []
            upcoming = []
            ended = []

            for event in json:
                date_format = '%Y-%m-%d %H:%M'

                date_start = datetime.datetime.strptime(event['start'], date_format)
                date_end = datetime.datetime.strptime(event['end'], date_format)

                # Ongoing events
                if date_start <= date_now:

                    # Time left of the event
                    date_remaining = (date_end - date_now)
                    hours_remaining = divmod(date_remaining.total_seconds(), 3600)[0]

                    if hours_remaining > 0:

                        # Duration of the event
                        date_duration = (date_end - date_start)
                        event['pretty-print-duration'] = await self.bot.get_cog("Utils").days_hours_minutes(
                            date_duration)
                        ongoing.append(event)

                    # Ended events
                    else:
                        ended.append(event)

                # Upcoming events
                else:

                    # Time until start
                    date_until = (date_start - date_now)
                    event['pretty-print-duration'] = await self.bot.get_cog("Utils").days_hours_minutes(date_until)

                    upcoming.append(event)

            # Sort by start date
            upcoming = sorted(upcoming, key=lambda k: k['start'])

            embed.add_field(name="🔓 **ONGOING**", value="\u200b", inline=False)
            for event in ongoing:
                days, hours, minutes = event["pretty-print-duration"]
                embed.add_field(name=f':small_orange_diamond: {event["name"]}',
                                value=f'**Time left:** {days} days, {hours} hours, {minutes} minutes\n**Starts:** {event["start"]}\n**Ends:** {event["end"]}\n\u200b',
                                inline=False)

            embed.add_field(name="🔒 **COMING** **UP** **NEXT**", value="\u200b", inline=False)
            for event in upcoming:
                days, hours, minutes = event["pretty-print-duration"]
                embed.add_field(name=f':small_orange_diamond: {event["name"]}',
                                value=f'**Time until start:** {days} days, {hours} hours\n**Starts:** {event["start"]}\n**Ends:** {event["end"]}\n\u200b',
                                inline=False)

            embed.add_field(name="**HAS** **ENDED**", value="\u200b", inline=False)
            for event in ended:
                embed.add_field(name=f':small_orange_diamond: {event["name"]}',
                                value=f'{event["start"]} - {event["end"]}\n\u200b',
                                inline=False)

            # Keep the length within the limits for the embed
            if len(embed.fields) > 25 or len(embed) > 6000:
                # Remove all fields above number 25, starting
                # from the bottom of "Coming up next" and moving up
                events_to_remove = len(embed.fields) - 25

                index_end = None
                for index, field in enumerate(embed.fields):
                    if field.name == '**HAS** **ENDED**':
                        index_end = index
                        break

                for i in range(1, events_to_remove):
                    embed.remove_field(index_end - i)

            for server in servers:
                channel_id = server[12]
                message_id = server[13]

                try:
                    await self.bot.http.edit_message(int(channel_id), int(message_id), embed=embed.to_dict())
                except discord.errors.NotFound:
                    pass
                except discord.errors.Forbidden:
                    pass

            await asyncio.sleep(86400)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_raid_overview(self, ctx):
        """
        This will post a message that updates continuously with on-going Raids.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to display raids?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        question_embed = await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        await wait_for_channel.delete()
        await question_embed.delete()

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = discord.Embed(title="Active Raids:",
                              color=discord.Colour.green())
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/raid_tut_group.png")
        embed.set_footer(text="Updates every 2nd minute.")
        embed.timestamp = datetime.datetime.utcnow()
        overview_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET raid_overview_channel_id = %s, raid_overview_message_id = %s WHERE server_id = %s"
        params = (channel_id, overview_msg.id, ctx.guild.id)
        await self.bot.db.execute(query, params)

    async def _init_update_raid_overview(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            query = "SELECT * FROM settings WHERE raid_overview_channel_id IS NOT NULL AND raid_overview_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            for server in servers:
                server_id = server[0]
                channel_id = server[10]
                message_id = server[11]

                query = "SELECT * FROM raids WHERE server_id = %s ORDER BY pokemon ASC, time"
                params = (server_id,)
                raids = await self.bot.db.execute(query, params)

                embed = discord.Embed(title="Active raids:", color=discord.Colour.dark_green())
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/raid_tut_group.png")
                embed.set_footer(text="Updates every 5th minute | Last updated: ")
                embed.timestamp = datetime.datetime.utcnow()

                if len(raids) > 0:
                    raid_dict = {}

                    for raid in raids:

                        pokemon = raid[5].title()
                        location = raid[7].title()
                        time = raid[6]

                        # URL to the raid-post
                        raid_url = f"https://discordapp.com/channels/{server_id}/{raid[1]}/{raid[2]}"

                        # Total amount of attending
                        attending = (len(raid[8].split(",")) - 1) + (len(raid[9].split(",")) - 1) + (
                                len(raid[10].split(",")) - 1) + int(raid[11])

                        # If it already exists, append value
                        if pokemon in raid_dict:
                            raid_dict[
                                pokemon] += f'➥ [{location}]({raid_url}) {time} :busts_in_silhouette: ({attending})\n'
                        else:  # create the key
                            raid_dict[
                                pokemon] = f'➥ [{location}]({raid_url}) {time} :busts_in_silhouette: ({attending})\n'

                    for key, value in raid_dict.items():

                        if len(value) > 6000:
                            embed.add_field(name="Warning",
                                            value=f":warning: Too many raids to display.\nThe limit is **6000**, you're at **{len(value)}**.\nPlease delete some old raids.")

                        elif len(value) >= 1024:

                            A = ""
                            B = ""
                            C = ""
                            D = ""
                            E = ""
                            F = ""

                            ABCDEF = [A, B, C, D, E, F]

                            value_list = value.split("\n")
                            value_list = value_list[:-1]
                            counter = 0

                            for val in value_list:

                                temp = ABCDEF[counter] + val + "\n"

                                if len(temp) <= 1024:
                                    ABCDEF[counter] += val + "\n"
                                else:
                                    counter += 1

                            key_fix = key
                            for letter in ABCDEF:
                                if len(letter) > 0:
                                    embed.add_field(name=key_fix, value=letter)
                                    key_fix = '\u200b'

                        else:
                            embed.add_field(name=key, value=value, inline=False)

                try:
                    await self.bot.http.edit_message(channel_id, message_id, embed=embed.to_dict())
                except discord.errors.NotFound:
                    query = "UPDATE settings SET raid_overview_channel_id = NULL, raid_overview_message_id = NULL WHERE server_id = %s"
                    params = (server_id,)
                    await self.bot.db.execute(query, params)
                except discord.errors.Forbidden:
                    pass
                except discord.errors.HTTPException:
                    pass

            await asyncio.sleep(300)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_ex_overview(self, ctx):
        """
        This will post a message that updates continuously with on-going Raids.
        You will be asked to tag a channel by using #.
        """
        await ctx.message.delete()

        embed = discord.Embed(title="In which channel would you like me to display EX-Raids?",
                              description="Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        question_embed = await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(ctx.channel)
            return

        await wait_for_channel.delete()
        await question_embed.delete()

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title="Error - No channel found",
                                  description="Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = discord.Embed(title="Active EX-Raids:",
                              color=discord.Colour.green())
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/raid_tut_group.png")
        embed.set_footer(text="Updates every hour.")
        embed.timestamp = datetime.datetime.utcnow()
        overview_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET exraid_overview_channel_id = %s, exraid_overview_message_id = %s WHERE server_id = %s"
        params = (channel_id, overview_msg.id, ctx.guild.id)
        await self.bot.db.execute(query, params)

    async def _init_update_ex_overview(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            query = "SELECT * FROM settings WHERE exraid_overview_channel_id IS NOT NULL AND exraid_overview_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            for server in servers:

                server_id = server[0]
                channel_id = server[14]
                message_id = server[15]

                query = "SELECT * FROM exraids WHERE server_id = %s ORDER BY pokemon ASC, time"
                params = (server_id,)
                raids = await self.bot.db.execute(query, params)

                embed = discord.Embed(title="Active EX-Raids:",
                                      color=discord.Colour.dark_green())
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/raid_tut_group.png")
                embed.set_footer(text="Updates every hour | Last updated: ")
                embed.timestamp = datetime.datetime.utcnow()

                if len(raids) > 0:
                    raid_dict = {}

                    for raid in raids:
                        pokemon = raid[5].title()
                        location = raid[8].title()
                        time = raid[6]
                        day = raid[7]

                        # URL to the raid-post
                        raid_url = f"https://discordapp.com/channels/{server_id}/{raid[1]}/{raid[2]}"

                        attending = (len(raid[9].split(",")) - 1) + (len(raid[10].split(",")) - 1) + (
                                len(raid[11].split(",")) - 1) + int(raid[12])

                        # If it already exists, append value
                        if pokemon in raid_dict:
                            raid_dict[
                                pokemon] += f'➥ [{location}]({raid_url}) {day} {time} :busts_in_silhouette: ({attending})\n'
                        else:  # create the key
                            raid_dict[
                                pokemon] = f'➥ [{location}]({raid_url}) {day} {time} :busts_in_silhouette: ({attending})\n'

                    for key, value in raid_dict.items():

                        if len(value) > 6000:
                            embed.add_field(name="Warning",
                                            value=f":warning: Too many raids to display.\nThe limit is **6000**, you're at **{len(value)}**.\nPlease delete some old raids.")

                        elif len(value) >= 1024:

                            A = ""
                            B = ""
                            C = ""
                            D = ""
                            E = ""
                            F = ""

                            ABCDEF = [A, B, C, D, E, F]

                            value_list = value.split("\n")
                            value_list = value_list[:-1]
                            counter = 0

                            for val in value_list:

                                temp = ABCDEF[counter] + val + "\n"

                                if len(temp) <= 1024:
                                    ABCDEF[counter] += val + "\n"
                                else:
                                    counter += 1

                            key_fix = key
                            for letter in ABCDEF:
                                if len(letter) > 0:
                                    embed.add_field(name=key_fix, value=letter)
                                    key_fix = '\u200b'

                        else:
                            embed.add_field(name=key, value=value, inline=False)

                try:
                    await self.bot.http.edit_message(int(channel_id), int(message_id), embed=embed.to_dict())
                except discord.errors.NotFound:
                    query = "UPDATE settings SET exraid_overview_channel_id = NULL, exraid_overview_message_id = NULL WHERE server_id = %s"
                    params = (server_id,)
                    await self.bot.db.execute(query, params)
                except discord.errors.Forbidden:
                    pass

            await asyncio.sleep(900)

    @commands.command(pass_context=True, hidden=True,
                      aliases=['Encounters', 'Encounter', 'encounter', 'Tasks', 'tasks'])
    @commands.has_permissions(administrator=True)
    async def encounters(self, ctx):
        """Retrieves all research tasks with encounters from Silphroad."""
        await ctx.message.delete()
        await ctx.message.channel.trigger_typing()

        async_session = AsyncHTMLSession()
        res = await async_session.get('https://thesilphroad.com/research-tasks')
        await res.html.arender()  # this call executes the js in the page
        items = res.html.find('.task-group')
        await async_session.close()

        my_tasks = []
        my_images = []

        for item in items:
            tasks = item.find('.taskText')
            images = item.find('.taskRewardsWrap')

            for task in tasks:
                my_tasks.append(task.text)

            for image in images:
                is_shiny = False
                if "shinyAvailable" in image.html:
                    is_shiny = True

                my_list = image.html.split("><")
                matching = [s for s in my_list if "https://assets.thesilphroad.com/img/pokemon/icons/" in s]
                my_images.append((matching, is_shiny))

        embed = discord.Embed(title="Research Tasks - Encounters", color=discord.Color.purple())
        description = ""
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/QuestIconProfessor.png")
        embed.set_footer(text="Updates once a day | ✨ = Chance of shiny | Last updated ")
        embed.timestamp = datetime.datetime.utcnow()

        for i in range(len(my_tasks)):
            try:

                if len(my_images[i][0]) < 1:
                    pass
                else:

                    mons = ""
                    for img in my_images[i][0]:
                        mon_id = img.split("/")[7].strip('.png"')
                        mon_id = "{:03d}".format(int(mon_id))
                        mon_name = await self.bot.get_cog("Utils").get_pokemon_name(str(mon_id))

                        if my_images[i][1] is True:
                            mons += "✨" + mon_name + " "
                        else:
                            mons += mon_name + " "

                    description += f'**{my_tasks[i]}**\n{mons}\n\n'

            except:
                # Mons without images / not in the "encounter"-session
                pass

        embed.description = description

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def install(self, ctx):
        """Uploads necessary emojis to the server in order to work correctly."""
        await ctx.message.delete()

        embed = discord.Embed(title="Installing..",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://cdn-images-1.medium.com/max/1600/1*LruTBJfGS0SDPrR9icfrMw.gif")
        install_msg = await ctx.channel.send(embed=embed)

        for emoji in ctx.guild.emojis:
            if emoji.name == 'valor' or emoji.name == 'Valor' or emoji.name == "instinct" or emoji.name == "Instinct" or emoji.name == "mystic" or emoji.name == "Mystic":
                try:
                    await emoji.delete(reason="Delibot Re-install")
                except discord.Forbidden:
                    embed = discord.Embed(title="Error - Insufficient permissions",
                                          description="Edit my role and enable 'Manage Emojis'",
                                          color=discord.Colour.dark_red())
                    await ctx.channel.send(embed=embed)
                    return

        await self.upload_emojis(ctx)

        embed = discord.Embed(title="Successfully installed!",
                              color=discord.Colour.dark_magenta())
        await install_msg.edit(embed=embed)

    @staticmethod
    async def upload_emojis(ctx):
        with open("images/mystic.png", "rb") as image:
            image_byte = image.read()
            await ctx.guild.create_custom_emoji(name="mystic",
                                                image=image_byte,
                                                reason="Installing mystic-emoji")
            await asyncio.sleep(5)

        with open("images/valor.png", "rb") as image:
            image_byte = image.read()
            await ctx.guild.create_custom_emoji(name="valor",
                                                image=image_byte,
                                                reason="Installing valor-emoji")
            await asyncio.sleep(5)

        with open("images/instinct.png", "rb") as image:
            image_byte = image.read()
            await ctx.guild.create_custom_emoji(name="instinct",
                                                image=image_byte,
                                                reason="Installing instinct-emoji")
            await asyncio.sleep(5)

    @staticmethod
    async def timeout_error_msg(channel):
        embed = discord.Embed(title="Timeout",
                              description="You took too long to respond, please try again.",
                              color=discord.Colour.dark_magenta())
        await channel.send(embed=embed, delete_after=20)


def setup(bot):
    bot.add_cog(Admin(bot))
