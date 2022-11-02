import discord
from discord.ext import commands

from utils.algolia import AlgoliaUtil
from utils.config import ConfigUtil
from main import ids
from utils.variables import Consts


class Search(commands.Cog):

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.config = await ConfigUtil.create(Consts.CONFIG_PATH)

        self.algolia = AlgoliaUtil(
            self.config.data.algolia_app_id,
            self.config.data.algolia_auth_key,
            self.config.data.algolia_index_name,
        )

    @commands.slash_command(guild_ids=ids.servers)
    async def search(self, ctx: discord.ApplicationContext, query: str):
        '''Searches the wiki for the given query'''
        ans = await self.algolia.search_query(query=query)

        await ctx.send_response(ans)


def setup(bot: discord.Bot):
    bot.add_cog(Search(bot))
