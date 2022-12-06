from dataclasses import asdict
from typing import Any

import aiofiles
import json5 as json
from dataclass_wizard import fromdict

from classes.config import Config


class ConfigUtil:

    def __init__(self, path: str, data: Config) -> None:
        self.path = path
        self.data = data

    @classmethod
    async def create(cls, path: str):
        '''Creates the ConfigUtil class, loads the file and returns the class.'''
        data = await cls.load_config(cls, path)
        return cls(path, data)

    async def load_config(self, path: str) -> Config:
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            return fromdict(Config, json.loads(await f.read()))  # type: ignore

    async def save_config(self, path: str):
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(
                json.dumps(  # type: ignore
                    asdict(self.data),
                    ensure_ascii=True,
                    indent=4,
                    quote_keys=True,
                    trailing_commas=False) + '\n')

    async def change_config(self, key: str, value: Any) -> Config | None:
        '''
        Change a config value

        :param key: The key to change
        :type key: str
        :param value: The new value
        :type value: Any
        :return: The updated config or None if there was an Error (maybe the key does not exist or the value was the wrong type)
        :rtype: Config | None
        '''
        if key not in self.data.__dict__.keys():
            return None

        try:
            self.data.__setattr__(key, value)
        except Exception:
            return None

        # save config
        await self.save_config(self.path)
        return self.data
