'''
Utility for loading bot extensions / cogs
'''

from pathlib import Path
from typing import Generator, List

from discord.ext import commands


def extensions(path: str,
               skip: List[str] | None = None) -> Generator[str, None, None]:
    '''
    Gets all extensions in the given directory

    :param path: Directory to search
    :type path: str
    :param skip: A list of extensions to skip
    :type skip: List[str] | None
    :yield: The current extension
    :rtype: Generator[str, None, None]
    '''
    files = Path(path).rglob("*.py")
    for file in files:
        if skip and file.name in [f'{f}.py' for f in skip]: continue
        yield file.as_posix()[:-3].replace("/", ".")


def load(bot: commands.Bot, path: str, skip: List[str] | None = None):
    '''
    Loads all extensions

    :param bot: The bot to load extensions
    :type bot: commands.Bot
    :param path: The directory to search for extensions
    :type path: str
    :param skip: A list of extensions to skip
    :type skip: List[str] | None
    '''
    for ext_file in extensions(path, skip):
        try:
            bot.load_extension(ext_file)
            print(f"Loaded {ext_file}")
        except Exception as ex:
            print(f"Failed to load {ext_file}: {ex}")


def unload(bot: commands.Bot, path: str, skip: List[str] | None = None):
    '''
    Unloads all extensions

    :param bot: The bot to load extensions
    :type bot: commands.Bot
    :param path: The directory to search for extensions
    :type path: str
    :param skip: A list of extensions to skip
    :type skip: List[str] | None
    '''
    for ext_file in extensions(path, skip):
        try:
            bot.unload_extension(ext_file)
            print(f"Unloaded {ext_file}")
        except Exception as ex:
            print(f"Failed to unload {ext_file}: {ex}")


async def reload(bot: commands.Bot, path: str, skip: List[str] | None = None):
    '''
    Reloads all extensions

    :param bot: The bot to load extensions
    :type bot: commands.Bot
    :param path: The directory to search for extensions
    :type path: str
    :param skip: A list of extensions to skip
    :type skip: List[str]
    '''
    unload(bot, path, skip)
    load(bot, path, skip)
