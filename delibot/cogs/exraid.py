import asyncio
from datetime import datetime

import discord
from discord.ext import commands


class Exraid(commands.Cog):
    """
    Commands for EX-Raids.
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self._init_delete_old_raids())

    async def _init_delete_old_raids(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM exraids WHERE created_at < ADDDATE(NOW(), INTERVAL -14 DAY)")
                    results = await cur.fetchall()
                    await cur.execute("DELETE FROM exraids WHERE created_at < ADDDATE(NOW(), INTERVAL -14 DAY)")

                    for result in results:
                        try:
                            await self.bot.http.delete_message(result[1], result[2])
                        except discord.NotFound:
                            pass
                        except discord.Forbidden:
                            pass
                        else:
                            # If more than 2 attending at the end, increment 'raids_created' for the author
                            attending = (len(result[9].split(",")) - 1) + (len(result[10].split(",")) - 1) + (
                                    len(result[11].split(",")) - 1) + int(result[12])

                            # Increment 'raids_joined' for the attending users.
                            if attending >= 2:
                                await cur.execute(
                                    "UPDATE users SET raids_created = raids_created + 1 WHERE server_id = %s AND "
                                    "user_id = %s",
                                    (result[0], result[3]))

                                # Only count the user as attending ONCE.
                                attended_users = [",", " ", ""]
                                all_users = result[8].split(",") + result[9].split(",") + result[10].split(",")

                                for user in all_users:
                                    user = user.strip()

                                    if user not in attended_users:
                                        attended_users.append(user)

                                        await self.bot.get_cog("Utils").create_user_if_not_exist(result[0], user)

                                        await cur.execute(
                                            "UPDATE users SET raids_joined = raids_joined + 1 WHERE server_id = %s "
                                            "AND user_id = %s",
                                            (result[0], user))

                        await asyncio.sleep(10)

            await asyncio.sleep(3600)

    async def mysqlRaid(self, guild_id: str, channel_id: str, message_id: str, user_id: str, author: str, pokemon: str,
                        time: str, day: str, location: str, valor: str, mystic: str, instinct: str):
        query = ("INSERT INTO exraids "
                 "(server_id, channel_id, message_id, user_id, author, pokemon, time, day, location, valor, mystic, "
                 "instinct) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        values = (
            str(guild_id), str(channel_id), str(message_id), str(user_id), str(author), str(pokemon), str(time),
            str(day),
            str(location), str(valor), str(mystic), str(instinct))

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                await conn.commit()

    async def get_default_ex_channel(self, guild_id):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT default_exraid_id FROM settings WHERE server_id = %s", (guild_id,))
                (channel,) = await cur.fetchone()

        return channel

    @commands.command(pass_context=True, aliases=['Exraid', 'xr', 'Xr'])
    async def exraid(self, ctx, pokemon: str, time: str, day: str, *, location: str, delete=True):
        """
        Starts a EX-raid. Works just like "!raid" but it lasts for 14 days and takes "day" as an additional parameter)
        """

        if delete:
            await ctx.message.delete()

        # Retrieve translation from JSON.
        raid_time, raid_location, raid_total, raid_by, raid_day = await self.bot.get_cog("Utils").get_translation(
            ctx.message.guild.id, "RAID_TIME RAID_LOCATION RAID_TOTAL RAID_BY RAID_DAY")

        # Create the user in the database if he doesn't exist.
        await self.bot.get_cog("Utils").create_user_if_not_exist(ctx.message.guild.id, ctx.message.author.id)

        # Channel to post in if it exist.
        default_ex_channel = await self.get_default_ex_channel(ctx.message.guild.id)

        # Retrieve gym location.
        gym_name = await self.bot.get_cog("Utils").get_gym(ctx.message.guild.id, location.lower())

        # Get the pokémon ID.
        pokemon_id = await  self.bot.get_cog("Utils").get_pokemon_id(pokemon)

        # Create the embed.
        embed = discord.Embed(
            description=f"**{raid_time}:** {time}\n**{raid_day}:** {day}\n**{raid_location}:** {gym_name}",
            color=discord.Colour.green())
        embed.set_author(name=f"⭐{pokemon.title()}⭐",
                         icon_url="https://www.pkparaiso.com/imagenes/shuffle/sprites/" + str(pokemon_id) + ".png")
        embed.timestamp = datetime.utcnow()

        # Pokemon image.
        url = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id, False, False)
        embed.set_thumbnail(url=url)

        embed.add_field(name="Valor (0)", value="\u200b", inline=False)
        embed.add_field(name="Mystic (0)", value="\u200b", inline=False)
        embed.add_field(name="Instinct (0)", value="\u200b", inline=False)
        embed.set_footer(text=f"{raid_total} 0 | {raid_by} {str(ctx.message.author)}")

        # Other channel
        if '<' in location and '>' in location:
            channel_id = location.split(" ")[-1]
            other_channel = self.bot.get_channel(channel_id[2:-1])
            location = location.replace(channel_id, '')
            embed.description = f'**{raid_time}:** {time}\n**{raid_location}:** {location.title()}'
            raid_message = await other_channel.send(embed=embed)
        elif default_ex_channel is not None:
            other_channel = self.bot.get_channel(int(default_ex_channel))
            raid_message = await other_channel.send(embed=embed)
        else:
            raid_message = await ctx.message.channel.send(embed=embed)

        # Fix full name if its short version
        if gym_name.rfind("]") != -1:
            location = (gym_name[gym_name.find("[") + len("["):gym_name.rfind("]")])
        else:
            location = gym_name

        # MYSQL
        await self.mysqlRaid(ctx.message.guild.id, raid_message.channel.id, raid_message.id, ctx.message.author.id, "",
                             pokemon, time, day, location.lower(), "", "", "")

        # Reactions
        reactions = ['1⃣', '2⃣', '3⃣', '\U0001f4dd',
                     '\U0000274c']  # '\U00000031\U000020e3', '\U00000032\U000020e3', '\U00000033\U000020e3'
        emojis = ctx.message.guild.emojis
        for emoji in emojis:
            if emoji.name == 'valor' or emoji.name == 'mystic' or emoji.name == 'instinct':
                reactions.insert(0, emoji)

        # Add reactions
        for reaction in reactions[:len(reactions)]:
            await raid_message.add_reaction(reaction)


def setup(bot):
    bot.add_cog(Exraid(bot))
