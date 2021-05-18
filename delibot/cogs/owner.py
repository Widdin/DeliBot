import discord
from discord.ext import commands

command_attrs = {'hidden': True}


class OwnerCog(commands.Cog, name='Owner Commands', command_attrs=command_attrs):
    """
    Commands for the bot-owner to load / unload / reload modules.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def servers(self, ctx):
        """Command which shows the total amount of server and users"""
        await ctx.message.delete()

        guilds = len(self.bot.guilds)
        users = sum(g.member_count for g in self.bot.guilds)

        embed = discord.Embed(color=discord.Colour(0x00ff00))
        embed.description = '**Total servers:** {0}\n**Total users:** {1}'.format(guilds, users)

        await ctx.send(embed=embed, delete_after=30)

    @commands.command(name='load')
    async def load_cog(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload')
    async def unload_cog(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload')
    async def reload_cog(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    async def cog_check(self, ctx):
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner('You do not own this bot.')
        return True


def setup(bot):
    bot.add_cog(OwnerCog(bot))
