from pydoc import describe
import discord
import os
import logging
from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button, View, Select
from discord import app_commands
import asyncio
import sys
from app.bot.helper.confighelper import (
    PLEXINVITER_VERSION,
    switch,
    Discord_bot_token,
    plex_roles,
)
import app.bot.helper.confighelper as confighelper
from app.bot.helper.message import *
from requests import ConnectTimeout
from plexapi.myplex import MyPlexAccount

# Configure logging to hide gateway logs
logging.getLogger("discord.gateway").setLevel(logging.ERROR)
logging.getLogger("discord.client").setLevel(logging.ERROR)
logging.getLogger("discord.http").setLevel(logging.WARNING)

maxroles = 10

if switch == 0:
    print("Missing Config.")
    sys.exit()


class Bot(commands.Bot):
    def __init__(self) -> None:
        print("Initializing Discord bot")
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=".", intents=intents)

    async def on_ready(self):
        print("Bot is online.")
        for guild in self.guilds:
            print("Syncing commands to " + guild.name)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_guild_join(self, guild):
        print(f"Joined guild {guild.name}")
        print(f"Syncing commands to {guild.name}")
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def setup_hook(self):
        print("Loading media server connectors")
        await self.load_extension(f"app.bot.cogs.app")


bot = Bot()


async def reload():
    await bot.reload_extension(f"app.bot.cogs.app")


async def getuser(interaction, server, type):
    value = None
    await interaction.user.send("Please reply with your {} {}:".format(server, type))
    while value == None:

        def check(m):
            return m.author == interaction.user and not m.guild

        try:
            value = await bot.wait_for("message", timeout=200, check=check)
            return value.content
        except asyncio.TimeoutError:
            message = "Timed Out. Try again."
            return None


plex_commands = app_commands.Group(
    name="plexsettings", description="PlexInviter Plex commands"
)


@plex_commands.command(
    name="addrole", description="Add a role to automatically add users to Plex"
)
@app_commands.checks.has_permissions(administrator=True)
async def plexroleadd(interaction: discord.Interaction, role: discord.Role):
    if len(plex_roles) <= maxroles:
        # Do not add roles multiple times.
        if role.name in plex_roles:
            await embederror(
                interaction.response, f'Plex role "{role.name}" already added.'
            )
            return

        plex_roles.append(role.name)
        saveroles = ",".join(plex_roles)
        confighelper.change_config("plex_roles", saveroles)
        await interaction.response.send_message(
            "Updated Plex roles. Bot is restarting. Please wait.", ephemeral=True
        )
        print("Plex roles updated. Restarting bot, Give it a few seconds.")
        await reload()
        print("Bot has been restarted. Give it a few seconds.")


@plex_commands.command(
    name="removerole", description="Stop adding users with a role to Plex"
)
@app_commands.checks.has_permissions(administrator=True)
async def plexroleremove(interaction: discord.Interaction, role: discord.Role):
    if role.name not in plex_roles:
        await embederror(
            interaction.response, f'"{role.name}" is currently not a Plex role.'
        )
        return
    plex_roles.remove(role.name)
    confighelper.change_config("plex_roles", ",".join(plex_roles))
    await interaction.response.send_message(
        f'PlexInviter will stop auto-adding "{role.name}" to Plex', ephemeral=True
    )


@plex_commands.command(
    name="listroles",
    description="List all roles whose members will be automatically added to Plex",
)
@app_commands.checks.has_permissions(administrator=True)
async def plexrolels(interaction: discord.Interaction):
    await interaction.response.send_message(
        "The following roles are being automatically added to Plex:\n"
        + ", ".join(plex_roles),
        ephemeral=True,
    )


@plex_commands.command(name="setup", description="Setup Plex integration")
@app_commands.checks.has_permissions(administrator=True)
async def setupplex(
    interaction: discord.Interaction,
    username: str,
    password: str,
    server_name: str,
    base_url: str = "",
    save_token: bool = True,
):
    await interaction.response.defer()
    try:
        account = MyPlexAccount(username, password)
        plex = account.resource(server_name).connect()
    except Exception as e:
        if str(e).startswith("(429)"):
            await embederror(
                interaction.followup, "Too many requests. Please try again later."
            )
            return

        await embederror(
            interaction.followup,
            "Could not connect to Plex server. Please check your credentials.",
        )
        return

    if save_token:
        # Save new config entries
        confighelper.change_config(
            "plex_base_url", plex._baseurl if base_url == "" else base_url
        )
        confighelper.change_config("plex_token", plex._token)
        confighelper.change_config("plex_server_name", server_name)

        # Delete old config entries
        confighelper.change_config("plex_user", "")
        confighelper.change_config("plex_pass", "")
    else:
        # Save new config entries
        confighelper.change_config("plex_user", username)
        confighelper.change_config("plex_pass", password)
        confighelper.change_config("plex_server_name", server_name)

        # Delete old config entries
        confighelper.change_config("plex_base_url", "")
        confighelper.change_config("plex_token", "")

    print("Plex authentication details updated. Restarting bot.")
    await interaction.followup.send(
        "Plex authentication details updated. Restarting bot. Please wait.\n"
        + "Please check logs and make sure you see the line: `Logged into plex`. If not run this command again and make sure you enter the right values.",
        ephemeral=True,
    )
    await reload()
    print("Bot has been restarted. Give it a few seconds.")


@plex_commands.command(
    name="setuplibs", description="Setup libraries that new users can access"
)
@app_commands.checks.has_permissions(administrator=True)
async def setupplexlibs(interaction: discord.Interaction, libraries: str):
    if not libraries:
        await embederror(interaction.response, "libraries string is empty.")
        return
    else:
        # Do some fancy python to remove spaces from libraries string, but only where wanted.
        libraries = ",".join(list(map(lambda lib: lib.strip(), libraries.split(","))))
        confighelper.change_config("plex_libs", str(libraries))
        print("Plex libraries updated. Restarting bot. Please wait.")
        await interaction.response.send_message(
            "Plex libraries updated. Please wait a few seconds for bot to restart.",
            ephemeral=True,
        )
        await reload()
        print("Bot has been restarted. Give it a few seconds.")


# Enable / Disable Plex integration
@plex_commands.command(name="enable", description="Enable auto-adding users to Plex")
@app_commands.checks.has_permissions(administrator=True)
async def enableplex(interaction: discord.Interaction):
    if confighelper.USE_PLEX:
        await interaction.response.send_message("Plex already enabled.", ephemeral=True)
        return
    confighelper.change_config("plex_enabled", True)
    print("Plex enabled, reloading server")
    await reload()
    confighelper.USE_PLEX = True
    await interaction.response.send_message(
        "Plex enabled. Restarting server. Give it a few seconds.", ephemeral=True
    )
    print("Bot has restarted. Give it a few seconds.")


@plex_commands.command(name="disable", description="Disable adding users to Plex")
@app_commands.checks.has_permissions(administrator=True)
async def disableplex(interaction: discord.Interaction):
    if not confighelper.USE_PLEX:
        await interaction.response.send_message(
            "Plex already disabled.", ephemeral=True
        )
        return
    confighelper.change_config("plex_enabled", False)
    print("Plex disabled, reloading server")
    await reload()
    confighelper.USE_PLEX = False
    await interaction.response.send_message(
        "Plex disabled. Restarting server. Give it a few seconds.", ephemeral=True
    )
    print("Bot has restarted. Give it a few seconds.")


bot.tree.add_command(plex_commands)

bot.run(Discord_bot_token)
