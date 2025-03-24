# PlexInviter-bot

PlexInviter is a Discord bot that invites users to your Plex media server. You can automate this bot to invite Discord users to Plex once a certain role is given to a user, or users can be added manually.

### Features

- Ability to invite users to Plex from Discord
- Fully automatic invites using Discord roles
- Ability to kick users from Plex if they leave the Discord server or if their role is taken away
- Ability to view the database in Discord and to edit it

Commands:

```
/plex invite <email>
This command is used to add an email to Plex
/plex remove <email>
This command is used to remove an email from Plex
/bot dbls
This command is used to list PlexInviter's database
/bot dbadd <@user> <optional: plex email>
This command is used to add existing Plex emails and Discord ID to the database
/bot dbrm <position>
This command is used to remove a record from the database. Use /bot dbls to determine record position. ex: /bot dbrm 1
```

# Creating Discord Bot

1. Create the Discord server that your users will get member roles or use an existing Discord that you can assign roles from
2. Log into https://discord.com/developers/applications and click 'New Application'
3. (Optional) Add a short description and an icon for the bot. Save changes.
4. Go to 'Bot' section in the side menu
5. Uncheck 'Public Bot' under Authorization Flow
6. Check all 3 boxes under Privileged Gateway Intents: Presence Intent, Server Members Intent, Message Content Intent. Save changes.
7. Copy the token under the username or reset it to copy. This is the token used in the Docker image.
8. Go to 'OAuth2' section in the side menu, then 'URL Generator'
9. Under Scopes, check 'bot' and applications.commands
10. Copy the 'Generated URL' and paste into your browser and add it to your Discord server from Step 1.
11. The bot will come online after the Docker container is running with the correct Bot Token

# Unraid Installation

> For Manual and Docker setup, see below

1. Ensure you have the Community Applications plugin installed.
2. Inside the Community Applications app store, search for PlexAdd.
3. Click the Install Button.
4. Add Discord bot token.
5. Click apply
6. Finish setting up using [Setup Commands](#after-bot-has-started)

# Manual Setup (For Docker, see below)

**1. Enter Discord bot token in bot.env**

**2. Install requirements**

```
pip3 install -r requirements.txt
```

**3. Start the bot**

```
python3 Run.py
```

# Docker Setup & Start

To run PlexInviter-bot in Docker, run the following command, replacing [path to config] with the absolute path to your bot config folder:

```
docker run -d --restart unless-stopped --name plexinviter-bot -v /[path to config]:/app/app/config -e "token=YOUR_DISCORD_TOKEN_HERE" yoruio/plexinviter-bot:latest
```

# After bot has started

# Plex Setup Commands:

```
/plexsettings setup <username> <password> <server name>
This command is used to setup Plex login.
/plexsettings addrole <@role>
These role(s) will be used as the role(s) to automatically invite user to Plex
/plexsettings removerole <@role>
This command is used to remove a role that is being used to automatically invite uses to Plex
/plexsettings setuplibs <libraries>
This command is used to setup Plex libraries. Default is set to all. Libraries is a comma separated list.
/plexsettings enable
This command enables the Plex integration (currently only enables auto-add / auto-remove)
/plexsettings disable
This command disables the Plex integration (currently only disables auto-add / auto-remove)
```

# Migration from Invitarr

Invitarr does not require the applications.commands scope, so you will need to kick and reinvite your Discord bot to your server, making sure to tick both the "bot" and "applications.commands" scopes in the OAuth URL generator.

PlexInviter-bot uses a slightly different database table than Invitarr. PlexInviter-bot will automatically update the Invitarr db table to the current PlexInviter-bot table format, but the new table will no longer be compatible with Invitarr, so backup your app.db before running PlexInviter-bot!

# Migration to Invitarr

To switch back to Invitarr, you will have to manually change the table format back. Open app.db in a sqlite CLI tool or browser like DB Browser, then remove the "jellyfin_username" column, and make the "email" column non-nullable.

# Contributing

We appreciate any and all contributions made to the project, whether that be new features, bugfixes, or even fixed typos! If you would like to contribute to the project, simply fork the development branch, make your changes, and open a pull request. _Pull requests that are not based on the development branch will be rejected._

# Other stuff

**Enable Intents else bot will not DM users after they get the role.**
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents
**Discord Bot requires Bot and application.commands permission to fully function.**
