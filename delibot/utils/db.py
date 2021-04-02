import logging

import aiomysql
from discord.ext import commands

from utils import default

config = default.get_config()
log = logging.getLogger()


class Database(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.init_conn())
        self.bot.db = self

    async def init_conn(self):
        log.info("Connecting to database...")

        db_host = config.get('DATABASE', 'db-host')
        db_name = config.get('DATABASE', 'db-name')
        db_user = config.get('DATABASE', 'db-user')
        db_pass = config.get('DATABASE', 'db-pass')
        db_port = config.getint('DATABASE', 'db-port')

        try:
            self.bot.pool = await aiomysql.create_pool(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_pass,
                db=db_name,
                autocommit=True,
                loop=self.bot.loop)
        except Exception as e:
            log.critical(f'Could not connect to database. Reason: {e}')
            exit()
        else:
            log.info("Successfully connected to database")

    async def execute(self, query, params=None, single=False, rowcount=False):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())

                if rowcount:
                    return cur.rowcount
                elif single:
                    return await cur.fetchone()
                else:
                    return await cur.fetchall()

    async def get_raids_older_than(self, hours: int):
        query = "SELECT * FROM raids WHERE created_at < ADDDATE(NOW(), INTERVAL -%s HOUR)"
        params = (hours,)

        return await self.execute(query, params)

    async def delete_raids_older_than(self, hours: int):
        query = "DELETE FROM raids WHERE created_at < ADDDATE(NOW(), INTERVAL -%s HOUR)"
        params = (hours,)

        return await self.execute(query, params)

    async def get_default_channel(self, guild_id: int):
        query = "SELECT default_raid_id FROM settings WHERE server_id = %s"
        params = (guild_id,)

        return await self.execute(query, params, single=True)


def setup(bot):
    bot.add_cog(Database(bot))
