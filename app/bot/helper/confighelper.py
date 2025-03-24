import configparser
import os
from os import environ, path
from dotenv import load_dotenv

CONFIG_PATH = "app/config/config.ini"
BOT_SECTION = "bot_envs"
PLEXINVITER_VERSION = 1.0

config = configparser.ConfigParser()

CONFIG_KEYS = [
    "username",
    "password",
    "discord_bot_token",
    "plex_user",
    "plex_pass",
    "plex_token",
    "plex_base_url",
    "plex_roles",
    "plex_server_name",
    "plex_libs",
    "owner_id",
    "channel_id",
    "auto_remove_user",
    "plex_enabled",
]

# settings
Discord_bot_token = ""
plex_roles = None
PLEXUSER = ""
PLEXPASS = ""
PLEX_SERVER_NAME = ""
PLEX_TOKEN = ""
PLEX_BASE_URL = ""
Plex_LIBS = None
plex_configured = True

switch = 0

# TODO: make this into a class

if path.exists("bot.env"):
    try:
        load_dotenv(dotenv_path="bot.env")
        # settings
        Discord_bot_token = environ.get("discord_bot_token")
        switch = 1

    except Exception as e:
        pass

try:
    Discord_bot_token = str(os.environ["token"])
    switch = 1
except Exception as e:
    pass

if not (path.exists(CONFIG_PATH)):
    with open(CONFIG_PATH, "w") as fp:
        pass


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
    PLEX_SERVER_NAME = config.get(BOT_SECTION, "plex_server_name")
    PLEXUSER = config.get(BOT_SECTION, "plex_user")
    PLEXPASS = config.get(BOT_SECTION, "plex_pass")
except:
    print("No Plex login info found")
    if not plex_token_configured:
        print("Could not load plex config")
        plex_configured = False

# Get Plex roles config
try:
    plex_roles = config.get(BOT_SECTION, "plex_roles")
except:
    print("Could not get Plex roles config")
    plex_roles = None
if plex_roles:
    plex_roles = list(plex_roles.split(","))
else:
    plex_roles = []

# Get Plex libs config
try:
    Plex_LIBS = config.get(BOT_SECTION, "plex_libs")
except:
    print("Could not get Plex libs config. Defaulting to all libraries.")
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


def get_config():
    """
    Function to return current config
    """
    try:
        config.read(CONFIG_PATH)
        return config
    except Exception as e:
        print(e)
        print("error in reading config")
        return None


def change_config(key, value):
    """
    Function to change the key, value pair in config
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
    except Exception as e:
        print(e)
        print("Cannot Read config.")

    try:
        config.set(BOT_SECTION, key, str(value))
    except Exception as e:
        config.add_section(BOT_SECTION)
        config.set(BOT_SECTION, key, str(value))

    try:
        with open(CONFIG_PATH, "w") as configfile:
            config.write(configfile)
    except Exception as e:
        print(e)
        print("Cannot write to config.")
