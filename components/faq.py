'''
Modals for faq
'''

import discord
from discord.ui import InputText, Modal

from classes.faq import FaqEntry
from utils.faq import FaqUtil
from utils.variables import Texts


# EMBEDS
def create_manage_embed(title: str, success: bool,
                        bot: discord.Bot | discord.Client, entry: FaqEntry):
    embed = discord.Embed(
        title=title,
        description=''
        if success else 'At least one of your tags does already exist.',
        color=discord.Color.green() if success else discord.Color.red(),
    )
    embed.set_author(name="Success!" if success else 'Error!')
    embed.set_thumbnail(url=img if (img := entry.image) else '')
    embed.add_field(name="Title", value=entry.title, inline=False)
    embed.add_field(name="Tags", value=', '.join(entry.tags), inline=False)
    embed.add_field(name="Description",
                    value=desc if
                    (desc := entry.description) else '*not given*',
                    inline=False)
    embed.add_field(name="Image-URL",
                    value=img if (img := entry.image) else '*not given*',
                    inline=True)
    embed.set_footer(text=Texts.EMBED_FOOTER.format(
        bot.user.name))  # type: ignore
    return embed


# MODALS
class FaqModal(Modal):
    '''Base Class for all FAQ-Modals'''

    def __init__(
        self,
        faq: FaqUtil,
        title: str | None,
        tags: str | None,
        description: str | None,
        image: str | None,
    ) -> None:
        self.faq = faq
        super().__init__(title='Add new FAQ')

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Title',
                required=True,
                value=title,
            ))

        self.add_item(
            InputText(
                style=discord.InputTextStyle.long,
                label='Tags',
                placeholder='Input the tags seperated by ","',
                required=True,
                value=tags,
            ))

        self.add_item(
            InputText(
                style=discord.InputTextStyle.long,
                label='Description',
                placeholder='Insert a description for this faq',
                required=False,
                value=description,
            ))

        self.add_item(
            InputText(
                style=discord.InputTextStyle.short,
                label='Image',
                placeholder='Insert a link',
                required=False,
                value=image,
            ))


class AddFaqModal(FaqModal):

    def __init__(self, faq: FaqUtil) -> None:
        super().__init__(faq, None, None, None, None)

    async def callback(self, interaction: discord.Interaction):
        title: str = self.children[0].value  # type: ignore
        tags = self.children[1].value.replace(  # type: ignore
            ' ', '', -1).split(',')
        description = self.children[2].value or None
        image = self.children[3].value or None
        faq = await self.faq.add_faq(tags, title, description, image)

        # error if faq is None -> tag already exists
        if faq is None:
            embed = create_manage_embed(
                'Could not add FAQ', False, interaction.client,
                FaqEntry(tags=tags,
                         title=title,
                         description=description,
                         image=image))
            await interaction.response.send_message(embed=embed)
            return

        # create embed
        embed = create_manage_embed("Added new FAQ", True, interaction.client,
                                    faq)
        await interaction.response.send_message(embed=embed)


class EditFaqModal(FaqModal):

    def __init__(self, faq: FaqUtil, entry: FaqEntry, tag: str) -> None:
        self.tags = entry.tags
        super().__init__(
            faq,
            entry.title,
            ', '.join(entry.tags),
            entry.description,
            entry.image,
        )

    async def callback(self, interaction: discord.Interaction):
        title: str = self.children[0].value  # type: ignore
        tags = self.children[1].value.replace(  # type: ignore
            ' ', '', -1).split(',')
        description = self.children[2].value or None
        image = self.children[3].value or None
        faq = await self.faq.edit_faq(self.tags, tags, title, description,
                                      image)

        # erorr if faq is None -> One of the tags does already exist
        if faq is None:
            embed = create_manage_embed(
                'Could not update FAQ', False, interaction.client,
                FaqEntry(tags=tags,
                         title=title,
                         description=description,
                         image=image))
            await interaction.response.send_message(embed=embed)
            return

        # create embed
        embed = create_manage_embed("Edited FAQ", True, interaction.client,
                                    faq)
        await interaction.response.send_message(embed=embed)
