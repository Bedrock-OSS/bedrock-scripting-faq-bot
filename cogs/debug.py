import discord
from discord.ext import commands

from main import ids


class Debug(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f'loaded {__name__}.{__class__.__name__} on server(s) {ids.servers}'
        )

    @commands.slash_command(guild_ids=ids.servers)
    @discord.guild_only()
    @discord.default_permissions(manage_messages=True)
    @commands.has_any_role(
        *ids.roles.admin
    )  # TODO currently, pycord has no way of restricting a slash command to a specific role. If this is added later, this will be changed.
    async def ping(self, ctx: discord.ApplicationContext):
        '''Measures the ping of the bot'''
        await ctx.respond(f'The bots latency is: {self.bot.latency * 1000} ms')


def setup(bot: commands.Bot):
    bot.add_cog(Debug(bot))
