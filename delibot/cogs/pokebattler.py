import asyncio
import json
import logging
import os
import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger()


class Pokebattler(commands.Cog):
    """
    Commands related to Pokebattler.
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.update_json())
        self.type_emoji = {'POKEMON_TYPE_BUG': '<:bug:495707181073694722>',
                           'POKEMON_TYPE_DARK': '<:dark:495707181249724416>',
                           'POKEMON_TYPE_DRAGON': '<:dragon:495707180797001739>',
                           'POKEMON_TYPE_ELECTRIC': '<:electric:495707181174358026>',
                           'POKEMON_TYPE_FAIRY': '<:fairy:495707181086408705>',
                           'POKEMON_TYPE_FIGHTING': '<:fighting:495707181237403648>',
                           'POKEMON_TYPE_FIRE': '<:fire:495707181384204288>',
                           'POKEMON_TYPE_FLYING': '<:flying:495707180847202305>',
                           'POKEMON_TYPE_GHOST': '<:ghost:495707181249855516>',
                           'POKEMON_TYPE_GRASS': '<:grass:495707180906053635>',
                           'POKEMON_TYPE_GROUND': '<:ground:495707181321289729>',
                           'POKEMON_TYPE_ICE': '<:ice:495707181283278848>',
                           'POKEMON_TYPE_NORMAL': '<:normal:495707181035945985>',
                           'POKEMON_TYPE_POISON': '<:poison:495707180838682635>',
                           'POKEMON_TYPE_PSYCHIC': '<:psychic:495707181317095425>',
                           'POKEMON_TYPE_ROCK': '<:rock:495707181203849216> ',
                           'POKEMON_TYPE_STEEL': '<:steel:495707181107118080> ',
                           'POKEMON_TYPE_WATER': '<:water:495707181224820756> '}

    @commands.command(name="c", aliases=["counter", "pvp"])
    async def c(self, ctx, league: str, pokemon: str, matchup: str = "counters", limit: int = 24):
        """
        Shows detailed information with counters on a specific Pokémon.
        **Leagues:** great (g), ultra (u), master (m), silph (s)
        **Match-ups:** general (g), counters (c)
        **Limit:** 1-24

        Examples:
        *!counter great umbreon*
        *!counter great umbreon counters 10*
        *!c g umbreon c 15*
        """

        await ctx.message.delete()

        # Capslock
        pokemon = pokemon.upper()

        LEAGUES = {
            "Great": ["COMBAT_LEAGUE_DEFAULT_GREAT",
                      "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pogo_great_league.png",
                      discord.Color.blue(), "Great"],
            "G": ["COMBAT_LEAGUE_DEFAULT_GREAT",
                  "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pogo_great_league.png",
                  discord.Color.blue(), "Great"],

            "Ultra": ["COMBAT_LEAGUE_DEFAULT_ULTRA",
                      "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pogo_ultra_league.png",
                      discord.Color.gold(), "Ultra"],
            "U": ["COMBAT_LEAGUE_DEFAULT_ULTRA",
                  "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pogo_ultra_league.png",
                  discord.Color.gold(), "Ultra"],

            "Master": ["COMBAT_LEAGUE_DEFAULT_MASTER",
                       "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pogo_master_league.png",
                       discord.Color.purple(), "Master"],
            "M": ["COMBAT_LEAGUE_DEFAULT_MASTER",
                  "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/pogo_master_league.png",
                  discord.Color.purple(), "Master"],

            "Silph": ["COMBAT_LEAGUE_SILPH_CUP", "https://silph.gg/img/badges/nightmare.png", discord.Color.orange(),
                      "Silph"],
            "S": ["COMBAT_LEAGUE_SILPH_CUP", "https://silph.gg/img/badges/nightmare.png", discord.Color.orange(),
                  "Silph"]
        }

        MATCHUP = {
            "General": ["TOP_DEFENDER_PVP", "General"],
            "G": ["TOP_DEFENDER_PVP", "General"],

            "Counters": ["POKEMON_PVP", "Counters"],
            "C": ["POKEMON_PVP", "Counter"]
        }

        url = f"https://fight.pokebattler.com/pvp/rankings/pokemon/leagues/{LEAGUES[league.title()][0]}/strategies/PVP/PVP?sort=WIN&filterType={MATCHUP[matchup.title()][0]}&filterValue={pokemon}&shieldStrategy=SHIELD_RANDOM&meta=DUAL_MOVE"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    json = await response.json()
                else:
                    embed = discord.Embed(title="Error",
                                          description="Something went wrong. Did you spell the Pokémon correctly?",
                                          color=discord.Color.red())
                    await ctx.send(embed=embed, delete_after=10)
                    return

        embed = discord.Embed(title=f"Counters for {pokemon.title()}", color=LEAGUES[league.title()][2])
        embed.set_thumbnail(url=LEAGUES[league.title()][1])
        embed.set_footer(text="Counters provided by Pokebattler", icon_url="https://i.imgur.com/o1QFd4z.png")

        embed.description = f"**League:** {LEAGUES[league.title()][3]}-league\n**Match-up:** {MATCHUP[matchup.title()][1]}\n**Limit:** {limit}\n"

        counter = 1
        for entry in reversed(json['attackers'][0]['byMove'][0]['defenders']):

            move_type1 = await self.get_move_info(entry['byMove'][0]['move1'])
            move_type2 = await self.get_move_info(entry['byMove'][0]['move2'])
            move_type3 = await self.get_move_info(entry['byMove'][0]['move3'])

            name = (entry['pokemonId']).replace("_", " ").title()

            if move_type1 is not None:
                move1 = f"{self.type_emoji[move_type1['type']]} " + (entry['byMove'][0]['move1']).replace("_",
                                                                                                          " ").title()
            else:
                move1 = ":question: " + (entry['byMove'][0]['move1']).replace("_", " ").title()
            if move_type2 is not None:
                move2 = f"{self.type_emoji[move_type2['type']]} " + (entry['byMove'][0]['move2']).replace("_",
                                                                                                          " ").title()
            else:
                move2 = ":question: " + (entry['byMove'][0]['move2']).replace("_", " ").title()
            if move_type3 is not None:
                move3 = f"{self.type_emoji[move_type3['type']]} " + (entry['byMove'][0]['move3']).replace("_",
                                                                                                          " ").title()
            else:
                move3 = ":question: " + (entry['byMove'][0]['move3']).replace("_", " ").title()

            embed.add_field(name=f"{counter}. {name}", value=f"{move1}\n{move2}\n{move3}\n\u200b", inline=True)

            # Limit the amount
            if counter >= limit:
                break

            counter += 1

        await ctx.send(embed=embed)

    @commands.command(name="pokebattler", aliases=["pb", "battle"])
    async def pokebattler(self, ctx, pokemon: str):
        """
        Shows detailed information with counters on a specific Raid-boss.
        Example: *!pokebattler snorlax*
        """
        # Battle Options
        WEATHERS = {'1': 'NO_WEATHER', '2': 'CLEAR', '3': 'RAINY', '4': 'PARTLY_CLOUDY', '5': 'OVERCAST', '6': 'WINDY',
                    '7': 'SNOW', '8': 'FOG'}
        ATTACK_STRATS = {'1': 'CINEMATIC_ATTACK_WHEN_POSSIBLE', '2': 'DODGE_SPECIALS', '3': 'DODGE_WEAVE_CAUTIOUS'}
        DODGE_STRATS = {'1': 'DODGE_100', '2': 'DODGE_REACTION_TIME', '3': 'DODGE_REACTION_TIME2', '4': 'DODGE_25'}
        FRIEND_LEVELS = {'1': 'FRIENDSHIP_LEVEL_0', '2': 'FRIENDSHIP_LEVEL_1', '3': 'FRIENDSHIP_LEVEL_2',
                         '4': 'FRIENDSHIP_LEVEL_3', '5': 'FRIENDSHIP_LEVEL_4'}

        # Delete command
        await ctx.message.delete()

        # No ID exploit
        if pokemon.isdigit():
            return

        # Ask for weather
        embed = discord.Embed(title="Choose Weather:")
        embed.add_field(name="1. <:weather_no_weather:507338776297865234> Extreme", value="\u200b", inline=False)
        embed.add_field(name="2. <:weather_clear:507338079103746058> Sunny/Clear", value="\u200b", inline=False)
        embed.add_field(name="3. <:weather_rainy:507338777052577792> Rainy", value="\u200b", inline=False)
        embed.add_field(name="4. <:weather_partly_cloudy:507338777107234827> Partly Cloudy", value="\u200b",
                        inline=False)
        embed.add_field(name="5. <:weather_overcast:507338776767627285> Cloudy", value="\u200b", inline=False)
        embed.add_field(name="6. <:weather_windy:507338776469569537> Windy", value="\u200b", inline=False)
        embed.add_field(name="7. <:weather_snow:507338777077874689> Snow", value="\u200b", inline=False)
        embed.add_field(name="8. <:weather_fog:507338777266487296> Fog", value="\u200b", inline=False)
        embed.set_thumbnail(url="https://techflourish.com/images/clipart-sun-and-clouds-and-rain.png")
        embed.set_footer(text="Enter a Number Below:")
        message_1 = await ctx.message.channel.send(embed=embed)

        def weather_check(message):
            return message.content.isdigit() and message.author.id == ctx.message.author.id

        try:
            weather_msg = await self.bot.wait_for('message', timeout=120, check=weather_check)
        except asyncio.TimeoutError:
            return

        await message_1.delete()
        await weather_msg.delete()

        # Ask for Attack Strategy
        embed = discord.Embed(title="Choose Attack Strategy:")
        embed.add_field(name="1. No Dodging", value="\u200b", inline=False)
        embed.add_field(name="2. Dodge Specials PRO", value="\u200b", inline=False)
        embed.add_field(name="3. Dodge All Weave", value="\u200b", inline=False)
        embed.set_thumbnail(url="http://learnobots.com/wp-content/uploads/2017/06/Icon-3.png")
        embed.set_footer(text="Enter a Number Below:")
        message_2 = await ctx.message.channel.send(embed=embed)

        try:
            attack_msg = await self.bot.wait_for('message', timeout=120, check=weather_check)
        except asyncio.TimeoutError:
            return

        await message_2.delete()
        await attack_msg.delete()

        # Ask for Dodge Strategy
        if attack_msg.content in ["2", "3"]:
            embed = discord.Embed(title="Choose Dodge Strategy:")
            embed.add_field(name="1. Perfect Dodging", value="\u200b", inline=False)
            embed.add_field(name="2. Realistic Dodging", value="\u200b", inline=False)
            embed.add_field(name="3. Realistic Dodging PRO", value="\u200b", inline=False)
            embed.add_field(name="4. 25% Dodging", value="\u200b", inline=False)
            embed.set_thumbnail(url="http://learnobots.com/wp-content/uploads/2017/06/Icon-3.png")
            embed.set_footer(text="Enter a Number Below:")
            message_3 = await ctx.message.channel.send(embed=embed)

            try:
                dodge_msg = await self.bot.wait_for('message', timeout=120, check=weather_msg)
            except asyncio.TimeoutError:
                return

            await message_3.delete()
            await dodge_msg.delete()

            weather = WEATHERS[weather_msg.content]
            attack = ATTACK_STRATS[attack_msg.content]
            dodge = DODGE_STRATS[dodge_msg.content]

        else:
            weather = WEATHERS[weather_msg.content]
            attack = ATTACK_STRATS[attack_msg.content]
            dodge = DODGE_STRATS['2']

        # Ask for Friend Level
        embed = discord.Embed(title="Choose Friend Level:")
        embed.add_field(name="1. Not Friends", value=":black_heart::black_heart::black_heart::black_heart:",
                        inline=False)
        embed.add_field(name="2. Good Friends", value=":heart::black_heart::black_heart::black_heart:", inline=False)
        embed.add_field(name="3. Great Friends", value=":heart::heart::black_heart::black_heart:", inline=False)
        embed.add_field(name="4. Ultra Friends", value=":heart::heart::heart::black_heart:", inline=False)
        embed.add_field(name="5. Best Friends", value=":heart::heart::heart::heart:", inline=False)
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/Badge_Friendship_GOLD_01.png")
        message_4 = await ctx.message.channel.send(embed=embed)

        try:
            friend_msg = await self.bot.wait_for('message', timeout=120, check=weather_check)
        except asyncio.TimeoutError:
            return

        await message_4.delete()
        await friend_msg.delete()

        friend = FRIEND_LEVELS[friend_msg.content]

        await self.pb_information(user=ctx.message.channel, server_id=ctx.message.guild.id,
                                  channel_id=ctx.message.channel.id, message_id=pokemon, WEATHER=weather,
                                  ATTACK_STRAT=attack, DODGE_STRAT=dodge, FRIEND_LEVEL=friend)

    async def pb_information(self, user: discord.Member, server_id: str, channel_id: str, message_id: str,
                             WEATHER: str = "NO_WEATHER", ATTACK_STRAT: str = "CINEMATIC_ATTACK_WHEN_POSSIBLE",
                             DODGE_STRAT: str = "DODGE_REACTION_TIME", FRIEND_LEVEL: str = "FRIENDSHIP_LEVEL_0"):

        # Invoked from message.
        if isinstance(message_id, int):

            query = "SELECT pokemon FROM raids WHERE server_id = %s AND channel_id = %s AND message_id = %s"
            params = (server_id, channel_id, message_id)
            (pokemon,) = await self.bot.db.execute(query, params, single=True)

        # Invoked by command
        else:
            pokemon = message_id

        alola = False
        if "alola" in pokemon or "alolan" in pokemon:
            pokemon = pokemon.split(" ")[1]
            alola = True
            pokemon_eng = f'{pokemon.upper()}_ALOLA_FORM'
        else:
            pokemon_id = await self.bot.get_cog("Utils").get_pokemon_id(pokemon)
            pokemon_eng = await self.bot.get_cog("Utils").get_pokemon_name(pokemon_id)

        boss = pokemon.title()

        try:
            raid_tier = await self.get_tier_of(pokemon_eng)
        except AttributeError:
            return

        try:
            url = f"https://fight.pokebattler.com/raids/defenders/{pokemon_eng.upper()}/levels/{raid_tier}/attackers/levels/30/strategies/{ATTACK_STRAT}/DEFENSE_RANDOM_MC?sort=OVERALL&weatherCondition={WEATHER}&dodgeStrategy={DODGE_STRAT}&aggregation=AVERAGE&randomAssistants=-1&friendLevel={FRIEND_LEVEL}"
        except KeyError:
            await user.send("Error - This Pokémon has not yet been added to the list OR It does not exist in raids.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    json = await response.json()
                else:
                    embed = discord.Embed(title="Error", description=f"{boss} does not exist in raids.",
                                          color=discord.Colour.blue())
                    await user.send(embed=embed)
                    return

        top_24 = json['attackers'][0]['randomMove']['defenders']

        boss_quick_moves = []
        boss_charge_moves = []

        for i in json['attackers'][0]['byMove']:
            if i['move1'] not in boss_quick_moves:
                boss_quick_moves.append(i['move1'])

            if i['move2'] not in boss_charge_moves:
                boss_charge_moves.append(i['move2'])

        boss_quick = ""
        boss_charge = ""

        for move in boss_quick_moves:
            quick = await self.get_move_info(move)
            boss_quick += f"{self.type_emoji[quick['type']]} {quick['name']}\n"

        for move in boss_charge_moves:
            charge = await self.get_move_info(move)
            boss_charge += f"{self.type_emoji[charge['type']]} {charge['name']}\n"

        embed = discord.Embed(color=discord.Colour.blue())

        stats_20 = await self.get_cp_and_type(pokemon_eng, 0.59740001)
        stats_25 = await self.get_cp_and_type(pokemon_eng, 0.667934)

        boss_types = ""

        for type in stats_20['types']:
            boss_types += f"{self.type_emoji[type]} {type.replace('POKEMON_TYPE_', '').title()}\n"

        embed.add_field(name="CP Ranges",
                        value=f"**L20:** {stats_20['min_cp']} - {stats_20['max_cp']}\n**L25:** {stats_25['min_cp']} - {stats_25['max_cp']}",
                        inline=True)
        embed.add_field(name="Type", value=f"{boss_types}", inline=True)
        embed.add_field(name="Quick Moves", value=f"{boss_quick}", inline=True)
        embed.add_field(name="Charge Moves", value=f"{boss_charge}", inline=True)

        display_weather = WEATHER.replace("_", " ").lower()
        embed.add_field(name="Counters",
                        value=f"Given a **unknown moveset** and **{display_weather}**, the following are the best known counters:",
                        inline=False)

        i = 0
        for pokemon in reversed(top_24):
            i += 1
            name = pokemon['pokemonId'].replace('_', ' ').title()
            quick = await self.get_move_info(pokemon['byMove'][-1]['move1'])
            charge = await self.get_move_info(pokemon['byMove'][-1]['move2'])
            embed.add_field(
                name=f"{i}. {name}",
                value=f"{self.type_emoji[quick['type']]} {quick['name']}\n{self.type_emoji[charge['type']]} {charge['name']}",
                inline=True)

            if i == 5:
                break

        if alola:
            images = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id, is_alola=True)
            embed.set_author(name=f"Alola {boss} {raid_tier.replace('_', ' ').title()}", icon_url=images['icon_url'])

        else:
            images = await self.bot.get_cog("Utils").get_pokemon_image_url(pokemon_id)
            embed.set_author(name=f"{boss} {raid_tier.replace('_', ' ').title()}", icon_url=images['icon_url'])

        embed.set_thumbnail(url=images['url'])
        embed.set_footer(text="Counters provided by Pokebattler.",
                         icon_url="https://articles.pokebattler.com/wp-content/uploads/2017/11/Asset-2.png")

        await user.send(embed=embed)

    @staticmethod
    async def get_move_info(move_name):
        with open('json/moves.json') as json_file:
            data = json.load(json_file)
            json_file.close()

        for move in data['move']:
            try:
                if move['moveId'] == move_name:
                    return {'type': move['type'],
                            'name': move['moveId'].replace('FAST', '').replace('_', ' ').title()}
            except KeyError:
                pass

        return None

    @staticmethod
    async def get_cp_and_type(pokemon_name: str, cp_multiplier: float):
        with open('json/pokemon.json') as json_file:
            data = json.load(json_file)
            json_file.close()

        for pokemon in data['pokemon']:
            if pokemon['pokemonId'].title() == pokemon_name:
                base_attack = float(pokemon['stats']['baseAttack'])
                base_defense = float(pokemon['stats']['baseDefense'])
                base_stamina = float(pokemon['stats']['baseStamina'])

                max_cp = int(((base_attack + 15.0) * (base_defense + 15.0) ** 0.5 * (
                        base_stamina + 15.0) ** 0.5 * cp_multiplier ** 2.0) / 10.0)
                min_cp = int(((base_attack + 10.0) * (base_defense + 10.0) ** 0.5 * (
                        base_stamina + 10.0) ** 0.5 * cp_multiplier ** 2.0) / 10.0)

                try:
                    types = {pokemon['type'], pokemon['type2']}
                except KeyError:
                    types = {pokemon['type']}

                return {'types': types,
                        'max_cp': max_cp,
                        'min_cp': min_cp}

        return None

    @staticmethod
    async def get_tier_of(pokemon: str):
        filepath = os.path.join('json/raid_bosses.json')
        with open(filepath, 'r', encoding='utf8') as f:
            data = json.load(f)

        # For each tier
        for i in range(0, 14):

            current_tier = data['tiers'][i]['tier']

            # Each mon in this tier
            for mons in data['tiers'][i]['raids']:

                if mons['pokemon'] == pokemon.upper():

                    if current_tier == "RAID_LEVEL_5_LEGACY":
                        current_tier = "RAID_LEVEL_5"

                    return current_tier

        return None

    async def update_json(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            # Only update if the file is older than 1 day
            if not await self.bot.get_cog("Utils").is_modified_older_than('json/raid_bosses.json', days=1):
                log.info("Skipping update because the JSON was recently modified.")

            else:
                log.info("Updating JSON for raid_bosses, moves and pokemon.")

                info = {
                    'https://fight.pokebattler.com/raids': 'json/raid_bosses.json',
                    'https://fight.pokebattler.com/moves': 'json/moves.json',
                    'https://fight.pokebattler.com/pokemon': 'json/pokemon.json'
                }

                for url in info:
                    data = await self.get_json(url)
                    if data:
                        file_path = info[url]
                        await self.bot.get_cog("Utils").dump_json(file_path, data)

                log.info("Successfully updated.")

            await asyncio.sleep(86400)

    @staticmethod
    async def get_json(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pokebattler(bot))
