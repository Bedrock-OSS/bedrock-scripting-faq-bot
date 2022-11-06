import discord
from discord.ext import commands
from classes.algolia import AlgoliaResult

from main import ids
from utils.algolia import AlgoliaUtil
from utils.config import ConfigUtil
from utils.variables import Consts


def create_result_embed(res: AlgoliaResult, longest: int):
    embed = discord.Embed(
        title=res.header,
        url=res.url,
        description=res.description,
        color=discord.Color.blurple(),
    )
    embed.set_thumbnail(url=f'attachment://{res.type.value}.png')

    return embed


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

        longest = max([len(res.header) for res in ans] +
                      [len(res.description) for res in ans if res.description])

        # create an embed for every result
        embeds = [create_result_embed(res, longest) for res in ans]

        # get all result types
        types = [res.type.value for res in ans]

        # create a list of all files needed for the result-type thumbnail
        files = [discord.File(f'./assets/{type}.png') for type in types]

        await ctx.send_response(files=files, embeds=embeds)


def setup(bot: discord.Bot):
    bot.add_cog(Search(bot))
