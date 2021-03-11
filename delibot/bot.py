import logging

import discord
from discord.ext import commands

from utils import default

logging.basicConfig(format='%(asctime)s [%(threadName)18s][%(module)14s][%(levelname)8s] %(message)s',
                    level=logging.INFO)
log = logging.getLogger()

config = default.get_config()

initial_extensions = ['cogs.owner',
                      'cogs.raid',
                      'cogs.utils',
                      'cogs.raw_reaction',
                      'cogs.exraid',
                      'cogs.silphroad',
                      'cogs.pokebox',
                      'cogs.pokebattler',
                      'cogs.point_of_interest',
                      'cogs.community',
                      'cogs.ocr',
                      'cogs.admin',
                      'cogs.research',
                      'cogs.trade',
                      'cogs.rocket_stop',
                      'utils.db']

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=config['SETTINGS']['prefix'], intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    log.info(f'Logged in as: {bot.user.name} - {bot.user.id} | Version: {discord.__version__}\n')
    await bot.change_presence(activity=discord.Game(name='Pokémon GO', type=1))


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

    if config.getboolean('TOKEN', 'is-developing'):
        log.info("Running with Development token")
        TOKEN = config['TOKEN']['dev-token']
    else:
        log.info("Running with Production token")
        TOKEN = config['TOKEN']['prod-token']

    bot.run(TOKEN, bot=True, reconnect=True)
