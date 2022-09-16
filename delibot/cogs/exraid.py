import asyncio
import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger()


class Exraid(commands.Cog):
    """
    Commands for EX-Raids.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.loop.create_task(self._init_delete_old_raids())

    async def _init_delete_old_raids(self):
        while not self.bot.is_closed():
            query = "SELECT * FROM exraids WHERE created_at < ADDDATE(NOW(), INTERVAL -14 DAY)"
            results = await self.bot.db.execute(query)

            query = "DELETE FROM exraids WHERE created_at < ADDDATE(NOW(), INTERVAL -14 DAY)"
            await self.bot.db.execute(query)

            log.info(f'Deleting {len(results)} old ex-raids...')

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

                        query = "UPDATE users SET raids_created = raids_created + 1 WHERE server_id = %s AND user_id = %s"
                        params = (result[0], result[3])
                        await self.bot.db.execute(query, params)

                        # Only count the user as attending ONCE.
                        attended_users = [",", " ", ""]
                        all_users = result[8].split(",") + result[9].split(",") + result[10].split(",")

                        for user in all_users:
                            user = user.strip()

                            if user not in attended_users:
                                attended_users.append(user)

                                await self.bot.get_cog("Utils").create_user_if_not_exist(result[0], user)

                                query = "UPDATE users SET raids_joined = raids_joined + 1 WHERE server_id = %s AND user_id = %s"
                                params = (result[0], user)
                                await self.bot.db.execute(query, params)

                await asyncio.sleep(10)

            log.info(f'Finished deleting {len(results)} old ex-raids. Sleeping for 60 minutes.')
            await asyncio.sleep(3600)

    async def get_default_ex_channel(self, guild_id):
        query = "SELECT default_exraid_id FROM settings WHERE server_id = %s"
        params = (guild_id,)

        return await self.bot.db.execute(query, params, single=True)

    @app_commands.command(name="exraid",
                          description='Starts a Raid with the given information. Deletes itself after 2 hours.')
    @app_commands.describe(pokemon="Pokemon that spawned on the Raid", time="Time to start the Raid",
                           day="The day the Raid starts", location="Location of the Raid")
    async def exraid(self, interaction: discord.Interaction, pokemon: str, time: str, day: str, location: str):
        """
        Starts a EX-raid. Works just like "!raid" but it lasts for 14 days and takes "day" as an additional parameter)
        """

        # Retrieve translation from JSON.
        raid_time, raid_location, raid_total, raid_by, raid_day = await self.bot.get_cog("Utils").get_translation(
            interaction.guild_id, "RAID_TIME RAID_LOCATION RAID_TOTAL RAID_BY RAID_DAY")

        # Create the user in the database if he doesn't exist.
        await self.bot.get_cog("Utils").create_user_if_not_exist(interaction.guild_id, interaction.user.id)

        # Channel to post in if it exist.
        (default_ex_channel,) = await self.get_default_ex_channel(interaction.guild_id)

        # Retrieve gym location.
        gym_name = await self.bot.get_cog("Utils").get_gym(interaction.guild_id, location.lower())

        # Get the pokémon ID.
        pokemon_id = await  self.bot.get_cog("Utils").get_pokemon_id(pokemon)

        # Create the embed.
        embed = discord.Embed(
            description=f"**{raid_time}:** {time}\n**{raid_day}:** {day}\n**{raid_location}:** {gym_name}",
            color=discord.Colour.green())
        images = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id)
        embed.set_thumbnail(url=images['url'])
        embed.set_author(name=f"⭐{pokemon.title()}⭐", icon_url=images['icon_url'])
        embed.add_field(name="Valor (0)", value="\u200b", inline=False)
        embed.add_field(name="Mystic (0)", value="\u200b", inline=False)
        embed.add_field(name="Instinct (0)", value="\u200b", inline=False)
        embed.set_footer(text=f"{raid_total} 0 | {raid_by} {str(interaction.user)}")
        embed.timestamp = datetime.utcnow()

        if default_ex_channel is not None:
            other_channel = self.bot.get_channel(int(default_ex_channel))
            raid_message = await other_channel.send(embed=embed)
            await interaction.response.send_message(f'Exraid created in {other_channel.mention}', ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)
            raid_message = await interaction.original_response()

        # Fix full name if its short version
        if gym_name.rfind("]") != -1:
            location = (gym_name[gym_name.find("[") + len("["):gym_name.rfind("]")])
        else:
            location = gym_name

        # Insert raid to database
        query = ("INSERT INTO exraids "
                 "(server_id, channel_id, message_id, user_id, author, pokemon, time, day, location, valor, mystic, "
                 "instinct) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        params = (
            str(interaction.guild_id),
            str(raid_message.channel.id),
            str(raid_message.id),
            str(interaction.user.id),
            "",
            pokemon,
            time, day,
            location.lower(),
            "",
            "",
            ""
        )
        await self.bot.db.execute(query, params)

        # Reactions
        reactions = ['1⃣', '2⃣', '3⃣', '\U0001f4dd',
                     '\U0000274c']  # '\U00000031\U000020e3', '\U00000032\U000020e3', '\U00000033\U000020e3'
        emojis = interaction.guild.emojis
        for emoji in emojis:
            if emoji.name == 'valor' or emoji.name == 'mystic' or emoji.name == 'instinct':
                reactions.insert(0, emoji)

        # Add reactions
        for reaction in reactions[:len(reactions)]:
            await raid_message.add_reaction(reaction)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Exraid(bot))
