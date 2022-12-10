'''
Modals for bug reporting
'''

from datetime import datetime

import discord
from discord.ui import InputText, Modal

from utils.variables import Ids
from utils.variables import Texts


# EMBEDS
def create_bug_embed(bug: str, interaction: discord.Interaction,
                     for_user: bool):
    embed = discord.Embed(
        title='Your bug report was sent!' if for_user else 'New Bug Report',
        color=discord.Color.blurple(),
        timestamp=datetime.now(),
    )
    # add additional information if the message is for the mods
    if not for_user:
        embed.add_field(
            name='From',
            value=interaction.user.mention,  # type: ignore
            inline=True,
        )
        embed.add_field(
            name='In Channel',
            value=interaction.channel.mention,  # type: ignore
            inline=True,
        )
    else:
        embed.set_author(name="Success!")

    embed.add_field(name='Report', value=bug, inline=False)
    embed.set_footer(text=Texts.EMBED_FOOTER.format(
        interaction.client.user.name))  # type: ignore
    return embed


# MODALS
class BugReportModal(Modal):

    def __init__(self, ids: Ids, bot: discord.Bot) -> None:
        super().__init__(title='Report a Bug')
        self.ids = ids
        self.bot = bot

        self.add_item(
            InputText(style=discord.InputTextStyle.long,
                      label='Tell us more about your bug:',
                      required=True))

    async def callback(self, interaction: discord.Interaction):
        bug: str = self.children[0].value  # type: ignore

        user_embed = create_bug_embed(bug, interaction, True)
        mod_embed = create_bug_embed(bug, interaction, False)

        # send confirmation
        await interaction.response.send_message(embed=user_embed,
                                                ephemeral=True)

        # get bug report channel
        bug_report_guild = self.bot.get_guild(self.ids.bug_report.server)
        if not bug_report_guild:
            print('ERROR: could not get bug report guild.')
            return

        bug_report_channel = bug_report_guild.get_channel(
            self.ids.bug_report.channel)

        if not bug_report_channel:
            print('ERROR: could not get bug report channel.')
            return

        # send bug to channel
        await bug_report_channel.send(embed=mod_embed)  # type: ignore
