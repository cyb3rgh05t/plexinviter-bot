from pickle import FALSE
# import app.bot.helper.jellyfinhelper as jelly
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
import app.bot.helper.jellyfinhelper as jelly
import texttable
from app.bot.helper.message import *
from app.bot.helper.confighelper import *

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'

plex_configured = True
# jellyfin_configured = True

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

plex_token_configured = True
try:
    PLEX_TOKEN = config.get(BOT_SECTION, 'plex_token')
    PLEX_BASE_URL = config.get(BOT_SECTION, 'plex_base_url')
except:
    print("No Plex auth token details found")
    plex_token_configured = False

# Get Plex config
try:
    PLEXUSER = config.get(BOT_SECTION, 'plex_user')
    PLEXPASS = config.get(BOT_SECTION, 'plex_pass')
    PLEX_SERVER_NAME = config.get(BOT_SECTION, 'plex_server_name')
except:
    print("No Plex login info found")
    if not plex_token_configured:
        print("Could not load plex config")
        plex_configured = False

# these were copied from the app object. They could be made static instead but I'm lazy.
async def embederror(recipient, message, ephemeral=True):
    embed1 = discord.Embed(title="",description=message, color=0xf50000)
    await send_embed(recipient, embed1, ephemeral)

async def embedinfo(recipient, message, ephemeral=True):
    embed1 = discord.Embed(title="",description=message, color=0x00FF00)
    await send_embed(recipient, embed1, ephemeral)

async def embedtitle(recipient, message, ephemeral=True):
        embed1 = discord.Embed(title=message, color=0x00FF00)
        await send_embed(recipient, embed1, ephemeral)

async def embedemail(recipient, message, ephemeral=True):
        time = (datetime.now() + timedelta(hours=24)).strftime("%d. %B %Y | %H:%M:%S")
        embed1 = discord.Embed(title='**'+ PLEX_SERVER_NAME +' Invite**  🎟️',description=message, color=0x00FF00)
        embed1.add_field(name="Gültig bis:", value='``'+ time +'``', inline=False)
        await send_embed(recipient, embed1, ephemeral)

async def embederroremail(recipient, message, ephemeral=True):
        embed1 = discord.Embed(title="",description=message, color=0xf50000)
        embed1.add_field(name="Mögliche Fehler:", value='``•`` Fehlerhaftes **EMail**-Format.\n``•`` Du bist schon bei **StreamNet** angemeldet.\n``•`` Die angegebene Email ist nicht bei **Plex** registriert.\n``•`` Username anstadt **EMail** angegeben', inline=False)
        await send_embed(recipient, embed1, ephemeral)

async def embedinfoaccept(recipient, message, ephemeral=True):
        embed1 = discord.Embed(title="",description=message, color=0x00FF00)
        #embed1.add_field(name="Plex Mail:", value=''+ email +'', inline=False)
        await send_embed(recipient, embed1, ephemeral)

async def embedcustom(recipient, title, fields, ephemeral=True):
    embed = discord.Embed(title=title)
    for k in fields:
        embed.add_field(name=str(k), value=str(fields[k]), inline=True)
    await send_embed(recipient, embed, ephemeral)

async def send_info(recipient, message, ephemeral=True):
    if isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(message, ephemeral=ephemeral)
    elif isinstance(recipient, discord.User) or isinstance(recipient, discord.member.Member) or isinstance(recipient, discord.Webhook):
        await recipient.send(message)

async def send_embed(recipient, embed, ephemeral=True):
    if isinstance(recipient, discord.User) or isinstance(recipient, discord.member.Member) or isinstance(recipient, discord.Webhook):
        await recipient.send(embed=embed)
    elif isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(embed=embed, ephemeral = ephemeral)


        
