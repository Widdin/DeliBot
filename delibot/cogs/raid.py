import asyncio
import logging
import discord
from discord.ext import commands
from datetime import datetime

log = logging.getLogger()


class Raid(commands.Cog):
    """
    Commands for Raids.
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.delete_old_raids())

    async def delete_old_raids(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            raids = await self.bot.db.get_raids_older_than(2)

            log.info(f'Deleting {len(raids)} old raids...')

            if len(raids) > 0:
                await self.bot.db.delete_raids_older_than(2)

                for raid in raids:
                    channel_id = raid[1]
                    message_id = raid[2]

                    # TODO: Update raids_created / raids_joined

                    try:
                        await self.bot.http.delete_message(channel_id, message_id)
                    except discord.NotFound:
                        pass
                    except discord.Forbidden:
                        pass
                    
            log.info(f'Finished deleting {len(raids)} old raids. Sleeping for 5 minutes.')
            await asyncio.sleep(300)

    async def ask_user(self, ctx):

        raid_creation, type_below, what_pokemon, what_time, what_location, thank_you, raid_time, raid_location, raid_total, raid_by = await self.bot.get_cog(
            "Utils").get_translation(ctx.message.guild.id, "RAID_CREATION TYPE_BELOW WHAT_POKEMON WHAT_TIME WHAT_LOCATION THANK_YOU RAID_TIME RAID_LOCATION RAID_TOTAL RAID_BY")

        embed = discord.Embed(title=what_pokemon, color=discord.Colour.red())
        embed.set_footer(text=type_below)
        await ctx.message.author.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        try:
            wait_for_mon = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.message.author.send("Timeout")
            return

        pokemon = wait_for_mon.content

        embed = discord.Embed(title=what_time, color=discord.Colour.orange())
        embed.set_footer(text=type_below)
        await ctx.message.author.send(embed=embed)

        try:
            wait_for_time = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.message.author.send("Timeout")
            return

        time = wait_for_time.content

        embed = discord.Embed(title=what_location, color=discord.Colour.green())
        embed.set_footer(text=type_below)
        await ctx.message.author.send(embed=embed)

        try:
            wait_for_loc = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.message.author.send("Timeout")
            return

        location = wait_for_loc.content

        embed = discord.Embed(title=thank_you, description=f"{raid_creation} {ctx.message.channel.name}",
                              color=discord.Colour.green())
        await ctx.message.author.send(embed=embed)

        return pokemon, time, location

    @commands.command(name="raid", aliases=["r", "R", "Raid"])
    async def raid(self, ctx, pokemon: str = None, time: str = None, *, location: str = None):
        """
        Starts a Raid with the given information. Will delete itself after 2 hours.
        If no args is given, you will be asked for input in private message.
        Example: *!raid snorlax 00:00 Park fountain*
        """

        # Deletes your command.
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        except discord.NotFound:
            pass
        except discord.HTTPException:
            pass

        # Retrieve translation from JSON.
        raid_creation, type_below, what_pokemon, what_time, what_location, thank_you, raid_time, raid_location, raid_total, raid_by = await self.bot.get_cog(
            "Utils").get_translation(ctx.message.guild.id, "RAID_CREATION TYPE_BELOW WHAT_POKEMON WHAT_TIME WHAT_LOCATION THANK_YOU RAID_TIME RAID_LOCATION RAID_TOTAL RAID_BY")

        # No input given, ask the user in PM for input.
        if pokemon is None or time is None or location is None:
            pokemon, time, location = await self.ask_user(ctx)

        # Channel to post in if it exist.
        (default_channel, ) = await self.bot.db.get_default_channel(ctx.message.guild.id)

        # Create the user in the database if he doesn't exist.
        await self.bot.get_cog("Utils").create_user_if_not_exist(ctx.message.guild.id, ctx.message.author.id)

        is_alola = False
        if 'alola' in pokemon.lower() or 'alolan' in pokemon.lower():
            is_alola = True
            pokemon = pokemon + " " + time
            time = location.split(" ")[0]
            location = ' '.join(location.split(" ")[1:])
            pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(pokemon.split(" ")[1])
        else:
            pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(pokemon)

        # Retrieve gym location.
        gym_name = await self.bot.get_cog("Utils").get_gym(ctx.message.guild.id, location.lower())

        # Create embed
        embed = discord.Embed(description=f"**{raid_time}:** {time}\n**{raid_location}:** {gym_name}",
                              color=discord.Colour.green())
        embed.set_author(name=pokemon.title(),
                         icon_url="https://www.pkparaiso.com/imagenes/shuffle/sprites/" + str(pokemon_id) + ".png")

        # Images
        if pokemon_id is None:
            images = await self.bot.get_cog("Utils").get_egg_image_url(pokemon=pokemon)
        else:
            images = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id, is_alola=is_alola)

        embed.set_thumbnail(url=images['url'])
        embed.set_author(name=pokemon.title(), icon_url=images['icon_url'])
        embed.add_field(name="Valor (0)", value="\u200b", inline=False)
        embed.add_field(name="Mystic (0)", value="\u200b", inline=False)
        embed.add_field(name="Instinct (0)", value="\u200b", inline=False)
        embed.set_footer(text=f"{raid_total}: 0 | {raid_by}: {str(ctx.message.author)}")
        embed.timestamp = datetime.utcnow()

        # <@&484280142806646815>
        # Role tagged in args
        if '<' in location and '>' in location and '@&' in location:
            role = location.split(" ")[-1]
            location = location.replace(role, '').strip()

            gym_name = await self.bot.get_cog("Utils").get_gym(ctx.message.guild.id, location.lower())

            embed.description = f'**{raid_time}:** {time}\n**{raid_location}:** {gym_name}'
            raid_message = await ctx.send(f"{role}", embed=embed)

        # <#556266308371480576>
        # Other channel in args
        elif '<' in location and '>' in location and '#' in location:
            channel_id = location.split(" ")[-1]
            other_channel = ctx.guild.get_channel(int(channel_id[2:-1]))
            location = location.replace(channel_id, '').strip()

            gym_name = await self.bot.get_cog("Utils").get_gym(ctx.message.guild.id, location.lower())

            embed.description = f'**{raid_time}:** {time}\n**{raid_location}:** {gym_name}'
            raid_message = await other_channel.send(embed=embed)

        elif default_channel is not None:
            other_channel = ctx.guild.get_channel(int(default_channel))
            raid_message = await other_channel.send(embed=embed)

        else:
            raid_message = await ctx.send(embed=embed)

        # Fix full name if its short version
        if gym_name.rfind("]") != -1:
            location = (gym_name[gym_name.find("[") + len("["):gym_name.rfind("]")])
        else:
            location = gym_name

        # Insert raid to database
        query = ("INSERT INTO raids (server_id, channel_id, message_id, user_id, author, pokemon, time, location, "
                 "valor, mystic, instinct) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        params = (str(ctx.message.guild.id), str(raid_message.channel.id), str(raid_message.id), str(ctx.message.author.id), "", str(pokemon), str(time), str(location.lower()), "", "", "")
        await self.bot.db.execute(query, params)

        # Find team-reactions
        reactions = ['1⃣', '2⃣', '3⃣', '\U0001f4dd', '\U0000274c', '\U00002694']
        emojis = ctx.message.guild.emojis
        for emoji in emojis:
            if emoji.name == 'valor' or emoji.name == 'mystic' or emoji.name == 'instinct':
                reactions.insert(0, emoji)

        # Add reactions
        for reaction in reactions[:len(reactions)]:
            await raid_message.add_reaction(reaction)

        # Send Logs
        log_channel_id = await self.bot.get_cog("Utils").get_log_channel(ctx.message.guild.id)
        if log_channel_id is not None:
            embed = discord.Embed(title="[RAID] - Created",
                                  description=f'➥ :bust_in_silhouette: {ctx.message.author.mention} ({ctx.message.author})\n➥ :mag_right: {pokemon} ({time}) @ {gym_name} ([{raid_message.id}](https://discordapp.com/channels/{ctx.message.guild.id}/{raid_message.channel.id}/{raid_message.id}))',
                                  color=discord.Color.green())
            embed.timestamp = datetime.utcnow()
            await self.bot.http.send_message(int(log_channel_id), "", embed=embed.to_dict())


def setup(bot):
    bot.add_cog(Raid(bot))
