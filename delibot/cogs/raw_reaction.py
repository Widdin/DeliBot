import asyncio
import datetime

import discord
from discord.ext import commands


class RawReaction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.bot.wait_until_ready()

        # If it's the bot, return
        if payload.user_id == self.bot.user.id:
            return

        guild_id = payload.guild_id
        channel_id = payload.channel_id
        user_id = payload.user_id
        message_id = payload.message_id
        emoji_name = payload.emoji.name.lower()

        if emoji_name in ['valor', 'mystic', 'instinct', '1⃣', '2⃣', '3⃣']:
            server = self.bot.get_guild(guild_id)
            if server is not None:
                await self.append_user(guild_id, channel_id, message_id, user_id, emoji_name)
                await self.update_raid(guild_id, channel_id, message_id)

        elif emoji_name == '📝':
            member = self.bot.get_guild(guild_id).get_member(user_id)
            if await self.is_author(guild_id, channel_id, message_id,
                                    user_id) is True or member.guild_permissions.administrator is True or await self.permission_role_or_admin(
                guild_id, member):
                await self.edit_raid(guild_id, channel_id, message_id, member)

        elif emoji_name == '❌':
            member = self.bot.get_guild(guild_id).get_member(user_id)
            if await self.is_author(guild_id, channel_id, message_id,
                                    user_id) is True or member.guild_permissions.administrator is True or await self.permission_role_or_admin(
                guild_id, member):
                await self.delete_raid(guild_id, channel_id, message_id, member)

        elif emoji_name == '⚔':
            member = self.bot.get_guild(guild_id).get_member(user_id)
            await self.bot.get_cog("Pokebattler").pb_information(member, guild_id, channel_id, message_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.bot.wait_until_ready()

        # If it's the bot, return
        if payload.user_id == self.bot.user.id:
            return

        guild_id = payload.guild_id
        channel_id = payload.channel_id
        user_id = payload.user_id
        message_id = payload.message_id
        emoji_name = payload.emoji.name.lower()

        if emoji_name in ['valor', 'mystic', 'instinct', '1⃣', '2⃣', '3⃣']:
            server = self.bot.get_guild(guild_id)
            if server is not None:
                await self.pop_user(guild_id, channel_id, message_id, user_id, emoji_name)
                await self.update_raid(guild_id, channel_id, message_id)

    async def edit_raid(self, guild_id: str, channel_id: str, message_id: str, member: discord.Member):
        query = "SELECT * FROM raids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        params = (guild_id, channel_id, message_id)
        response = await self.bot.db.execute(query, params)

        exraid = False
        if len(response) == 0:
            query = "SELECT * FROM exraids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
            params = (guild_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params)
            exraid = True

            if len(response) == 0:
                return

        # Retrieve translation from JSON.
        edit_question, edit_type, thank_you, raid_time, raid_location, raid_day = await self.bot.get_cog(
            "Utils").get_translation(guild_id, "EDIT_QUESTION EDIT_TYPE THANK_YOU RAID_TIME RAID_LOCATION RAID_DAY")

        keys = {'1⃣': 'pokemon', '2⃣': 'time', '3⃣': 'location', '4⃣': 'day'}

        embed = discord.Embed(title=edit_question, color=discord.Colour.red())
        embed.add_field(name="1. Pokémon", value="\u200b", inline=False)
        embed.add_field(name=f"2. {raid_time}", value="\u200b", inline=False)
        embed.add_field(name=f"3. {raid_location}", value="\u200b", inline=False)
        embed.add_field(name=f"4. {raid_day}", value="\u200b", inline=False)
        embed.set_thumbnail(url="https://vignette.wikia.nocookie.net/pokemon/images/3/3b/Delibird_XY.gif")
        embed.set_footer(text="React with an Emoji below:")
        msg = await member.send(embed=embed)

        add_reactions = ['1⃣', '2⃣', '3⃣', '4⃣']
        for add_reaction in add_reactions:
            await msg.add_reaction(add_reaction)

        def check_reaction(reaction, user):
            return user.id == member.id

        try:
            wait_for_reaction, wait_for_user = await self.bot.wait_for('reaction_add', timeout=5.0, check=check_reaction)
        except asyncio.TimeoutError:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_red())
            await member.send(embed=embed)
            return

        embed = discord.Embed(title=f"{edit_type} {keys[wait_for_reaction.emoji].title()}",
                              color=discord.Colour.orange())
        await member.send(embed=embed)

        def check_msg(message):
            return message.author.id == member.id

        try:
            wait_for_message = await self.bot.wait_for('message', timeout=60.0, check=check_msg)
        except asyncio.TimeoutError:
            embed = discord.Embed(title=f"Timeout",
                                  description=f"You took too long to respond, please try again.",
                                  color=discord.Colour.dark_red())
            await member.send(embed=embed)
            return

        embed = discord.Embed(title=f"{thank_you}!",
                              description=f"{keys[wait_for_reaction.emoji].title()} will be changed to: {wait_for_message.content}",
                              color=discord.Colour.green())
        embed.set_thumbnail(url="https://www.inzonedesign.com/wp-content/uploads/2015/05/checkmark.gif")
        await member.send(embed=embed)

        # Update row with new variables
        if exraid is True:
            query = await self.get_edit_raid_query(keys[wait_for_reaction.emoji])
            params = (wait_for_message.content, guild_id, channel_id, message_id)
            await self.bot.db.execute(query, params)

        elif exraid is False and keys[wait_for_reaction.emoji] != "day":
            query = await self.get_edit_raid_query(keys[wait_for_reaction.emoji])
            query = query.replace('exraids', 'raids')
            params = (wait_for_message.content, guild_id, channel_id, message_id)
            await self.bot.db.execute(query, params)

        await self.update_raid(guild_id, channel_id, message_id)

        # Send Logs
        log_channel_id = await self.bot.get_cog("Utils").get_log_channel(guild_id)
        if log_channel_id is not None:
            embed = discord.Embed(title="[RAID] - Edited",
                                  description=f'➥ :bust_in_silhouette: {member.mention} ({member})\n➥ :mag_right: {keys[wait_for_reaction.emoji].title()} to {wait_for_message.content} ([{message_id}](https://discordapp.com/channels/{guild_id}/{channel_id}/{message_id}))',
                                  color=discord.Color.orange())
            embed.timestamp = datetime.datetime.utcnow()
            await self.bot.http.send_message(int(log_channel_id), "", embed=embed.to_dict())

    @staticmethod
    async def get_edit_raid_query(key):
        if key == 'pokemon':
            query = "UPDATE exraids SET pokemon=%s WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif key == 'time':
            query = "UPDATE exraids SET time=%s WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif key == 'location':
            query = "UPDATE exraids SET location=%s WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif key == 'day':
            query = "UPDATE exraids SET day=%s WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        else:
            return None

        return query

    async def update_raid(self, guild_id: str, channel_id: str, message_id: str):

        query = "SELECT user_id, pokemon, time, location, valor, mystic, instinct, harmony FROM raids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        params = (guild_id, channel_id, message_id)
        response = await self.bot.db.execute(query, params)

        if len(response) == 0:

            query = "SELECT user_id, pokemon, time, day, location, valor, mystic, instinct, harmony FROM exraids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
            params = (guild_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params)

            if len(response) == 0:
                return
            else:
                user_id, boss, time, day, location, valor, mystic, instinct, harmony = await self.bot.db.execute(query,
                                                                                                                 params,
                                                                                                                 single=True)
                ex_raid = True
        else:
            user_id, boss, time, location, valor, mystic, instinct, harmony = await self.bot.db.execute(query, params,
                                                                                                        single=True)
            ex_raid = False

        # Total amount of users attending
        total_valor = len(valor.split(",")) - 1
        total_mystic = len(mystic.split(",")) - 1
        total_instinct = len(instinct.split(",")) - 1
        total = total_valor + total_mystic + total_instinct + harmony

        guild = self.bot.get_guild(guild_id)

        valor_ids = valor.split(",")[:-1]
        valor_names = ""

        mystic_ids = mystic.split(",")[:-1]
        mystic_names = ""

        instinct_ids = instinct.split(",")[:-1]
        instinct_names = ""

        if len(valor_ids) != 0:
            for v in valor_ids:
                member = guild.get_member(int(v.strip()))
                valor_names += member.display_name + ", "

        if len(mystic_ids) != 0:
            for m in mystic_ids:
                member = guild.get_member(int(m.strip()))
                mystic_names += member.display_name + ", "

        if len(instinct_ids) != 0:
            for i in instinct_ids:
                member = guild.get_member(int(i.strip()))
                instinct_names += member.display_name + ", "

        if valor_names == "":
            valor_names = "\u200b"
        if mystic_names == "":
            mystic_names = "\u200b"
        if instinct_names == "":
            instinct_names = "\u200b"

        # Retrieve translation from JSON.
        raid_time, raid_location, raid_total, raid_by, raid_day = await self.bot.get_cog("Utils").get_translation(
            guild_id, "RAID_TIME RAID_LOCATION RAID_TOTAL RAID_BY RAID_DAY")

        # Retrieve gym location.
        gym_name = await self.bot.get_cog("Utils").get_gym(guild_id, location.lower())

        Alola = False
        if 'alola' in boss.lower() or 'alolan' in boss.lower():
            Alola = True
            boss_id_fix = boss.split(" ")[1]
            pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(boss_id_fix)
        else:
            pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(boss)

        if ex_raid is True:
            embed = discord.Embed(
                description=f"**{raid_time}: ** {time}\n**{raid_day}:** {day}\n**{raid_location}:** {gym_name}",
                color=discord.Colour.green())
            embed.set_author(name=f"⭐{boss.title()}⭐",
                             icon_url="https://www.pkparaiso.com/imagenes/shuffle/sprites/" + str(pokemon_id) + ".png")
        else:
            embed = discord.Embed(description=f"**{raid_time}:** {time}\n**{raid_location}:** {gym_name}",
                                  color=discord.Colour.green())
            embed.set_author(name=boss.title(),
                             icon_url="https://www.pkparaiso.com/imagenes/shuffle/sprites/" + str(pokemon_id) + ".png")

        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/pokemon_icons/pokemon_icon_" + str(
                pokemon_id) + "_00.png")

        if pokemon_id is None:

            if boss.lower() in ['t1', 't2', 'tier1', 'tier2', 'egg1', 'egg2']:
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/ic_raid_egg_normal.png")
                embed.set_author(name=boss.title(),
                                 icon_url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/ic_raid_egg_normal.png")
            elif boss.lower() in ['t3', 't4', 'tier3', 'tier4', 'egg3', 'egg4']:
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/ic_raid_egg_rare.png")
                embed.set_author(name=boss.title(),
                                 icon_url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/ic_raid_egg_rare.png")
            elif boss.lower() in ['t5', 'tier5', 'egg5']:
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/ic_raid_egg_legendary.png")
                embed.set_author(name=boss.title(),
                                 icon_url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/ic_raid_egg_legendary.png")
            else:
                embed.set_thumbnail(url="http://cdn.onlinewebfonts.com/svg/img_555509.png")
                embed.set_author(name=boss.title(), icon_url="http://cdn.onlinewebfonts.com/svg/img_555509.png")

        elif Alola:
            url = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id, alola=True)
            embed.set_thumbnail(url=url)
        else:
            url = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id)
            embed.set_thumbnail(url=url)

        embed.add_field(name=f"Valor ({total_valor})", value=f"{valor_names}", inline=False)
        embed.add_field(name=f"Mystic ({total_mystic})", value=f"{mystic_names}", inline=False)
        embed.add_field(name=f"Instinct ({total_instinct})", value=f"{instinct_names}", inline=False)
        embed.set_footer(text=f"{raid_total}: {total} | {raid_by}: {guild.get_member(int(user_id))}")

        try:
            await self.bot.http.edit_message(channel_id, message_id, embed=embed.to_dict())
        except discord.errors.NotFound:
            return

    async def pop_user(self, guild_id: str, channel_id: str, message_id: str, name: str, team: str):

        guild_id = str(guild_id)
        channel_id = str(channel_id)
        message_id = str(message_id)
        name = str(name)

        if team in ['1⃣', '2⃣', '3⃣']:
            nmr_dict = {'1⃣': 1, '2⃣': 2, '3⃣': 3}

            query = "UPDATE raids SET harmony = harmony - %s WHERE server_id = %s AND channel_id = %s AND message_id= %s"
            params = (nmr_dict[team], guild_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params)

            if len(response) == 0:
                query = query.replace('raids', 'exraids')
                params = (nmr_dict[team], guild_id, channel_id, message_id)
                await self.bot.db.execute(query, params)

        else:
            query = await self.get_pop_user_query(team)

            if query is None:
                return

            params = (name + ", ", guild_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params)

            if len(response) == 0:
                query = query.replace('raids', 'exraids')
                params = (name + ", ", guild_id, channel_id, message_id)
                await self.bot.db.execute(query, params)

    @staticmethod
    async def get_pop_user_query(team: str):
        if team == 'valor':
            query = "UPDATE raids SET valor=REPLACE(valor, %s, '') WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif team == 'mystic':
            query = "UPDATE raids SET mystic=REPLACE(mystic, %s, '') WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif team == 'instinct':
            query = "UPDATE raids SET instinct=REPLACE(instinct, %s, '') WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        else:
            return None

        return query

    async def append_user(self, guild_id: str, channel_id: str, message_id: str, name: str, team: str):
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        message_id = str(message_id)
        name = str(name)

        if team in ['1⃣', '2⃣', '3⃣']:
            nmr_dict = {'1⃣': 1, '2⃣': 2, '3⃣': 3}

            query = "UPDATE raids SET harmony = harmony + %s WHERE server_id = %s AND channel_id = %s AND message_id= %s"
            params = (nmr_dict[team], guild_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params)

            if len(response) == 0:
                query = "UPDATE exraids SET harmony = harmony + %s WHERE server_id = %s AND channel_id = %s AND message_id= %s"
                params = (nmr_dict[team], guild_id, channel_id, message_id)
                await self.bot.db.execute(query, params)

        else:
            query = await self.get_append_user_query(team)

            if query is None:
                return

            params = (name + ", ", guild_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params)

            if len(response) == 0:
                query = query.replace('raids', 'exraids')
                params = (name + ", ", guild_id, channel_id, message_id)
                await self.bot.db.execute(query, params)

    @staticmethod
    async def get_append_user_query(team: str):
        if team == 'valor':
            query = "UPDATE raids SET valor=CONCAT(valor, %s) WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif team == 'mystic':
            query = "UPDATE raids SET mystic=CONCAT(mystic, %s) WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        elif team == 'instinct':
            query = "UPDATE raids SET instinct=CONCAT(instinct, %s) WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        else:
            return None

        return query

    async def is_author(self, server_id: str, channel_id: str, message_id: str, member_id: str):
        query = "SELECT user_id FROM raids WHERE server_id = %s AND channel_id = %s AND message_id= %s"
        params = (server_id, channel_id, message_id)
        response = await self.bot.db.execute(query, params, single=True)

        if response is None:
            query = "SELECT user_id FROM exraids WHERE server_id = %s AND channel_id = %s AND message_id= %s"
            params = (server_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params, single=True)

            if response is None:
                query = "SELECT user_id FROM research WHERE server_id = %s AND channel_id = %s AND message_id= %s"
                params = (server_id, channel_id, message_id)
                response = await self.bot.db.execute(query, params, single=True)

                if response is None:
                    return False

        (user_id, ) = response

        if str(user_id) == str(member_id):
            return True
        else:
            return False

    async def permission_role_or_admin(self, server_id: str, member: discord.Member):

        query = "SELECT role_permission FROM settings WHERE server_id = %s"
        params = (server_id,)
        role_id = await self.bot.db.execute(query, params, single=True)

        try:
            if discord.utils.get(member.roles, id=int(role_id)):
                return True
            else:
                return False
        except TypeError:  # int(None)
            return False

    async def delete_raid(self, server_id: str, channel_id: str, message_id: str, member: discord.Member):
        query = "DELETE FROM raids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        params = (server_id, channel_id, message_id)
        response = await self.bot.db.execute(query, params, rowcount=True)

        if response != 1:
            query = "DELETE FROM exraids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
            params = (server_id, channel_id, message_id)
            response = await self.bot.db.execute(query, params, rowcount=True)

            if response != 1:
                query = "DELETE FROM research WHERE server_id = %s AND channel_id = %s AND message_id = %s"
                params = (server_id, channel_id, message_id)
                response = await self.bot.db.execute(query, params, rowcount=True)

                if response == 0:
                    return

        try:
            await self.bot.http.delete_message(channel_id, message_id)
        except discord.errors.NotFound:
            return

        # Send Logs
        log_channel_id = await self.bot.get_cog("Utils").get_log_channel(server_id)
        if log_channel_id is not None:
            embed = discord.Embed(title="[RAID] - Deleted",
                                  description=f'➥ :bust_in_silhouette: {member.mention} ({member})\n➥ :mag_right: ([{message_id}](https://discordapp.com/channels/{server_id}/{channel_id}/{message_id}))',
                                  color=discord.Color.red())
            embed.timestamp = datetime.datetime.utcnow()
            await self.bot.http.send_message(log_channel_id, "", embed=embed.to_dict())

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        await self.bot.wait_until_ready()

        guild_id = payload.guild_id
        channel_id = payload.channel_id
        message_id = payload.message_id

        query = "DELETE FROM raids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
        params = (str(guild_id), str(channel_id), str(message_id))
        await self.bot.db.execute(query, params)


def setup(bot):
    bot.add_cog(RawReaction(bot))
