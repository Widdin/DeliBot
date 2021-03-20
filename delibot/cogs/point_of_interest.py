import discord
from discord.ext import commands


class PointOfInterest(commands.Cog):
    """
    Commands for adding point of interests (gyms / stops).
    """

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def allowed_latlon(validation_string):
        allowed_chars = set('0123456789+-.')

        if set(validation_string) <= allowed_chars:
            return True
        else:
            return False

    @commands.group(name="create", invoke_without_command=True)
    async def create(self, ctx):
        """
        Adds a Gym / Pokestop to the database so it will appear as a hyperlink on Raid-creations.
        Example: !create gym "Some name" 60.450 -20.350
        Example: !create pokestop "Some name" 60.450 -20.350
        """
        await ctx.message.delete()

        embed = discord.Embed(title=f"Available sub-commands for Create",
                              color=discord.Colour.orange())
        embed.add_field(name='gym', value='Example: !create gym "city fountain" 12.345 98.765', inline=False)
        embed.add_field(name='pokestop', value='Example: !create pokestop "water mountain" 12.345 98.765', inline=False)
        embed.set_footer(text="Auto-deleting in 20 seconds..")

        await ctx.message.channel.send(embed=embed, delete_after=20)

    @create.command(name="create_gym", aliases=["gym", "Gym"])
    async def create_gym(self, ctx, name, lat, lon):

        allowed = await self.bot.get_cog("RawReaction").permission_role_or_admin(ctx.message.guild.id,
                                                                                 ctx.message.author)

        if allowed or ctx.message.author.guild_permissions.administrator:

            lat_check = await self.allowed_latlon(lat)
            lon_check = await self.allowed_latlon(lon)

            if lat_check is True and lon_check is True:

                async with self.bot.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        success = await cur.execute(
                            "INSERT INTO gyms (server_id, name, lat, lon) VALUES (%s, %s, %s, %s)",
                            (ctx.message.guild.id, name.lower(), lat, lon))
                        await conn.commit()

                if success == 1:
                    embed = discord.Embed(title=f"Gym - {name.title()} was successfully created.",
                                          color=discord.Colour.green())
                    embed.set_thumbnail(
                        url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/hint_gym.png")
                    embed.set_footer(text="Auto-deleting in 15 seconds..")
                    await ctx.message.channel.send(embed=embed, delete_after=15)
                else:
                    embed = discord.Embed(title=f"Gym - Failed to create {name.title()}.",
                                          color=discord.Colour.red())
                    embed.add_field(name='latitude', value=lat)
                    embed.add_field(name='longitude', value=lon)
                    embed.set_thumbnail(
                        url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/hint_gym.png")
                    embed.set_footer(text="Auto-deleting in 15 seconds..")
                    await ctx.message.channel.send(embed=embed, delete_after=15)
                    return

            else:
                embed = discord.Embed(
                    color=discord.Colour.red())
                embed.add_field(name='Error',
                                value=f'**Latitude** or **Longitude** is in wrong format\n\nYou sent in: **{lat}** **{lon}**\n\nExample: **60.00** **-25.00**')
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await ctx.message.channel.send(embed=embed, delete_after=15)
                return

    @create.command(pass_context=True, aliases=["pokestop", "Pokestop", "stop", "Stop"])
    async def create_pokestop(self, ctx, name, lat, lon):

        allowed = await self.bot.get_cog("RawReaction").permission_role_or_admin(ctx.message.guild.id,
                                                                                 ctx.message.author)

        if allowed or ctx.message.author.guild_permissions.administrator:

            lat_check = await self.allowed_latlon(lat)
            lon_check = await self.allowed_latlon(lon)

            if lat_check is True and lon_check is True:

                query = "INSERT INTO pokestops (server_id, name, lat, lon) VALUES (%s, %s, %s, %s)"
                params = (ctx.message.guild.id, name.lower(), lat, lon)
                success = self.bot.db.execute(query, params)

                if success == 1:
                    embed = discord.Embed(title=f"Pokestop - {name.title()} was successfully created.",
                                          color=discord.Colour.green())
                    embed.set_thumbnail(
                        url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pokestop_near.png")
                    embed.set_footer(text="Auto-deleting in 15 seconds..")
                    await ctx.message.channel.send(embed=embed, delete_after=15)
                else:
                    embed = discord.Embed(title=f"Pokestop - Failed to create {name.title()}.",
                                          color=discord.Colour.red())
                    embed.add_field(name='latitude', value=lat)
                    embed.add_field(name='longitude', value=lon)
                    embed.set_thumbnail(
                        url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pokestop_near.png")
                    embed.set_footer(text="Auto-deleting in 15 seconds..")
                    await ctx.message.channel.send(embed=embed, delete_after=15)
                    return

            else:
                embed = discord.Embed(
                    color=discord.Colour.red())
                embed.add_field(name='Error',
                                value=f'**Latitude** or **Longitude** is in wrong format\n\nYou sent in: **{lat}** **{lon}**\n\nExample: **60.00** **-25.00**')
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await ctx.message.channel.send(embed=embed, delete_after=15)
                return

    @commands.group(name="delete", invoke_without_command=True)
    async def delete(self, ctx):
        """
        Deletes a Gym / Pokestop from the database.
        Example: *!delete gym "Some name"*
        Example: *!delete pokestop "Some name"*
        """
        await ctx.message.delete()

        embed = discord.Embed(title=f"Available sub-commands for Delete",
                              color=discord.Colour.orange())
        embed.add_field(name='gym', value='Example: !delete gym "city fountain"', inline=False)
        embed.add_field(name='pokestop', value='Example: !delete pokestop "water mountain"', inline=False)
        embed.set_footer(text="Auto-deleting in 15 seconds..")

        await ctx.message.channel.send(embed=embed, delete_after=15)

    @delete.command(name="delete_gym", aliases=["gym", "Gym"])
    async def delete_gym(self, ctx, name):

        allowed = await self.bot.get_cog("RawReaction").permission_role_or_admin(ctx.message.guild.id,
                                                                                 ctx.message.author)

        if allowed or ctx.message.author.guild_permissions.administrator:

            query = "DELETE FROM gyms WHERE server_id = %s AND name = %s"
            params = (ctx.message.guild.id, name.lower())
            success = self.bot.db.execute(query, params)

            if success == 1:
                embed = discord.Embed(title=f"Gym - {name} was successfully deleted.",
                                      color=discord.Colour.green())
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/hint_gym.png")
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await ctx.message.channel.send(embed=embed, delete_after=15)
            else:
                embed = discord.Embed(title=f"Gym - Failed to find {name}.",
                                      color=discord.Colour.red())
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/hint_gym.png")
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await ctx.message.channel.send(embed=embed, delete_after=15)
        else:
            raise commands.CheckFailure

    @delete.command(name="delete_pokestop", aliases=["pokestop", "Pokestop", "stop", "Stop"])
    async def delete_pokestop(self, ctx, name):

        allowed = await self.bot.get_cog("RawReaction").permission_role_or_admin(ctx.message.guild.id,
                                                                                 ctx.message.author)

        if allowed or ctx.message.author.guild_permissions.administrator:

            query = "DELETE FROM pokestops WHERE server_id = %s AND name = %s"
            params = (ctx.message.guild.id, name.lower())
            success = self.bot.db.execute(query, params)

            if success == 1:
                embed = discord.Embed(title=f"Pokestop - {name} was successfully deleted.",
                                      color=discord.Colour.green())
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/img_pokestop.png")
                await ctx.message.channel.send(embed=embed, delete_after=15)
            else:
                embed = discord.Embed(title=f"Pokestop - Failed to find {name}.",
                                      color=discord.Colour.red())
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/img_pokestop.png")
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await ctx.message.channel.send(embed=embed, delete_after=15)
        else:
            raise commands.CheckFailure


def setup(bot):
    bot.add_cog(PointOfInterest(bot))
