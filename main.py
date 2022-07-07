import os

import discord
from discord.ext import commands

import settings
from app.common.log import get_logger

intents = discord.Intents.default()
log = get_logger()

cogs: list = [
    f'app.commands.{cmds}.{cmd[:-3]}'
    for cmds in os.listdir(f'{os.curdir}/app/commands')
    for cmd in os.listdir(f'{os.curdir}/app/commands/{cmds}') if cmd.endswith(".py")
]

client = commands.Bot(command_prefix=settings.BOT_PREFIX, help_command=None, intents=intents)


@client.event
async def on_ready():
    log.info("Bot is ready!")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Drinking..."))
    for cog in cogs:
        log.info(f'Cogs: {cogs}')
        try:
            log.info(f'Loading cog {cog}')
            client.load_extension(cog)
            log.info(f'Loaded cog {cog}')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            log.info(f'Failed to load cog {cog}\n{exc}')


if __name__ == "__main__":
    client.run(settings.DISCORD_TOKEN)
