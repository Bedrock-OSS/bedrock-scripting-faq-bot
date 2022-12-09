import os
from dataclasses import asdict
from typing import List

import aiofiles
import discord
import json5 as json
from dataclass_wizard import fromlist

from classes.faq import FaqEntry
from utils.cache import lru_cache


class FaqUtil:

    def __init__(self, path: str, data: List[FaqEntry]) -> None:
        self.path = path
        self.data = data

    @classmethod
    async def create(cls, path: str):
        '''Creates the FaqUtil class, loads the file and returns the class.'''
        data = await cls.load_faq(cls, path)
        return cls(path, data)

    async def load_faq(self, path: str) -> list[FaqEntry]:
        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                return [
                    *fromlist(FaqEntry, json.loads(await
                                                   f.read()))  # type: ignore
                ]
        except FileNotFoundError:
            # faq does not exist, create file
            print('No faq.json-file found, creating new one...')
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write('')
                return []

    async def save_faq(self, path: str):
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(
                json.dumps(  # type: ignore
                    [asdict(i) for i in self.data],
                    ensure_ascii=True,
                    indent=4,
                    quote_keys=True,
                    trailing_commas=False))

    async def add_faq(self,
                      tags: List[str],
                      title: str,
                      description: str | None = None,
                      image: str | None = None) -> FaqEntry | None:
        '''
        Adds the new entry to the faq

        :param tags: The tags to add
        :type tags: List[str]
        :param title: The title to add
        :type title: str
        :param description: The information to add, defaults to None
        :type description: str | None, optional
        :param image: The image link to add, defaults to None
        :type image: str | None, optional
        :return: The created Entry or None if one of the tags already exists
        :rtype: FaqEntry
        '''
        if any(tag in self.get_all_tags(-1) for tag in tags):
            return None
        entry = FaqEntry(tags=[tag.lower() for tag in tags],
                         title=title,
                         description=description,
                         image=image,
                         modification_time=int(discord.utils.utcnow().timestamp()))
        self.data.append(entry)

        # save faq
        await self.save_faq(self.path)

        return entry

    def get_faq(self, tag: str) -> FaqEntry | None:
        '''
        Gets a FAQ-Entry by its tags

        :param tag: The tag to search
        :type tag: str
        :return: The found entry or None if nothing was found
        :rtype: FaqEntry | None
        '''
        for entry in self.data:
            if tag in entry.tags:
                return entry

    async def edit_faq(self,
                       old_tags: list[str],
                       new_tags: list[str],
                       title: str,
                       description: str | None = None,
                       image: str | None = None) -> FaqEntry | None:
        '''
        Edits a FAQ by one of its tags

        :param old_tags: The tag to edit
        :type old_tags: list[str]
        :param new_tags: A list of new tags
        :type new_tags: list[str]
        :param title: The new title
        :type title: str
        :param description: The new description, defaults to None
        :type description: str | None, optional
        :param image: The new image, defaults to None
        :type image: str | None, optional
        :return: The updated entry or None if a) There was not an entry with this tag or b) One of the new tags already exists
        :rtype: FaqEntry | None
        '''
        # search entry
        entry = self.get_faq(old_tags[0])

        # either there is no entry OR any of the tags, that are completely newly added do already exist
        if entry is None or any(
                tag in self.get_all_tags(-1)
                for tag in [x for x in new_tags if x not in old_tags]):
            return

        # edit entry and save
        entry.tags = [tag.lower() for tag in new_tags]
        entry.title = title
        entry.description = description
        entry.image = image
        entry.modification_time = int(discord.utils.utcnow().timestamp())

        await self.save_faq(self.path)

        return entry

    async def remove_faq(self, tag: str) -> FaqEntry | None:
        '''
        Removes the FAQ-Entry found by the tag

        :param tag: The tag to search
        :type tag: str
        :return: The deleted entry or None if nothing was found and deleted
        :rtype: FaqEntry | None
        '''
        for entry in self.data:
            if tag in entry.tags:
                self.data.remove(entry)

                # save faq
                await self.save_faq(self.path)

                return entry

    def download_faq(self) -> discord.File:
        '''
        Downloads the FAQ-File

        :return: The FAQ-File
        :rtype: discord.File
        '''
        faq_path = os.path.join(os.getcwd(), self.path)
        return discord.File(faq_path)

    @lru_cache(60)
    def get_all_tags(self, amount: int, offset: int = 0) -> list[str]:
        '''
        Returns a list of all tags

        :param amount: The amount of tags that need to be returned. -1 for all tags
        :type amount: int
        :param offset: The amount of tags (starting from beginning) that should not be included. Defaults to 0
        :type offset: int
        :return: A list of all tags
        :rtype: list[str]
        '''
        tags = sorted([t for e in self.data for t in e.tags])
        if amount == -1:
            return tags

        tags = tags[offset:offset + amount:]

        return tags
