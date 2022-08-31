import asyncio
import datetime
import logging
from pathlib import Path

import aiohttp
import discord
from discord import app_commands, utils
from discord.ext import commands

log = logging.getLogger()


class Admin(commands.Cog):
    """
    Commands for the Server Owner / Admins
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.loop.create_task(self._init_update_raid_overview())
        self.bot.loop.create_task(self._init_update_ex_overview())
        self.bot.loop.create_task(self._init_update_event())
        self.bot.loop.create_task(self._init_update_community_day())

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_community_day(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        This will post a message that updates continuously with on-going / up-coming community days.
        """
        embed = await self.bot.get_cog("Community").get_embed_community_day(self, interaction.guild_id)
        embed.set_footer(text="Updates every day.")
        embed.timestamp = utils.utcnow()
        event_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET community_day_channel_id = %s, community_day_message_id = %s WHERE server_id = %s"
        params = (channel.id, event_msg.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    async def _init_update_community_day(self):
        while not self.bot.is_closed():
            query = "SELECT * FROM settings WHERE community_day_channel_id IS NOT NULL AND community_day_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            log.info(f'Updating community day for {len(servers)} servers.')

            for server in servers:
                server_id = server[0]
                channel_id = server[16]
                message_id = server[17]

                embed = await self.bot.get_cog("Community").get_embed_community_day(self, server_id)
                embed.set_footer(text="Updates every day | Last updated: ")
                embed.timestamp = utils.utcnow()

                try:
                    channel = self.bot.get_partial_messageable(id=int(channel_id), guild_id=int(server_id))
                    message = discord.PartialMessage(channel=channel, id=int(message_id))
                    await message.edit(embed=embed)
                except:
                    query = "UPDATE settings SET community_day_channel_id = NULL, community_day_message_id = NULL WHERE server_id = %s"
                    params = (server_id,)
                    await self.bot.db.execute(query, params)

            log.info(f'Finished updating community day for {len(servers)} servers. Sleeping for 24 hours.')
            await asyncio.sleep(86400)

    @app_commands.command()
    @app_commands.default_permissions()
    async def unset_role_permission(self, interaction: discord.Interaction):
        """
        The role set with "set_role_permission" will become none.
        """
        query = "UPDATE settings SET role_permission = NULL WHERE server_id = %s"
        params = (interaction.guild_id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Permission role has been unset.",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_role_permission(self, interaction: discord.Interaction, role: discord.Role):
        """
        The role will be granted permissions to edit and delete any Raid and also use create/delete gym.
        """
        query = "UPDATE settings SET role_permission = %s WHERE server_id = %s"
        params = (role.id, interaction.guild_id)

        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Permission role has been set.",
                              description=f"{role.name} is the chosen role for additional permissions.",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed, delete_after=20)

        await interaction.response.send_message(f'{role.mention} has been set.', ephemeral=True)

    @app_commands.command()
    @app_commands.default_permissions()
    async def unset_ex_scan(self, interaction: discord.Interaction):
        """
        The channel set with "set_ex_scan" will become none.
        """
        query = "UPDATE settings SET exraid_channel_id = NULL WHERE server_id = %s"
        params = (interaction.guild_id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="EX-Pass Scanning Channel has been unset.",
                              description="EX-Pass Scanning is now offline!",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_ex_scan(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        The channel will be continuously checked for EX-Raid-pass images and create EX-raids based on the text on the image.
        You will be asked to tag a channel by using #.
        """

        query = "UPDATE settings SET exraid_channel_id = %s WHERE server_id = %s"
        params = (channel.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="EX-Pass Scanning has been set.",
                              description="This is the chosen channel for scanning EX-Pass screenshots!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

    @app_commands.command()
    @app_commands.default_permissions()
    async def unset_profile_scan(self, interaction: discord.Interaction):
        """
        The channel set with "set_profile_scan" will become none.
        """
        query = "UPDATE settings SET profile_channel_id = NULL WHERE server_id = %s"
        params = (interaction.guild_id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Profile Scanning Channel has been unset.",
                              description="Profile Scanning is now offline!",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed, delete_after=20)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_profile_scan(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        The channel will be continuously checked for Team images and give the player that posts an image a role based on their color.
        """

        query = "UPDATE settings SET profile_channel_id = %s WHERE server_id = %s"
        params = (channel.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Profile Scanning has been set.",
                              description="This is the chosen channel for auto-assigning teams!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    @app_commands.command()
    @app_commands.default_permissions()
    async def unset_raid_channel(self, interaction: discord.Interaction):
        """
        The channel set with "set_raid_channel" will become none.
        """
        query = "UPDATE settings SET default_raid_id = NULL WHERE server_id = %s"
        params = (interaction.guild_id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Raid Channel has been unset.",
                              description="Raids will be posted in the channel they are invoked.",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed, delete_after=20)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_raid_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Any Raid that gets created will be automagically posted in this channel.
        """

        query = "UPDATE settings SET default_raid_id = %s WHERE server_id = %s"
        params = (channel.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Raid Channel has been set.",
                              description="This is the chosen channel for posting Raids!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    @app_commands.command()
    @app_commands.default_permissions()
    async def unset_ex_channel(self, interaction: discord.Interaction):
        """
        The channel set with "set_ex_channel" will become none.
        """
        query = "UPDATE settings SET default_exraid_id = NULL WHERE server_id = %s"
        params = (interaction.guild_id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="EX-Raid Channel has been unset.",
                              description="EX-Raids will be posted in the channel they are invoked.",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed, delete_after=20)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_ex_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Any EX-Raid that gets created will be automagically posted in this channel.
        """

        query = "UPDATE settings SET default_exraid_id = %s WHERE server_id = %s"
        params = (channel.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="EX-Raid Channel has been set.",
                              description="This is the chosen channel for posting EX-Raids!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_language(self, interaction: discord.Interaction):
        """
        This will change the language on most of the commands.
        You will be asked to click on one of the emojis once they all have shown up.
        """
        embed = discord.Embed(title="Which language would you like?",
                              description="Wait for all reactions to appear!",
                              color=discord.Colour.dark_magenta())
        embed.set_footer(text="Please react with an Emoji below:")
        embed.set_thumbnail(url="https://www.unitedwebworks.com/hs-fs/hubfs/earth-gif.gif")
        flag_msg = await interaction.channel.send(embed=embed, delete_after=20)

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
            return user.id == interaction.user.id and reaction.emoji in reactions_dict.keys() and reaction.message.id == flag_msg.id

        try:
            wait_for_reaction, wait_for_user = await self.bot.wait_for("reaction_add", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(interaction.channel)
            return

        embed = discord.Embed(title="Thank you!",
                              description=f"The language will be changed to: {reactions_dict[wait_for_reaction.emoji]} - {wait_for_reaction.emoji}",
                              color=discord.Colour.dark_magenta())
        await interaction.channel.send(embed=embed, delete_after=20)

        query = "UPDATE settings SET language = %s WHERE server_id = %s"
        params = (reactions_dict[wait_for_reaction.emoji], interaction.guild_id)
        await self.bot.db.execute(query, params)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_gmt(self, interaction: discord.Interaction):
        """
        Sets the GMT for your timezone so research-quests gets deleted on the correct time.
        You will be asked to enter a GMT, such as +1, 0, -1
        """
        embed = discord.Embed(title="What is your GMT?",
                              description="[(Greenwich Mean Time)](https://whatismytimezone.com/)\nUse the format ``+0`` or ``-0``",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://americanaddictioncenters.org/wp-content/uploads/2017/02/moving_clock_icon.gif")
        embed.set_footer(text="Type below:")
        await interaction.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == interaction.user.id

        try:
            wait_for_message = await self.bot.wait_for("message", timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await self.timeout_error_msg(interaction.channel)
            return

        if "+" in wait_for_message.content or "-" in wait_for_message.content:
            embed = discord.Embed(title="Thank you!",
                                  description=f"The GMT will be changed to: {wait_for_message.content}",
                                  color=discord.Colour.dark_magenta())
            await interaction.channel.send(embed=embed, delete_after=20)

            query = "UPDATE settings SET timezone = %s WHERE server_id = %s"
            params = (wait_for_message.content, interaction.guild_id)
            await self.bot.db.execute(query, params)

        else:
            embed = discord.Embed(title="Error",
                                  description="You didn't use ``+`` or ``-``, please try again.",
                                  color=discord.Colour.dark_red())
            await interaction.channel.send(embed=embed, delete_after=20)
            return

    @app_commands.command()
    @app_commands.default_permissions()
    async def unset_log_channel(self, interaction: discord.Interaction):
        """
        The channel set with "set_log_channel" will become none.
        """
        query = "UPDATE settings SET log_channel_id = NULL WHERE server_id = %s"
        params = (interaction.guild_id,)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Log Channel has been unset.",
                              description="Logging is now Offline!",
                              color=discord.Colour.green())
        await interaction.channel.send(embed=embed, delete_after=20)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Any Raid created / edited / deleted will be posted in this channel.
        """

        query = "UPDATE settings SET log_channel_id = %s WHERE server_id = %s"
        params = (channel.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title="Log Channel has been set.",
                              description="This is the chosen channel for posting Logs!",
                              color=discord.Colour.green())
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_event_overview(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        This will post a message that updates continuously with on-going / up-coming events.
        """

        embed = discord.Embed(title="Events:", color=discord.Colour.gold())
        embed.set_thumbnail(
            url="https://img15.deviantart.net/5a53/i/2016/277/8/f/pikachu_go_by_ry_spirit-dajx7us.png")
        embed.set_footer(text="Updates every hour.")
        embed.timestamp = utils.utcnow()
        event_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET event_overview_channel_id = %s, event_overview_message_id = %s WHERE server_id = %s"
        params = (channel.id, event_msg.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    async def _init_update_event(self):
        while not self.bot.is_closed():
            query = "SELECT * FROM settings WHERE event_overview_channel_id IS NOT NULL AND event_overview_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            log.info(f'Updating event overview for {len(servers)} servers.')

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
            embed.timestamp = utils.utcnow()

            date_now = datetime.datetime.now()

            ongoing = []
            upcoming = []
            ended = []

            for event in json:
                date_format = '%Y-%m-%d %H:%M'

                if event['start'] is not None:
                    date_start = datetime.datetime.strptime(event['start'], date_format)
                    date_end = datetime.datetime.strptime(event['end'], date_format)

                    # Ongoing events
                    if date_start <= date_now:

                        # Time left of the event
                        date_remaining = (date_end - date_now)
                        hours_remaining = divmod(date_remaining.total_seconds(), 3600)[0]

                        if hours_remaining > 0:

                            # Duration of the event
                            date_duration = (date_end - date_now)
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
                server_id = server[11]
                channel_id = server[12]
                message_id = server[13]

                try:
                    channel = self.bot.get_partial_messageable(id=int(channel_id), guild_id=int(server_id))
                    message = discord.PartialMessage(channel=channel, id=int(message_id))
                    await message.edit(embed=embed)
                except discord.errors.Forbidden:
                    pass
                except discord.errors.HTTPException:
                    pass
                except TypeError:
                    pass

            log.info(f'Finished updating event overview for {len(servers)} servers. Sleeping for 1 hour.')
            await asyncio.sleep(3600)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_raid_overview(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        This will post a message that updates continuously with on-going Raids.
        """
        embed = discord.Embed(title="Active Raids:",
                              color=discord.Colour.green())
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/raid_tut_group.png")
        embed.set_footer(text="Updates every 2nd minute.")
        embed.timestamp = utils.utcnow()
        overview_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET raid_overview_channel_id = %s, raid_overview_message_id = %s WHERE server_id = %s"
        params = (channel.id, overview_msg.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    async def _init_update_raid_overview(self):
        while not self.bot.is_closed():
            query = "SELECT * FROM settings WHERE raid_overview_channel_id IS NOT NULL AND raid_overview_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            log.info(f'Updating raid overview for {len(servers)} servers.')

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
                embed.timestamp = utils.utcnow()

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
                    channel = self.bot.get_partial_messageable(id=int(channel_id), guild_id=int(server_id))
                    message = discord.PartialMessage(channel=channel, id=int(message_id))
                    await message.edit(embed=embed)
                except:
                    query = "UPDATE settings SET raid_overview_channel_id = NULL, raid_overview_message_id = NULL WHERE server_id = %s"
                    params = (server_id,)
                    await self.bot.db.execute(query, params)

            log.info(f'Finished updating raid overview for {len(servers)} servers. Sleeping for 5 minutes.')
            await asyncio.sleep(300)

    @app_commands.command()
    @app_commands.default_permissions()
    async def set_ex_overview(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        This will post a message that updates continuously with on-going Raids.
        """
        embed = discord.Embed(title="Active EX-Raids:",
                              color=discord.Colour.green())
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/raid_tut_group.png")
        embed.set_footer(text="Updates every hour.")
        embed.timestamp = utils.utcnow()
        overview_msg = await channel.send(embed=embed)

        query = "UPDATE settings SET exraid_overview_channel_id = %s, exraid_overview_message_id = %s WHERE server_id = %s"
        params = (channel.id, overview_msg.id, interaction.guild_id)
        await self.bot.db.execute(query, params)

        await interaction.response.send_message(f'Created in {channel.mention}', ephemeral=True)

    async def _init_update_ex_overview(self):
        while not self.bot.is_closed():
            query = "SELECT * FROM settings WHERE exraid_overview_channel_id IS NOT NULL AND exraid_overview_message_id IS NOT NULL"
            servers = await self.bot.db.execute(query)

            log.info(f'Updating ex overview for {len(servers)} servers.')

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
                embed.timestamp = utils.utcnow()

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
                    channel = self.bot.get_partial_messageable(id=int(channel_id), guild_id=int(server_id))
                    message = discord.PartialMessage(channel=channel, id=int(message_id))
                    await message.edit(embed=embed)
                except:
                    query = "UPDATE settings SET exraid_overview_channel_id = NULL, exraid_overview_message_id = NULL WHERE server_id = %s"
                    params = (server_id,)
                    await self.bot.db.execute(query, params)

            log.info(f'Finished updating ex overview for {len(servers)} servers. Sleeping for 15 minutes.')
            await asyncio.sleep(900)

    # @commands.command(pass_context=True, hidden=True,
    #                   aliases=['Encounters', 'Encounter', 'encounter', 'Tasks', 'tasks'])
    # @commands.has_permissions(administrator=True)
    # async def encounters(self, ctx):
    #     """Retrieves all research tasks with encounters from Silphroad."""
    #     
    #     await ctx.message.channel.trigger_typing()
    #
    #     async_session = AsyncHTMLSession()
    #     res = await async_session.get('https://thesilphroad.com/research-tasks')
    #     await res.html.arender()  # this call executes the js in the page
    #     items = res.html.find('.task-group')
    #     await async_session.close()
    #
    #     my_tasks = []
    #     my_images = []
    #
    #     for item in items:
    #         tasks = item.find('.taskText')
    #         images = item.find('.taskRewardsWrap')
    #
    #         for task in tasks:
    #             my_tasks.append(task.text)
    #
    #         for image in images:
    #             is_shiny = False
    #             if "shinyAvailable" in image.html:
    #                 is_shiny = True
    #
    #             my_list = image.html.split("><")
    #             matching = [s for s in my_list if "https://assets.thesilphroad.com/img/pokemon/icons/" in s]
    #             my_images.append((matching, is_shiny))
    #
    #     embed = discord.Embed(title="Research Tasks - Encounters", color=discord.Color.purple())
    #     description = ""
    #     embed.set_thumbnail(
    #         url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/QuestIconProfessor.png")
    #     embed.set_footer(text="Updates once a day | ✨ = Chance of shiny | Last updated ")
    #     embed.timestamp = utils.utcnow()
    #
    #     for i in range(len(my_tasks)):
    #         try:
    #
    #             if len(my_images[i][0]) < 1:
    #                 pass
    #             else:
    #
    #                 mons = ""
    #                 for img in my_images[i][0]:
    #                     mon_id = img.split("/")[7].strip('.png"')
    #                     mon_id = "{:03d}".format(int(mon_id))
    #                     mon_name = await self.bot.get_cog("Utils").get_pokemon_name(str(mon_id))
    #
    #                     if my_images[i][1] is True:
    #                         mons += "✨" + mon_name + " "
    #                     else:
    #                         mons += mon_name + " "
    #
    #                 description += f'**{my_tasks[i]}**\n{mons}\n\n'
    #
    #         except:
    #             # Mons without images / not in the "encounter"-session
    #             pass
    #
    #     embed.description = description
    #
    #     await ctx.send(embed=embed)

    @app_commands.command()
    @app_commands.default_permissions()
    async def install(self, interaction: discord.Interaction):
        """Uploads necessary emojis to the server in order to work correctly."""

        embed = discord.Embed(title="Installing..",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://cdn-images-1.medium.com/max/1600/1*LruTBJfGS0SDPrR9icfrMw.gif")
        install_msg = await interaction.channel.send(embed=embed)

        for emoji in interaction.guild.emojis:
            if emoji.name == 'valor' or emoji.name == 'Valor' or emoji.name == "instinct" or emoji.name == "Instinct" or emoji.name == "mystic" or emoji.name == "Mystic":
                try:
                    await emoji.delete(reason="Delibot Re-install")
                except discord.Forbidden:
                    embed = discord.Embed(title="Error - Insufficient permissions",
                                          description="Edit my role and enable 'Manage Emojis'",
                                          color=discord.Colour.dark_red())
                    await interaction.channel.send(embed=embed)
                    return

        await self.upload_emojis(interaction)

        embed = discord.Embed(title="Successfully installed!",
                              color=discord.Colour.dark_magenta())
        await install_msg.edit(embed=embed)

    @staticmethod
    async def upload_emojis(interaction):
        with open(Path("images/mystic.png"), "rb") as image:
            image_byte = image.read()
            await interaction.guild.create_custom_emoji(name="mystic",
                                                        image=image_byte,
                                                        reason="Installing mystic-emoji")
            await asyncio.sleep(5)

        with open(Path("images/valor.png"), "rb") as image:
            image_byte = image.read()
            await interaction.guild.create_custom_emoji(name="valor",
                                                        image=image_byte,
                                                        reason="Installing valor-emoji")
            await asyncio.sleep(5)

        with open(Path("images/instinct.png"), "rb") as image:
            image_byte = image.read()
            await interaction.guild.create_custom_emoji(name="instinct",
                                                        image=image_byte,
                                                        reason="Installing instinct-emoji")
            await asyncio.sleep(5)

    @staticmethod
    async def timeout_error_msg(channel):
        embed = discord.Embed(title="Timeout",
                              description="You took too long to respond, please try again.",
                              color=discord.Colour.dark_magenta())
        await channel.send(embed=embed, delete_after=20)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
