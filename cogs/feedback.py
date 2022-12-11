import discord
from discord.ext import commands

from components.feedback import FeedbackModal
from main import ids
from utils.config import ConfigUtil
from utils.variables import Consts


class Feedback(commands.Cog):
    FEEDBACK_COOLDOWN: int

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _feedback_cooldown(
            msg: discord.Message) -> commands.Cooldown | None:  # type: ignore
        # sourcery skip: instance-method-first-arg-name
        # since this method will not be run inside the class instance,
        # we need to put the variable seperate to the actual instance
        return commands.Cooldown(1, Feedback.FEEDBACK_COOLDOWN)

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f'loaded {__name__}.{__class__.__name__} on server(s) {ids.servers}'
        )

        # load config file
        self.data = await ConfigUtil.create(Consts.CONFIG_PATH)

        # set FEEDBACK_COOLDOWN
        Feedback.FEEDBACK_COOLDOWN = self.data.data.feedback_cooldown

    @commands.slash_command(name='feedback')
    @commands.dynamic_cooldown(
        _feedback_cooldown,  # type: ignore
        commands.BucketType.user,
    )
    async def send_feedback(self, ctx: discord.ApplicationContext):
        '''Found a bug? Want to give us feedback? Then you are right!'''
        # do not open modal if feedback reporting is not allowed
        if not self.data.data.allow_feedback:
            await ctx.send_response(
                'We are sorry, but currently it is not allowed to send feedback!\n'
                'If you think this might be a mistake, feel free to contact us directly!',
                ephemeral=True,
            )
            return
        await ctx.send_modal(FeedbackModal(ids, self.bot))

    # feedback group
    feedbackmanage = discord.SlashCommandGroup(
        'feedbackmanage',
        'Commands for managing feedback reports',
        guild_ids=ids.servers,
        default_member_permissions=discord.Permissions(manage_messages=True),
        checks=[commands.has_any_role(*ids.roles.faq_management).predicate],
    )

    @feedbackmanage.command()
    async def allow_reports(self,
                            ctx: discord.ApplicationContext,
                            allow: bool | None = None):
        '''Whether the users should be able to send feedback'''
        # only show value if allow is not given
        if allow is not None:
            # set value
            conf = await self.data.change_config('allow_feedback', allow)

            if conf is None:
                await ctx.send_response(
                    f'There was an error while setting the config `allow_feedback` to `{allow}`! Please try again!',
                    ephemeral=True)
                return

        if self.data.data.allow_feedback:
            await ctx.send_response('Users are now **able** to send feedback!',
                                    ephemeral=True)
            return

        await ctx.send_response('Users are now **unable** to send feedback!',
                                ephemeral=True)

    @feedbackmanage.command()
    async def report_cooldown(self,
                              ctx: discord.ApplicationContext,
                              cooldown: int | None = None):
        '''The amount of seconds before a user can send other feedback again'''
        # only show value if cooldown is not given
        if cooldown is not None:
            # set value
            conf = await self.data.change_config('feedback_cooldown', cooldown)

            if conf is None:
                await ctx.send_response(
                    f'There was an error while setting the config `feedback_cooldown` to `{cooldown}`! Please try again!',
                    ephemeral=True)
                return

        await ctx.send_response(
            f'The current cooldown for sending feedback is **{self.data.data.feedback_cooldown}** seconds!',
            ephemeral=True)

        # set FEEDBACK_COOLDOWN
        Feedback.FEEDBACK_COOLDOWN = self.data.data.feedback_cooldown


def setup(bot: commands.Bot):
    bot.add_cog(Feedback(bot))
