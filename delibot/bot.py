import asyncio
import logging
import logging.handlers
from datetime import datetime
from typing import List, Optional

import discord
from discord.ext import commands

from utils import default


class CustomBot(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            testing_guild_id: Optional[int] = None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_pool = None
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


async def main():
    logging.basicConfig(format='%(asctime)s [%(filename)14s:%(lineno)4d][%(funcName)30s][%(levelname)8s] %(message)s',
                        level=logging.INFO)
    file_handler = logging.FileHandler(filename='logs/' + '{:%Y-%m-%d}.log'.format(datetime.now()))
    formatter = logging.Formatter('%(asctime)s [%(filename)14s:%(lineno)4d][%(levelname)8s] %(message)s')
    file_handler.setFormatter(formatter)

    log = logging.getLogger()
    log.addHandler(file_handler)

    config = default.get_config()

    intents = discord.Intents.default()
    intents.members = True

    extensions = ['utils.db',
                  'utils.utils',
                  'cogs.owner',
                  'cogs.raid',
                  'cogs.raw_reaction',
                  'cogs.exraid',
                  'cogs.community',
                  'cogs.admin',
                  # 'cogs.silphroad',
                  # 'cogs.pokebox',
                  # 'cogs.pokebattler',
                  # 'cogs.point_of_interest',
                  # 'cogs.ocr',
                  # 'cogs.research',
                  # 'cogs.trade',
                  # 'cogs.rocket_stop',
                  # 'cogs.trade'
                  ]

    async with CustomBot(commands.when_mentioned, initial_extensions=extensions, intents=intents) as bot:
        if config.getboolean('TOKEN', 'is-developing'):
            log.info("Running with Development token")
            token = config['TOKEN']['dev-token']
        else:
            log.info("Running with Production token")
            token = config['TOKEN']['prod-token']

        await bot.start(token)


asyncio.run(main())
