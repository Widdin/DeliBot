from discord.ext import commands

# The Cog metaclass allows you to pass two kwargs, name and command_attrs.
# Name changes the name of the Cog when shown in help, and command_attrs sets an attribute of every command in the cog.
# In this case, we're setting the name to "Owner Commands" and setting each command's hidden attribute to be True.
# Hidden prevents it from showing up on the default help.
# See https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#discord.ext.commands.CogMeta For more detail

command_attrs = {'hidden': True}


class OwnerCog(commands.Cog, name='Owner Commands', command_attrs=command_attrs):

    def __init__(self, bot):
        self.bot = bot

    # This is how you would manually set hidden on a per-command basis.
    # However, we've done that on our cog definition with command_attrs, so this is redundant.
    @commands.command(name='load', hidden=True)
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

    # As we want every command defined in our owner cog to be owner-only, we don't have to apply the owner-check to each command
    # and can instead use the special method, cog_check, which will add a check to each command in the cog.
    # See https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#discord.ext.commands.Cog.cog_check for details
    async def cog_check(self, ctx):
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner('You do not own this bot.')
        return True


def setup(bot):
    bot.add_cog(OwnerCog(bot))
