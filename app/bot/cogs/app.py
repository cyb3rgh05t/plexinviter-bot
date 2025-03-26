from pickle import FALSE
from app.bot.helper.textformat import bcolors
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta, datetime
import asyncio
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import app.bot.helper.db as db
import app.bot.helper.plexhelper as plexhelper
import texttable
from app.bot.helper.message import *
from app.bot.helper.confighelper import *

CONFIG_PATH = "app/config/config.ini"
BOT_SECTION = "bot_envs"

plex_configured = True

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

plex_token_configured = True
try:
    PLEX_TOKEN = config.get(BOT_SECTION, "plex_token")
    PLEX_BASE_URL = config.get(BOT_SECTION, "plex_base_url")
except:
    print("No Plex auth token details found")
    plex_token_configured = False

# Get Plex config
try:
    PLEXUSER = config.get(BOT_SECTION, "plex_user")
    PLEXPASS = config.get(BOT_SECTION, "plex_pass")
    PLEX_SERVER_NAME = config.get(BOT_SECTION, "plex_server_name")
except:
    print("No Plex login info found")
    if not plex_token_configured:
        print("Could not load plex config")
        plex_configured = False

# Get Plex roles config
try:
    plex_roles = config.get(BOT_SECTION, "plex_roles")
except:
    plex_roles = None
if plex_roles:
    plex_roles = list(plex_roles.split(","))
else:
    plex_roles = []

# Get Plex libs config
try:
    Plex_LIBS = config.get(BOT_SECTION, "plex_libs")
except:
    Plex_LIBS = None
if Plex_LIBS is None:
    Plex_LIBS = ["all"]
else:
    Plex_LIBS = list(Plex_LIBS.split(","))

# Get Enable config
try:
    USE_PLEX = config.get(BOT_SECTION, "plex_enabled")
    USE_PLEX = USE_PLEX.lower() == "true"
except:
    print("Could not get Plex enable config. Defaulting to False")
    USE_PLEX = False

if USE_PLEX and plex_configured:
    try:
        print("Connecting to Plex......")
        if plex_token_configured and PLEX_TOKEN and PLEX_BASE_URL:
            print("Using Plex auth token")
            plex = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
        else:
            print("Using Plex login info")
            account = MyPlexAccount(PLEXUSER, PLEXPASS)
            plex = account.resource(
                PLEX_SERVER_NAME
            ).connect()  # returns a PlexServer instance
        print("Logged into Plex!")
    except Exception as e:
        # probably rate limited.
        print(
            "Error with Plex login. Please check Plex authentication details. If you have restarted the bot multiple times recently, this is most likely due to being ratelimited on the Plex API. Try again in 10 minutes."
        )
        print(f"Error: {e}")
else:
    print(
        f"Plex {'disabled' if not USE_PLEX else 'not configured'}. Skipping Plex login."
    )


class app(commands.Cog):
    # App command groups
    plex_commands = app_commands.Group(
        name="plex", description="PlexInviter Plex commands"
    )
    bot_commands = app_commands.Group(
        name="bot", description="PlexInviter general commands"
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ascii_logo = r"""

 ██████╗██╗   ██╗██████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
██╔════╝╚██╗ ██╔╝██╔══██╗╚════██╗██╔══██╗██╔════╝ ██║  ██║██╔═████╗██╔════╝╚══██╔══╝
██║      ╚████╔╝ ██████╔╝ █████╔╝██████╔╝██║  ███╗███████║██║██╔██║███████╗   ██║   
██║       ╚██╔╝  ██╔══██╗ ╚═══██╗██╔══██╗██║   ██║██╔══██║████╔╝██║╚════██║   ██║   
╚██████╗   ██║   ██████╔╝██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   
 ╚═════╝   ╚═╝   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
    """
        print(ascii_logo)
        print("=====================================================")
        print(f"PlexInviter Version {PLEXINVITER_VERSION}")
        print(f"Author: cyb3rgh05t https://github.com/cyb3rgh05t/\n")
        print("=====================================================")
        print(f"To support this project, please visit")
        print(f"https://github.com/cyb3rgh05t/plexinviter-bot")
        print("=====================================================")
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

        # TODO: Make these debug statements work. roles are currently empty arrays if no roles assigned.
        if plex_roles is None:
            print(
                "Configure Plex roles to enable auto invite to Plex after a role is assigned."
            )

    async def getemail(self, after):
        email = None
        await embedemail(
            after,
            "Antworte einfach mit deiner **PLEX Mail**, damit ich dich bei **"
            + PLEX_SERVER_NAME
            + "** hinzufügen kann!",
        )
        while email == None:

            def check(m):
                return m.author == after and not m.guild

            try:
                email = await self.bot.wait_for("message", timeout=86400, check=check)
                if plexhelper.verifyemail(str(email.content)):
                    return str(email.content)
                else:
                    email = None
                    message = "<:rejected:995614671128244224> Ungültige **Plex Mail**. Bitte gib nur deine **Plex Mail** ein und nichts anderes."
                    await embederroremail(after, message)
                    continue
            except asyncio.TimeoutError:
                message = (
                    "⏳ Zeitüberschreitung\n\nWende dich an den **"
                    + PLEX_SERVER_NAME
                    + "** Admin <@408885990971670531> damit der dich manuell hinzufügen kann."
                )
                await embederror(after, message)
                return None

    async def addtoplex(self, email, response):
        if plexhelper.verifyemail(email):
            if plexhelper.plexinviter(plex, email, Plex_LIBS):
                await embedinfo(
                    response,
                    "<:approved:995615632961847406> Deine **Plex Mail** wurde zu **"
                    + PLEX_SERVER_NAME
                    + "** hinzugefügt",
                )
                return True
            else:
                await embederror(
                    response,
                    "<:rejected:995614671128244224> There was an error adding this email address. Check logs.",
                )
                return False
        else:
            await embederror(response, "<:rejected:995614671128244224> Invalid email.")
            return False

    async def removefromplex(self, email, response):
        if plexhelper.verifyemail(email):
            if plexhelper.plexremove(plex, email):
                await embedinfo(
                    response,
                    "<:approved:995615632961847406> This email address has been removed from **"
                    + PLEX_SERVER_NAME
                    + "**.",
                )
                return True
            else:
                await embederror(
                    response,
                    "<:rejected:995614671128244224> There was an error removing this email address. Check logs.",
                )
                return False
        else:
            await embederror(response, "<:rejected:995614671128244224> Invalid email.")
            return False

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if plex_roles is None:
            return
        roles_in_guild = after.guild.roles
        role = None

        plex_processed = False

        # Check Plex roles
        if plex_configured and USE_PLEX:
            for role_for_app in plex_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Plex role was added
                    if role is not None and (
                        role in after.roles and role not in before.roles
                    ):
                        email = await self.getemail(after)
                        if email is not None:
                            await embedinfo(
                                after, "**GOTCHA**, wir werden deine Email bearbeiten!"
                            )
                            if plexhelper.plexinviter(plex, email, Plex_LIBS):
                                db.save_user_email(str(after.id), email)
                                await asyncio.sleep(5)
                                await embedinfo(
                                    after,
                                    "**Whoop, Whoop**\n\n<:approved:995615632961847406> **"
                                    + email
                                    + "** \n\nwurde bei **"
                                    + PLEX_SERVER_NAME
                                    + "** hinzugefügt!\n\n➡️ **["
                                    + PLEX_SERVER_NAME
                                    + " Invite akzeptieren](https://app.plex.tv/desktop/#!/settings/manage-library-access)**",
                                )
                            else:
                                await embederror(
                                    after,
                                    "<:rejected:995614671128244224> Es gab einen Fehler beim Hinzufügen deiner Email. Bitte kontaktiere <@408885990971670531> .",
                                )
                        plex_processed = True
                        break

                    # Plex role was removed
                    elif role is not None and (
                        role not in after.roles and role in before.roles
                    ):
                        try:
                            user_id = after.id
                            email = db.get_useremail(user_id)
                            plexhelper.plexremove(plex, email)
                            deleted = db.remove_email(user_id)
                            if deleted:
                                print(
                                    "Removed Plex email {} from DataBase".format(
                                        after.name
                                    )
                                )
                                # await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Plex from this user.")
                            await embedinfo(
                                after,
                                "<:approved:995615632961847406> Du wurdest bei **"
                                + PLEX_SERVER_NAME
                                + "** entfernt!",
                            )
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from Plex.".format(email))
                        plex_processed = True
                        break
                if plex_processed:
                    break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if USE_PLEX and plex_configured:
            email = db.get_useremail(member.id)
            plexhelper.plexremove(plex, email)

        deleted = db.delete_user(member.id)
        if deleted:
            print(
                "Removed {} from DataBase because user left Discord server.".format(
                    email
                )
            )

    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="invite", description="Invite a user to Plex")
    async def plexinvite(self, interaction: discord.Interaction, email: str):
        await self.addtoplex(email, interaction.response)

    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="remove", description="Remove a user from Plex")
    async def plexremove(self, interaction: discord.Interaction, email: str):
        await self.removefromplex(email, interaction.response)

    @app_commands.checks.has_permissions(administrator=True)
    @bot_commands.command(
        name="dbadd", description="Add a user to the PlexInviter database"
    )
    async def dbadd(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        email: str = "",
    ):
        email = email.strip()

        # Check email if provided
        if email and not plexhelper.verifyemail(email):
            await embederror(
                interaction.response, "<:rejected:995614671128244224> Invalid email."
            )
            return

        try:
            db.save_user_email(str(member.id), email)
            await embedinfo(
                interaction.response,
                "<:approved:995615632961847406> Email was added to the Database.",
            )
        except Exception as e:
            await embederror(
                interaction.response,
                "<:rejected:995614671128244224> There was an error adding this email address to Database. Check PlexInviter logs for more info",
            )
            print(e)

    @app_commands.checks.has_permissions(administrator=True)
    @bot_commands.command(name="dbls", description="View PlexInviter database")
    async def dbls(self, interaction: discord.Interaction):

        embed = discord.Embed(title="PlexInviter Database.")
        all = db.read_all()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t"])
        table.set_cols_align(["c", "c", "c"])
        header = ("#", "DISCORD", "PLEX")
        table.add_row(header)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(
                name=f"**{index}. {username}**",
                value=dbemail,
                inline=False,
            )
            table.add_row((index, username, dbemail))

        total = str(len(all))
        if len(all) > 25:
            f = open("db.txt", "w")
            f.write(table.draw())
            f.close()
            await interaction.response.send_message(
                "DataBase too large! Total: {total}".format(total=total),
                file=discord.File("db.txt"),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.checks.has_permissions(administrator=True)
    @bot_commands.command(
        name="dbrm", description="Remove user from PlexInviter database"
    )
    async def dbrm(self, interaction: discord.Interaction, position: int):
        embed = discord.Embed(title="StreamNet Plex Database.")
        all = db.read_all()
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(
                name=f"**{index}. {username}**",
                value=dbemail,
                inline=False,
            )

        try:
            position = int(position) - 1
            id = all[position][1]
            discord_user = await self.bot.fetch_user(id)
            username = discord_user.name
            deleted = db.delete_user(id)
            if deleted:
                print("Removed {} from DataBase".format(username))
                await embedinfo(
                    interaction.response,
                    "<:approved:995615632961847406> Removed {} from Database".format(
                        username
                    ),
                )
            else:
                await embederror(
                    interaction.response,
                    "<:rejected:995614671128244224> Cannot remove this User from DataBase.",
                )
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(app(bot))
