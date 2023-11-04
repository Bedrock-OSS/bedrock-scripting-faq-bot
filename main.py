import datetime
import logging
import logging.handlers
import os
from random import choice

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils import loader
from utils.variables import Ids, Presences

# start logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(filename='discord.log',
                              encoding='utf-8',
                              maxBytes=10*1024*1024, backupCount=5)
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(intents=intents)

# load ids
ids = Ids('config/ids.jsonc')


@tasks.loop(seconds=20)
async def change_presence():
    presence = choice(Presences.presences)

    msg = presence[1]
    if '{} users' in msg:
        msg = msg.format(len(bot.users))
    elif '{} servers' in msg:
        msg = msg.format(len(bot.guilds))

    await bot.change_presence(
        activity=discord.Activity(type=presence[0], name=msg))


@bot.event
async def on_ready():
    print('-' * 30)
    print(datetime.datetime.now())
    print('Logged in as:')
    print(bot.user.name)  # type: ignore
    print(bot.user.id)  # type: ignore
    print('On server(s):')
    print(ids.servers)
    print('-' * 30)

    change_presence.start()


# react on check failure, eg. when the users doesn't have the correct role
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext,
                                       error: commands.CheckFailure):
    if (type(error) == commands.MissingAnyRole):
        await ctx.send_response(
            'You do not have the permissions to access this command!',
            ephemeral=True,
        )
    elif (type(error) == commands.CommandOnCooldown):
        # TODO use clearer regex
        await ctx.send_response(
            f'This command is on cooldown! Try again in {error.args[0].split(" ")[-1].replace("s", "")} seconds!',
            ephemeral=True,
        )
    else:
        raise error


# run bot
loader.load(bot, 'cogs', ['test'])
bot.run(os.getenv('TOKEN'))
