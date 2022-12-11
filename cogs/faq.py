import datetime
import math

import discord
from discord.ext import commands, pages
from thefuzz import fuzz, process

from components.faq import AddFaqModal, EditFaqModal
from main import ids
from utils.faq import FaqUtil
from utils.tabulate import tabulate
from utils.variables import Texts


class Faq(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _get_tags_autocomplete(self, ctx: discord.AutocompleteContext):
        # return all tags list if value is ''
        if ctx.value == '':
            return self.data.get_all_tags(-1)

        # return the nearest tags, which are calculated by thefuzz
        res = process.extract(
            ctx.value.lower(),
            self.data.get_all_tags(-1),
            limit=10,
            scorer=fuzz.WRatio,
        )

        return [tag[0] for tag in res if tag[1] >= 50]

    def _create_faq_embed(self, tag: str) -> discord.Embed:
        # get faq
        faq = self.data.get_faq(tag)

        if faq is None:
            embed = discord.Embed(
                title='Tag not found',
                description=
                'Could not find your tag. If you made a typo, use the autocomplete feature to find the correct tag!',
                color=discord.Color.red(),
            )
        else:
            # create embed
            embed = discord.Embed(
                title=faq.title,
                description=faq.description,
                color=discord.Color.blurple(),
            )
            embed.set_thumbnail(url=img if (img := faq.image) else '')
            if (faq.modification_time != 0):
                embed.timestamp = datetime.datetime.fromtimestamp(
                    faq.modification_time)
                embed.set_footer(text="Last updated:")

        # embed.set_footer(text=Texts.EMBED_FOOTER.format(
        #     self.bot.user.name))  # type: ignore

        return embed

    def _get_tags_as_pages(
            self, ctx: discord.ApplicationContext) -> list[discord.Embed]:
        '''
        Gets all FAQ Tags and returns them as a list of embeds, which each display only a set amount of tags.

        This is used for displaying all tags with the paginator module.

        :param ctx: The context to use
        :type ctx: discord.ApplicationContext
        :return: A list of all pages
        :rtype: list[discord.Embed]
        '''
        # determine if user is on mobile (if user is on desktop and mobile, desktop will be preferred)
        # if user is on mobile, each tag will be put on a new line, to make it easier to read
        mobile = ctx.author.mobile_status != discord.Status.offline  # type: ignore

        if mobile and ctx.author.desktop_status != discord.Status.offline:  # type: ignore
            # overwrite mobile status with desktop status
            mobile = False

        if mobile and ctx.author.web_status != discord.Status.offline:  # type: ignore
            # overwrite mobile status with web status
            mobile = False

        # get all tags and add them to a list
        tag_pages: list[discord.Embed] = []

        AMOUNT = 20
        for page in range(math.ceil(len(self.data.get_all_tags(-1)) / AMOUNT)):
            tags = self.data.get_all_tags(AMOUNT, AMOUNT * page)

            # tabulate data
            lines = tags if mobile else tabulate(tags, 1, 62)
            formatted = "\n".join(lines)

            # create embed and append to tag_pages
            embed = discord.Embed(title='All FAQ Tags',
                                  color=discord.Color.blurple())
            embed.add_field(name='Tags',
                            value=f'```{formatted}```',
                            inline=False)
            embed.set_footer(text=Texts.EMBED_FOOTER.format(
                self.bot.user.name))  # type: ignore

            tag_pages.append(embed)

        return tag_pages

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f'loaded {__name__}.{__class__.__name__} on server(s) {ids.servers}'
        )

        # load faq file
        self.data = await FaqUtil.create('config/faq.json')
        self.deleted_data = await FaqUtil.create('config/faq_bin.json')

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        # search messages for faq-content (title, description) or tag, but only if messages contains a '?'
        if msg.author.id == self.bot.user.id:  # type: ignore
            return

        if len(msg.content) == 0 or '?' not in msg.content:
            return

        percentages = [95, 85, 75]
        send_faq_directly = False

        if msg.content.startswith('?'):
            # ?-command -> percentages are lower and message will be sent directly without emoji
            percentages = [i - 10 for i in percentages]
            send_faq_directly = True

        # search tags
        res = process.extract(
            msg.content,
            self.data.get_all_tags(-1),
            limit=1,
            scorer=fuzz.token_sort_ratio,
        )

        res = [tag[0] for tag in res if tag[1] >= percentages[0]]

        if len(res) != 1:
            # search titles
            res = process.extract(
                msg.content,
                {i.tags[0]: i.title
                 for i in self.data.data},
                limit=1,
                scorer=fuzz.token_set_ratio,
            )

            res = [
                tag[2] for tag in res  # type: ignore
                if tag[1] >= percentages[1]
            ]

        if len(res) != 1:
            # search descriptions
            res = process.extract(
                msg.content,
                {i.tags[0]: i.description
                 for i in self.data.data},
                limit=1,
                scorer=fuzz.token_set_ratio,
            )

            res = [
                tag[2] for tag in res  # type: ignore
                if tag[1] >= percentages[2]
            ]

        if len(res) != 1:
            return

        if not send_faq_directly:
            # send emoji to request faq
            await msg.add_reaction('❓')

            def check_init(reaction: discord.Reaction, user: discord.User):
                return (user.id == msg.author.id) and (
                    reaction.emoji == '❓') and (reaction.message.id == msg.id)

            try:
                await self.bot.wait_for('reaction_add',
                                        timeout=60,
                                        check=check_init)
            except Exception:
                await msg.remove_reaction('❓', self.bot.user)  # type: ignore
                return

        embed = self._create_faq_embed(res[0])  # type: ignore
        # embed.set_author(name='Auto-Support')
        ans = await msg.channel.send(embed=embed)

        # make faq removable

        await ans.add_reaction('🚫')

        def check_remove(reaction: discord.Reaction, user: discord.User):
            return (user.id == msg.author.id) and (  # type: ignore
                reaction.emoji == '🚫') and (  # type: ignore
                    reaction.message.id == ans.id)  # type: ignore

        try:
            await self.bot.wait_for(
                'reaction_add',
                timeout=10,
                check=check_remove,
            )
        except Exception:
            await ans.remove_reaction('🚫', self.bot.user)  # type: ignore
        else:
            await ans.delete()

    # ADMIN
    # create SlashCommandGroup to structure the commands
    faqmanage = discord.SlashCommandGroup(
        'faqmanage',
        'Commands for managing the FAQ',
        guild_ids=ids.servers,
        # default_member_permissions=discord.Permissions(manage_messages=True),
        checks=[commands.has_any_role(*ids.roles.faq_management).predicate],
    )

    @faqmanage.command()
    async def add(self, ctx: discord.ApplicationContext):
        '''Adds a new FAQ to the FAQs'''
        await ctx.send_modal(AddFaqModal(self.data))

    @faqmanage.command()
    @discord.option('tag', str, description='The tag of the faq to delete')
    async def delete(self, ctx: discord.ApplicationContext, tag: str):
        '''Deletes a FAQ by its tag'''
        faq = await self.data.remove_faq(tag)

        if not faq:
            await ctx.send_response('Could not remove your faq.')
            return

        # put deleted faq in deleted_data
        await self.deleted_data.add_faq(faq.tags, faq.title, faq.description,
                                        faq.image)

        await ctx.send_response(f'Removed your faq: `{faq}`')

    @faqmanage.command()
    async def edit(self, ctx: discord.ApplicationContext, tag: str):
        '''Edits a FAQ by its tag'''
        entry = self.data.get_faq(tag)
        if entry is None:
            await ctx.send_response(f'The Tag {tag} was not found!',
                                    ephemeral=True)
            return

        await ctx.send_modal(EditFaqModal(self.data, entry, tag))

    @faqmanage.command()
    async def download(self, ctx: discord.ApplicationContext):
        '''Download faq.json'''
        file = self.data.download_faq()
        await ctx.send_response(f"{file.filename}", file=file)

    # USER
    faq = discord.SlashCommandGroup(
        'faq',
        'Commands for accessing the FAQ',
    )

    @faq.command()
    @discord.option('tag', autocomplete=_get_tags_autocomplete)
    async def get(self, ctx: discord.ApplicationContext, tag: str):
        embed = self._create_faq_embed(tag)

        await ctx.send_response(embed=embed)

        # make faq removable
        msg = await ctx.interaction.original_response()

        await msg.add_reaction('🚫')

        def check(reaction: discord.Reaction, user: discord.User):
            return (user.id == ctx.author.id) and (  # type: ignore
                reaction.emoji == '🚫') and (  # type: ignore
                    reaction.message.id == msg.id)  # type: ignore

        try:
            await self.bot.wait_for(
                'reaction_add',
                timeout=10,
                check=check,
            )
        except Exception:
            await msg.remove_reaction('🚫', self.bot.user)  # type: ignore
        else:
            await msg.delete()

    @faq.command(name='list')
    async def list_tags(self, ctx: discord.ApplicationContext, page: int = 1):
        '''Get a list of all FAQ-Tags'''
        paginator = pages.Paginator(
            pages=self._get_tags_as_pages(ctx),  # type: ignore
            loop_pages=True,
            disable_on_timeout=True,
            timeout=60)

        await paginator.respond(ctx.interaction)

        if page > paginator.page_count:
            await paginator.goto_page(paginator.page_count)
        elif page < 1:
            await paginator.goto_page(0)
        else:
            await paginator.goto_page(page - 1)


def setup(bot: commands.Bot):
    bot.add_cog(Faq(bot))
