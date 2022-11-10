import discord
from discord.ext import commands
from classes.algolia import AlgoliaResult

from main import ids
from utils.algolia import AlgoliaUtil
from utils.config import ConfigUtil
from utils.variables import Consts, Texts
from collections import OrderedDict


def create_result_embed(term: str, res: list[AlgoliaResult], bot: discord.Bot):
    # get wiki-group to mention it
    cmd = bot.get_application_command('wiki', type=discord.SlashCommandGroup)

    # create embed
    embed = discord.Embed(
        title=f'Your search for ***{term}*** returned:',
        description=
        f'For more information on a result, use </wiki details:{cmd.id}>',  # type: ignore
        color=discord.Color.blurple(),
    )

    # add a field for every entry
    for i, field in enumerate(res, 1):
        embed.add_field(
            name=
            f'({i}) {field.header}{f" - {d}" if (d := field.description) else ""}',
            value=field.url,
            inline=False,
        )

    embed.set_footer(text=Texts.EMBED_FOOTER.format(
        bot.user.name))  # type: ignore

    return embed


class Search(commands.Cog):

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self._search_cache: OrderedDict[int,
                                        list[AlgoliaResult]] = OrderedDict()

    @property
    def search_cache(self):
        return self._search_cache

    def add_search_cache(self, key: int, val: list[AlgoliaResult]):
        '''
        Cache for search results

        This method adds an new AlgoliaResult to the search_cache, so the user can request details with `/wiki details`.
        
        Only 10 AlgoliaResults are cached, the oldest will be deleted.

        :param key: The Key, most of the time it is the author.id
        :type key: int
        :param val: The AlgoliaResults the user requested
        :type val: list[AlgoliaResult]
        '''
        self._search_cache[key] = val  # type: ignore
        if len(self._search_cache.keys()) > 3:
            self._search_cache.popitem(False)

    @commands.Cog.listener()
    async def on_ready(self):
        self.config = await ConfigUtil.create(Consts.CONFIG_PATH)

        self.algolia = AlgoliaUtil(
            self.config.data.algolia_app_id,
            self.config.data.algolia_auth_key,
            self.config.data.algolia_index_name,
        )

    wiki = discord.SlashCommandGroup('wiki',
                                     'Search the wiki',
                                     guild_ids=ids.servers)

    @wiki.command()
    @discord.option('query', str, description='The query to search for')
    @discord.option(
        'max',
        int,
        description='The maximum amount of results to return. maximum is 5')
    async def search(self,
                     ctx: discord.ApplicationContext,
                     query: str,
                     max: int = 5):
        '''Searches the wiki for the given query'''
        ans = await self.algolia.search_query(query=query, max=max)

        self.add_search_cache(
            ctx.author.id,  # type: ignore
            ans,
        )  # type: ignore

        # create an embed for every result
        embed = create_result_embed(query, ans, self.bot)

        await ctx.send_response(embed=embed)

    @wiki.command()
    async def details(self, ctx: discord.ApplicationContext, id: int):
        '''Show additional details for a search result'''
        id -= 1
        # get cached results
        # if there is nothing cached, send error
        try:
            res = self.search_cache[ctx.author.id]  # type: ignore
        except KeyError:
            # get wiki-group to mention it
            cmd = self.bot.get_application_command(
                'wiki', type=discord.SlashCommandGroup)
            await ctx.send_response(
                'Could not find your last search-request! '
                f'Please use </wiki search:{cmd.id}> to get '  # type: ignore
                'a list of search results before using this command.')
            return

        # get specific result
        # if the id does not exist, send error
        try:
            ans = res[id]
        except IndexError:
            await ctx.send_response(
                f'The id {id} does not exist in your last search request. '
                f'Please use an id between 0 and {len(res)}.')
            return

        # get metadata
        data = await self.algolia.get_metadata(ans.url)
        await ctx.send_response('data')


def setup(bot: discord.Bot):
    bot.add_cog(Search(bot))
