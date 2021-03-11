import asyncio
import time
from datetime import timedelta, datetime

import discord
from discord.ext import commands


class Research(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Start background tasks
        self.bot.loop.create_task(self._init_delete_old_research())

    async def _init_delete_old_research(self):
        gmt_dict = {'00:00': '+2', '01:00': '+1', '02:00': '+0', '03:00': '-1', '04:00': '-2', '05:00': '-3',
                    '06:00': '-4', '07:00': '-5', '08:00': '-6', '09:00': '-7', '10:00': '-8', '11:00': '-9',
                    '12:00': '-10', '13:00': '-11', '14:00': '+12', '15:00': '+11', '16:00': '+10', '17:00': '+9',
                    '18:00': '+8', '19:00': '+7', '20:00': '+6', '21:00': '+5', '22:00': '+4', '23:00': '+3'}

        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            async with self.bot.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM research")
                    results = await cur.fetchall()

            for result in results:
                if result[8] == gmt_dict[time.strftime("%H:00")] or result[9] < datetime.now() + timedelta(days=-1):
                    async with self.bot.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "DELETE FROM research WHERE server_id = %s AND channel_id = %s AND message_id = %s",
                                (result[0], result[1], result[2]))

                            try:
                                await self.bot.http.delete_message(result[1], result[2])
                            except discord.NotFound:
                                pass
                            except discord.Forbidden:
                                pass
                            except discord.HTTPException:
                                pass

            await asyncio.sleep(3600)

    @commands.command(pass_context=True, aliases=["rs", "quest", "Quest", "Research", "RS", "q", "Q"])
    async def research(self, ctx, *, info: str = None):

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        # Create the user in the database if he doesn't exist.
        # await self.bot.get_cog("Utils").create_user_if_not_exist(ctx.message.server.id, ctx.message.author.id)

        # research_created +1 for the user
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE users SET research_created = research_created + 1 WHERE server_id = %s AND user_id = %s",
                    (str(ctx.message.guild.id), str(ctx.message.author.id)))

        # Retrieve translation from JSON.
        what_quest, what_reward, what_pokestop, type_below, quest_creation, quest, quest_reward, thank_you, raid_by = await self.bot.get_cog(
            "Utils").get_translation(ctx.message.guild.id,
                                     "WHAT_QUEST WHAT_REWARD WHAT_POKESTOP TYPE_BELOW QUEST_CREATION QUEST QUEST_REWARD THANK_YOU RAID_BY")

        try:
            if info is None:
                # No input given, ask the user in PM
                embed = discord.Embed(title=what_quest, color=discord.Colour.red())
                embed.set_footer(text=type_below)
                await ctx.message.author.send(embed=embed)

                def check(message):
                    return message.author.id == ctx.author.id

                msg_quest = await self.bot.wait_for("message", timeout=30.0, check=check)
                questText = msg_quest.content

                embed = discord.Embed(title=what_reward, color=discord.Colour.orange())
                embed.set_footer(text=type_below)
                await ctx.message.author.send(embed=embed)

                msg_reward = await self.bot.wait_for("message", timeout=30.0, check=check)
                rewardText = msg_reward.content

                embed = discord.Embed(title=what_pokestop, color=discord.Colour.green())
                embed.set_footer(text=type_below)
                await ctx.message.author.send(embed=embed)

                msg_pokestop = await self.bot.wait_for("message", timeout=30.0, check=check)
                pokestopText = msg_pokestop.content

                embed = discord.Embed(title=f"{thank_you}!",
                                      description=f"{quest_creation} {ctx.message.channel.name}",
                                      color=discord.Colour.green())
                await ctx.message.author.send(embed=embed)
            else:
                questText, rewardText, pokestopText = info.split(",")
        except ValueError:
            try:
                await ctx.channel.send(
                    ctx.message.author.mention + ": Missing required argument.\n```!research {quest} , {reward} , {pokestop}```",
                    delete_after=10)
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

        pokestopText = pokestopText.lower().lstrip()

        # Retrieve pokestop location
        stop_name = await self.bot.get_cog("Utils").get_pokestop(ctx.message.guild.id, pokestopText)

        # Embed
        embed = discord.Embed(color=discord.Colour.gold())
        embed.set_author(name="Field Research Quest",
                         icon_url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/QuestSymbol.png")
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/QuestReward.png")
        embed.add_field(name=quest, value="\u2022 " + questText.title())
        embed.add_field(name=quest_reward, value="\u2022 " + rewardText.title())
        embed.add_field(name="Pokéstop", value=f"\u2022 {stop_name}")
        embed.set_footer(text=f"{raid_by}: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)

        try:
            msg = await ctx.channel.send(embed=embed)
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return

        try:
            await msg.add_reaction('\U0000274c')
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        await self.insert_database(ctx.message.guild.id, ctx.message.channel.id, msg.id, ctx.message.author.id,
                                   ctx.message.author, questText, rewardText, pokestopText)

    async def insert_database(self, server_id: str, channel_id: str, message_id: str, user_id: str, author: str,
                              quest: str, reward: str, pokestop: str):

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT timezone FROM settings WHERE server_id = %s", (server_id,))
                (GMT,) = await cur.fetchone()

                await cur.execute(
                    "INSERT INTO research (server_id, channel_id, message_id, user_id, author, quest, reward, pokestop, GMT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (server_id, channel_id, message_id, user_id, str(author), quest, reward, pokestop, GMT))
                await conn.commit()


def setup(bot):
    bot.add_cog(Research(bot))
