import asyncio
import datetime
import logging
from utils import default
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

        embed = discord.Embed(title=f"Permission role has been unset.",
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

        embed = discord.Embed(title=f"What role would you like to give permission to edit/delete raids & add gyms?",
                              description=f"Please tag the role below by using @",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed)

        def check(message):
            return ctx.author.id == message.author.id

        wait_for_role = await self.bot.wait_for("message", timeout=30.0, check=check)

        if wait_for_role is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET role_permission = %s WHERE server_id = %s"
        params = (wait_for_role.content[3:-1], ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        embed = discord.Embed(title=f"Permission role has been set.",
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

        embed = discord.Embed(title=f"EX-Pass Scanning Channel has been unset.",
                              description=f"EX-Pass Scanning is now offline!",
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

        embed = discord.Embed(title=f"In which channel would you like me to scan for EX-Pass screenshots?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(m):
            return m.author.id == ctx.message.author.id

        channel = await self.bot.wait_for("message", timeout=20.0, check=check)

        if channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET exraid_channel_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.guild.get_channel(int(channel_id))
        embed = discord.Embed(title=f"EX-Pass Scanning has been set.",
                              description=f"This is the chosen channel for scanning EX-Pass screenshots!",
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

        embed = discord.Embed(title=f"Profile Scanning Channel has been unset.",
                              description=f"Profile Scanning is now offline!",
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

        embed = discord.Embed(title=f"In which channel would you like me to assign teams?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET profile_channel_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.guild.get_channel(int(channel_id))
        embed = discord.Embed(title=f"Profile Scanning has been set.",
                              description=f"This is the chosen channel for auto-assigning teams!",
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

        embed = discord.Embed(title=f"Raid Channel has been unset.",
                              description=f"Raids will be posted in the channel they are invoked.",
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

        embed = discord.Embed(title=f"In which channel would you like me to post Raids?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET default_raid_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title=f"Raid Channel has been set.",
                              description=f"This is the chosen channel for posting Raids!",
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

        embed = discord.Embed(title=f"EX-Raid Channel has been unset.",
                              description=f"EX-Raids will be posted in the channel they are invoked.",
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

        embed = discord.Embed(title=f"In which channel would you like me to post EX-Raids?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://media.pokemoncentral.it/wiki/3/3f/Sprxymsh225.gif")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET default_exraid_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title=f"EX-Raid Channel has been set.",
                              description=f"This is the chosen channel for posting EX-Raids!",
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

        embed = discord.Embed(title=f"Which language would you like?", description=f"Wait for all reactions to appear!",
                              color=discord.Colour.dark_magenta())
        embed.set_footer(text="Please react with an Emoji below:")
        embed.set_thumbnail(url="https://www.unitedwebworks.com/hs-fs/hubfs/earth-gif.gif")
        flag_msg = await ctx.channel.send(embed=embed, delete_after=20)

        reactions_dict = {'🇺🇸': 'US', '🇸🇪': 'SE', '🇩🇪': 'DE', '🇫🇷': 'FR', '🇬🇷': 'GR', '🇳🇱': 'NL'}

        for reaction in reactions_dict:
            await  flag_msg.add_reaction(reaction)

        def check(reaction, user):
            return user.id == ctx.author.id and reaction.emoji in reactions_dict.keys() and reaction.message.id == flag_msg.id

        wait_for_reaction, wait_for_user = await self.bot.wait_for("reaction_add", timeout=20.0, check=check)

        if wait_for_reaction is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        embed = discord.Embed(title=f"Thank you!",
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

        embed = discord.Embed(title=f"What is your GMT?",
                              description=f"[(Greenwich Mean Time)](https://whatismytimezone.com/)\nUse the format ``+0`` or ``-0``",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://americanaddictioncenters.org/wp-content/uploads/2017/02/moving_clock_icon.gif")
        embed.set_footer(text="Type below:")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_message = await self.bot.wait_for("message", timeout=20.0, check=check)

        if wait_for_message is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        if "+" in wait_for_message.content or "-" in wait_for_message.content:
            embed = discord.Embed(title=f"Thank you!",
                                  description=f"The GMT will be changed to: {wait_for_message.content}",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)

            query = "UPDATE settings SET timezone = %s WHERE server_id = %s"
            params = (wait_for_message.content, ctx.guild.id)
            await self.bot.db.execute(query, params)

        else:
            embed = discord.Embed(title=f"Error",
                                  description=f"You didn't use ``+`` or ``-``, please try again.",
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

        embed = discord.Embed(title=f"Log Channel has been unset.",
                              description=f"Logging is now Offline!",
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

        embed = discord.Embed(title=f"In which channel would you like me to post Logs?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://mbtskoudsalg.com/images/log-in-button-png-6.png")
        await ctx.channel.send(embed=embed, delete_after=20)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        query = "UPDATE settings SET log_channel_id = %s WHERE server_id = %s"
        params = (channel_id, ctx.message.guild.id)
        await self.bot.db.execute(query, params)

        channel = ctx.message.guild.get_channel(int(channel_id))
        embed = discord.Embed(title=f"Log Channel has been set.",
                              description=f"This is the chosen channel for posting Logs!",
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

        embed = discord.Embed(title=f"In which channel would you like me to display events?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = discord.Embed(title=f"Events:",
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

            query = "SELECT * FROM settings WHERE event_overview_channel_id != %s AND event_overview_message_id != %s"
            params = ('', '')
            servers = await self.bot.db.execute(query, params)

            log.info("Updating events")

            asession = AsyncHTMLSession()
            res = await asession.get('https://thesilphroad.com/')
            await res.html.arender(wait=5.0, sleep=2.0)  # this call executes the js in the page
            items = res.html.find('.timeline-item')
            await asession.close()

            events = []
            # For each event-div
            for item in items:
                # Add the contents to a list
                rows = item.text.split("\n")
                events.append(f'{rows[2]}|{rows[0]}|{rows[3]}|{rows[1]}')

            for server in servers:
                server_id = server[0]
                channel_id = server[12]
                message_id = server[13]

                embed = discord.Embed(title=f"Events:",
                                      color=discord.Colour.gold())
                embed.set_thumbnail(
                    url="https://img15.deviantart.net/5a53/i/2016/277/8/f/pikachu_go_by_ry_spirit-dajx7us.png")
                embed.set_footer(text="Updates every hour | Last updated: ")
                embed.timestamp = datetime.datetime.utcnow()

                embed.add_field(name="**HAPPENING** **NOW** 🔓", value="\u200b", inline=False)
                once = True
                for event in events:
                    event = event.split("|")

                    if "left" not in event[1] and once is True:
                        embed.add_field(name="**COMING** **UP** **NEXT** 🔒", value="\u200b", inline=False)
                        once = False

                    embed.add_field(name=f"🔸 **{event[0]}** \n{event[3]}",
                                    value=f"**Time:** {event[1]}\n**Description:** {event[2]}\n\u200b", inline=False)
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

        embed = discord.Embed(title=f"In which channel would you like me to display raids?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        question_embed = await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        await wait_for_channel.delete()
        await question_embed.delete()

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = discord.Embed(title=f"Active Raids:",
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

            query = "SELECT * FROM settings WHERE raid_overview_channel_id != %s AND raid_overview_message_id != %s"
            params = ('', '')
            servers = await self.bot.db.execute(query, params)

            for server in servers:
                server_id = server[0]
                channel_id = server[10]
                message_id = server[11]

                query = "SELECT * FROM raids WHERE server_id = %s ORDER BY pokemon ASC, time"
                params = (server_id,)
                raids = await self.bot.db.execute(query, params)

                embed = discord.Embed(title=f"Active raids:", color=discord.Colour.dark_green())
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
                    pass
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

        embed = discord.Embed(title=f"In which channel would you like me to display EX-Raids?",
                              description=f"Please tag the channel below by using #",
                              color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://img.icons8.com/metro/1600/list.png")
        question_embed = await ctx.channel.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        wait_for_channel = await self.bot.wait_for("message", timeout=20.0, check=check)
        await wait_for_channel.delete()
        await question_embed.delete()

        if wait_for_channel is None:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_magenta())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel_id = wait_for_channel.content[2:-1]

        if not channel_id.isdigit():
            embed = discord.Embed(title=f"Error - No channel found",
                                  description=f"Please ONLY tag the channel and nothing else, like: #general",
                                  color=discord.Colour.red())
            await ctx.channel.send(embed=embed, delete_after=20)
            return

        channel = ctx.guild.get_channel(int(channel_id))

        embed = discord.Embed(title=f"Active EX-Raids:",
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

            query = "SELECT * FROM settings WHERE exraid_overview_channel_id != %s AND exraid_overview_message_id != %s"
            params = ('', '')
            servers = await self.bot.db.execute(query, params)

            for server in servers:

                server_id = server[0]
                channel_id = server[14]
                message_id = server[15]

                query = "SELECT * FROM exraids WHERE server_id = %s ORDER BY pokemon ASC, time"
                params = (server_id,)
                raids = await self.bot.db.execute(query, params)

                embed = discord.Embed(title=f"Active EX-Raids:",
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
                    pass
                except discord.errors.Forbidden:
                    pass

            await asyncio.sleep(900)

    @commands.command(pass_context=True, hidden=True,
                      aliases=['Encounters', 'Encounter', 'encounter', 'Tasks', 'tasks'])
    @commands.has_permissions(administrator=True)
    async def encounters(self, ctx):
        """
        In development.
        """
        await ctx.message.delete()
        await ctx.message.channel.trigger_typing()

        asession = AsyncHTMLSession()
        res = await asession.get('https://thesilphroad.com/research-tasks')
        await res.html.arender()  # this call executes the js in the page
        items = res.html.find('.task-group')
        await asession.close()

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
        """
        Uploads necessary emojis to the server in order to work correctly.
        """
        # Delete command
        await ctx.message.delete()

        embed = discord.Embed(title=f"Installing..", color=discord.Colour.dark_magenta())
        embed.set_thumbnail(url="https://cdn-images-1.medium.com/max/1600/1*LruTBJfGS0SDPrR9icfrMw.gif")
        install_msg = await ctx.channel.send(embed=embed)

        for emoji in ctx.guild.emojis:
            if emoji.name == 'valor' or emoji.name == 'Valor' or emoji.name == "instinct" or emoji.name == "Instinct" or emoji.name == "mystic" or emoji.name == "Mystic":
                try:
                    await emoji.delete(reason="Delibot Re-install")
                except discord.Forbidden:
                    embed = discord.Embed(title=f"Error - Insufficient permissions",
                                          description=f"Edit my role and enable 'Manage Emojis'",
                                          color=discord.Colour.dark_red())
                    await ctx.channel.send(embed=embed)
                    return

        await self.upload_emojis(ctx)

        embed = discord.Embed(title=f"Successfully installed!", color=discord.Colour.dark_magenta())
        await install_msg.edit(embed=embed)

    @staticmethod
    async def upload_emojis(ctx):
        with open("images/mystic.png", "rb") as image:
            image_byte = image.read()
            await ctx.guild.create_custom_emoji(name="mystic", image=image_byte, reason="Installing mystic-emoji")
            await asyncio.sleep(5)

        with open("images/valor.png", "rb") as image:
            image_byte = image.read()
            await ctx.guild.create_custom_emoji(name="valor", image=image_byte, reason="Installing valor-emoji")
            await asyncio.sleep(5)

        with open("images/instinct.png", "rb") as image:
            image_byte = image.read()
            await ctx.guild.create_custom_emoji(name="instinct", image=image_byte, reason="Installing instinct-emoji")
            await asyncio.sleep(5)


def setup(bot):
    bot.add_cog(Admin(bot))
