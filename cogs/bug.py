import discord
from discord.ext import commands

from components.bug import BugReportModal
from main import ids
from utils.config import ConfigUtil
from utils.variables import Consts


class Bug(commands.Cog):
    BUG_REPORT_COOLDOWN: int

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _bug_report_cooldown(
            msg: discord.Message) -> commands.Cooldown | None:  # type: ignore
        # sourcery skip: instance-method-first-arg-name
        # since this method will not be run inside the class instance,
        # we need to put the variable seperate to the actual instance
        return commands.Cooldown(1, Bug.BUG_REPORT_COOLDOWN)

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f'loaded {__name__}.{__class__.__name__} on server(s) {ids.servers}'
        )

        # load config file
        self.data = await ConfigUtil.create(Consts.CONFIG_PATH)

        # set BUG_REPORT_COOLDOWN
        Bug.BUG_REPORT_COOLDOWN = self.data.data.bug_report_cooldown

    @commands.slash_command(name='bug')
    @commands.dynamic_cooldown(
        _bug_report_cooldown,  # type: ignore
        commands.BucketType.user,
    )
    async def report_bug(self, ctx: discord.ApplicationContext):
        '''Found a bug? Report a bug!'''
        # do not open modal if bug reporting is not allowed
        if not self.data.data.allow_bug_reports:
            await ctx.send_response(
                'We are sorry, but currently it is not allowed to send bug reports!\n'
                'If you think this might be a mistake, feel free to leave feedback!',
                ephemeral=True,
            )
            return
        await ctx.send_modal(BugReportModal(ids, self.bot))

    # bug group
    bugmanage = discord.SlashCommandGroup(
        'bugmanage',
        'Commands for managing bug reports',
        guild_ids=ids.servers,
        default_member_permissions=discord.Permissions(manage_messages=True),
        checks=[commands.has_any_role(*ids.roles.faq_management).predicate],
    )

    @bugmanage.command()
    async def allow_reports(self,
                            ctx: discord.ApplicationContext,
                            allow: bool | None = None):
        '''Whether the users should be able to report bugs'''
        # only show value if allow is not given
        if allow is not None:
            # set value
            conf = await self.data.change_config('allow_bug_reports', allow)

            if conf is None:
                await ctx.send_response(
                    f'There was an error while setting the config `allow_bug_reports` to `{allow}`! Please try again!',
                    ephemeral=True)
                return

        if self.data.data.allow_bug_reports:
            await ctx.send_response('Users are now **able** to report bugs!',
                                    ephemeral=True)
            return

        await ctx.send_response('Users are now **unable** to report bugs!',
                                ephemeral=True)

    @bugmanage.command()
    async def report_cooldown(self,
                              ctx: discord.ApplicationContext,
                              cooldown: int | None = None):
        '''The amount of seconds before a user can report another bug again'''
        # only show value if cooldown is not given
        if cooldown is not None:
            # set value
            conf = await self.data.change_config('bug_report_cooldown',
                                                 cooldown)

            if conf is None:
                await ctx.send_response(
                    f'There was an error while setting the config `bug_report_cooldown` to `{cooldown}`! Please try again!',
                    ephemeral=True)
                return

        await ctx.send_response(
            f'The current cooldown for sending bug reports is **{self.data.data.bug_report_cooldown}** seconds!',
            ephemeral=True)

        # set BUG_REPORT_COOLDOWN
        Bug.BUG_REPORT_COOLDOWN = self.data.data.bug_report_cooldown


def setup(bot: commands.Bot):
    bot.add_cog(Bug(bot))
