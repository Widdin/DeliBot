import logging

import aiomysql
from discord.ext import commands

from utils import default

config = default.get_config()
log = logging.getLogger()


class Database(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.db = self

    async def cog_load(self) -> None:
        await self.init_conn()
        await self.verify_amount_of_servers()

    async def init_conn(self):
        log.info("Connecting to database...")

        db_host = config.get('DATABASE', 'db-host')
        db_name = config.get('DATABASE', 'db-name')
        db_user = config.get('DATABASE', 'db-user')
        db_pass = config.get('DATABASE', 'db-pass')
        db_port = config.getint('DATABASE', 'db-port')

        try:
            self.bot.db_pool = await aiomysql.create_pool(
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
            log.info("Successfully connected to database.")

    async def execute(self, query, params=None, single=False, rowcount=False):
        async with self.bot.db_pool.acquire() as conn:
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

    async def verify_amount_of_servers(self):
        query = "SELECT count(*) FROM settings"
        (amount_in_database,) = await self.execute(query, single=True)

        amount_in_bot = len(self.bot.guilds)

        if amount_in_bot > amount_in_database:
            log.info(f'Server(s) are missing in the database: (bot) {amount_in_bot} vs {amount_in_database} (db)')

            query = "SELECT server_id FROM settings"
            servers_in_database = await self.execute(query)

            for guild in self.bot.guilds:

                if not any(str(guild.id) in i for i in servers_in_database):
                    log.info(f'Creating entry for the guild "{guild.name}" ({guild.id}) because it was not found.')

                    query = "INSERT INTO settings (server_id) VALUES (%s)"
                    params = (str(guild.id),)

                    result = await self.execute(query, params, rowcount=True)
                    if result:
                        log.info(f'Successfully inserted "{guild.name}" ({guild.id})')
                    else:
                        log.info(f'Failed to insert "{guild.name}" ({guild.id})')

        else:
            log.info("Assuming all servers has an entry in the settings-table.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Database(bot))
