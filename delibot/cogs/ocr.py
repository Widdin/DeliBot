import re
from io import BytesIO
from typing import Literal

import aiohttp
import discord
import pytesseract
from PIL import Image
from discord import app_commands
from discord.ext import commands


class OCR(commands.Cog):
    """
    Commands for assigning Team-role and reading EX-raid images.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def set_team(self, interaction: discord.Interaction, team: Literal['Valor', 'Mystic', 'Instinct']):
        """
        Assigns a team to yourself.
        """

        # Retrieve translation from JSON.
        error, missing_role, missing_role_desc, team_already_assigned, team_already_assigned_desc, insufficient_perm, missing_perm, team_welcome, team_welcome_desc = await self.bot.get_cog(
            "Utils").get_translation(interaction.guild_id,
                                     "ERROR MISSING_ROLE MISSING_ROLE_DESC TEAM_ALREADY_ASSIGNED TEAM_ALREADY_ASSIGNED_DESC INSUFFICIENT_PERM MISSING_PERM TEAM_WELCOME TEAM_WELCOME_DESC")

        team_colors = {
            "Valor": discord.Colour.red(),
            "Instinct": discord.Colour.gold(),
            "Mystic": discord.Colour.blue()
        }

        team_images = {
            "Valor": "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/team_red.png",
            "Instinct": "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/team_yellow.png",
            "Mystic": "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/team_blue.png"
        }

        role = discord.utils.get(interaction.guild.roles, name=team)  # Uppercase
        if role is None:
            role = discord.utils.get(interaction.guild.roles, name=team.lower())  # Lowercase
            if role is None:
                embed = discord.Embed(title=f"{error} - {missing_role}",
                                      description=f"{team} {missing_role_desc}",
                                      color=discord.Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        for user_role in interaction.user.roles:
            if user_role.name.lower() in ['valor', 'instinct', 'mystic']:
                embed = discord.Embed(title=f"{error} - {team_already_assigned}",
                                      description=f"{team_already_assigned_desc}",
                                      color=discord.Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            embed = discord.Embed(title=f"{error} - {insufficient_perm}",
                                  description=f"{missing_perm}",
                                  color=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title=f"{team_welcome} {team.title()}!",
                              description=f"{interaction.user.mention} {team_welcome_desc}",
                              color=team_colors[team.title()])
        embed.set_thumbnail(url=team_images[team.title()])
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def scan_team(self, interaction: discord.Interaction, image: discord.Attachment):
        query = "SELECT profile_channel_id, exraid_channel_id FROM settings WHERE server_id = %s"
        params = (str(interaction.guild_id),)
        profile_channel_id, exraid_channel_id = await self.bot.db.execute(query, params, single=True)

        # Scan Profile Image
        if str(interaction.channel.id) == profile_channel_id:
            await self.ocr_team_image(interaction, image)
        else:
            channel = interaction.guild.get_channel(int(profile_channel_id)) if profile_channel_id is not None else None
            mention = channel.mention if channel is not None else "<not set, use set_profile_scan>"
            await interaction.response.send_message(f'You are not allowed to use this command here.\nUse the channel: {mention}.', ephemeral=True)

        # Scan Exraid Image
        # elif str(interaction.channel.id) == exraid_channel_id:
        #    await self.ocr_ex_image(image)

    async def exraid_exist(self, server_id: str, pokemon: str, time: str, day: str, location: str):
        query = "SELECT * FROM exraids WHERE server_id = %s AND pokemon = %s AND time = %s AND day = %s AND location = %s"
        params = (server_id, pokemon, time, day, location)

        result = await self.bot.db.execute(query, params, single=True)

        if result is None:
            return False
        else:
            return True

    async def ocr_ex_image(self, message, re_run: int = 0):
        # 10. August 10:00 - 12:00
        ger_pattern = '(\d+)(\.)(\s+)(\w+)(\s+)(\d+:\d+)(\s+)-(\s+)(\d+:\d+)'
        # 10 August 10:00 - 12:00
        eu_pattern = '(\d+)(\s+)(\w+)(\s+)(\d+:\d+)(\s+)-(\s+)(\d+:\d+)'
        # August 10 10:30 PM - 11:30 PM
        eng_pattern = '(\w+)(\s+)(\d+)(\s+)(\d+:\d+)(\s+|)(AM|PM)(\s+)-(\s+)(\d+:\d+)(\s+|)(AM|PM)'
        # 23 August 5:00 M - 5:45 M
        greek_pattern = '(\d+)(\s)(\w+)(\s)(\d+:\d+)(\s|)(\w)(\s)(\W+)(\s)(\d+:\d+)(\s|)(\w)'

        img_url = message.attachments[0].url

        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(img_url) as response:
                image_bytes = await response.read()

        with Image.open(BytesIO(image_bytes)) as my_image:
            w, h = my_image.size

            crop_w = w * 0.18
            crop_h = h * 0.61

            my_image = my_image.crop((crop_w, h * 0.1, w - crop_w, h - crop_h))
            my_image = my_image.convert('L')
            my_image = my_image.point(lambda x: 0 if x < 195 else 255, '1')

            if re_run == 0:
                txt = pytesseract.image_to_string(my_image).replace("—", "-")
                patterns = [eu_pattern, eng_pattern, ger_pattern]
            else:
                txt = pytesseract.image_to_string(my_image, lang="ell").replace("—", "-")
                patterns = [greek_pattern]

            block = txt.split("\n")

            for pattern in patterns:
                rg = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                m = rg.search(txt)

                if m:
                    s = m.start()
                    e = m.end()

                    date = txt[s:e]
                    break

            # Retrieve translation from JSON.
            image_failed, image_failed_desc, warning, raid_exist = await self.bot.get_cog("Utils").get_translation(
                message.guild.id, "IMAGE_FAILED IMAGE_FAILED_DESC WARNING RAID_EXIST")

            try:
                date_index = block.index(date)
                location = block[date_index + 2]
                date = date.split(" ")
            except:
                embed = discord.Embed(title=image_failed,
                                      description=image_failed_desc,
                                      color=discord.Color.red())
                try:
                    await message.channel.send(embed=embed, delete_after=20)
                except discord.Forbidden:
                    await message.author.send("DeliBot does not have the proper permissions to send messages.")
                    return
                except discord.HTTPException:
                    return

                # Run one more time with greek
                if re_run > 0:
                    return
                else:
                    await self.ocr_ex_image(message, 1)

                return

            # Delete greek double -- between time
            the_time = ' '.join(date[2:])
            if the_time.count('--') >= 1:
                the_time = the_time.replace('--', '-')

            existence = await self.exraid_exist(server_id=message.guild.id, pokemon="Regigigas",
                                                time=the_time, day=f"{date[0]} {date[1]}",
                                                location=str(location))

            # The raid doesn't exist, create it.
            if existence is False:

                ctx = discord.ext.commands.Context(bot=self.bot, message=message, prefix="?")
                await ctx.invoke(self.bot.get_command("exraid"), pokemon="Regigigas", time=the_time,
                                 day=f"{date[0]} {date[1]}", location=str(location), delete=False)

                embed = discord.Embed(description='Successfully created the EX-Raid!',
                                      color=discord.Color.green())
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await message.channel.send(embed=embed, delete_after=15)

                # Success reaction
                await message.add_reaction('✅')
                return

            # The raid already exists, don't create it.
            elif existence is True:

                embed = discord.Embed(title=warning, description=raid_exist, color=discord.Color.red())
                embed.set_footer(text="Auto-deleting in 15 seconds..")
                await message.channel.send(embed=embed, delete_after=15)

                # Failed reaction
                await message.add_reaction('❌')
                return

    async def ocr_team_image(self, interaction, attachment):
        img_url = attachment.url

        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(img_url) as response:
                image_bytes = await response.read()

        with Image.open(BytesIO(image_bytes)) as my_image:
            rgb = my_image.getpixel((1, my_image.size[1] * 0.5))

        target_colors = {"Valor": (255, 0, 0), "Instinct": (255, 255, 0), "Mystic": (0, 0, 255)}

        def color_difference(color1, color2):
            return sum([abs(component1 - component2) for component1, component2 in zip(color1, color2)])

        differences = [[color_difference(rgb, target_value), target_name] for target_name, target_value in target_colors.items()]
        differences.sort()
        my_color_name = differences[0][1]

        # Retrieve translation from JSON.
        error, missing_role, missing_role_desc, team_already_assigned, team_already_assigned_desc, insufficient_perm, missing_perm, team_welcome, team_welcome_desc = await self.bot.get_cog(
            "Utils").get_translation(interaction.guild.id,
                                     "ERROR MISSING_ROLE MISSING_ROLE_DESC TEAM_ALREADY_ASSIGNED TEAM_ALREADY_ASSIGNED_DESC INSUFFICIENT_PERM MISSING_PERM TEAM_WELCOME TEAM_WELCOME_DESC")

        role = discord.utils.get(interaction.guild.roles, name=f'{my_color_name}')  # Uppercase
        if role is None:
            role = discord.utils.get(interaction.guild.roles, name=f'{my_color_name.lower()}')  # Lowercase
            if role is None:
                embed = discord.Embed(title=f"{error} - {missing_role}",
                                      description=f"{my_color_name} {missing_role_desc}",
                                      color=discord.Colour.red())
                await interaction.response.send_message(embed=embed)
                return

        for author_role in interaction.user.roles:
            if author_role.name.lower() in ['valor', 'instinct', 'mystic']:
                embed = discord.Embed(title=f"{error} - {team_already_assigned}",
                                      description=team_already_assigned_desc,
                                      color=discord.Colour.red())
                await interaction.response.send_message(embed=embed)
                return

        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            embed = discord.Embed(title=f"{error} - {insufficient_perm}",
                                  description=missing_perm,
                                  color=discord.Colour.red())
            await interaction.response.send_message(embed=embed)
            return

        target_images = {
            "Valor": "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/team_red.png",
            "Instinct": "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/team_yellow.png",
            "Mystic": "https://raw.githubusercontent.com/ZeChrales/PogoAssets/master/static_assets/png/team_blue.png"
        }

        embed = discord.Embed(title=f"{team_welcome} {my_color_name}!",
                              description=f"{interaction.user.mention} {team_welcome_desc}",
                              color=discord.Color((rgb[0] << 16) + (rgb[1] << 8) + rgb[2]))
        embed.set_thumbnail(url=target_images[my_color_name])
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OCR(bot))
