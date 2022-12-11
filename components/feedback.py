'''
Modals for feedback reporting
'''

from datetime import datetime

import discord
from discord.ui import InputText, Modal

from utils.variables import Ids
from utils.variables import Texts


# EMBEDS
def create_feedback_embed(feedback: str, interaction: discord.Interaction,
                          for_user: bool):
    embed = discord.Embed(
        title='Your feedback was sent!' if for_user else 'New Feedback Report',
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
            value=
            f'`{interaction.guild}` / {interaction.channel.mention}',  # type: ignore
            inline=True,
        )
    else:
        embed.set_author(name="Success!")

    embed.add_field(name='Report', value=feedback, inline=False)
    embed.set_footer(text=Texts.EMBED_FOOTER.format(
        interaction.client.user.name))  # type: ignore
    return embed


# MODALS
class FeedbackModal(Modal):

    def __init__(self, ids: Ids, bot: discord.Bot) -> None:
        super().__init__(title='Send Feedback')
        self.ids = ids
        self.bot = bot

        self.add_item(
            InputText(style=discord.InputTextStyle.long,
                      label='Tell us more about your feedback:',
                      required=True))

    async def callback(self, interaction: discord.Interaction):
        feedback: str = self.children[0].value  # type: ignore

        user_embed = create_feedback_embed(feedback, interaction, True)
        mod_embed = create_feedback_embed(feedback, interaction, False)

        # send confirmation
        await interaction.response.send_message(embed=user_embed,
                                                ephemeral=True)

        # get feedback channel
        feedback_guild = self.bot.get_guild(self.ids.feedback.server)
        if not feedback_guild:
            print('ERROR: could not get feedback guild.')
            return

        feedback_channel = feedback_guild.get_channel(
            self.ids.feedback.channel)

        if not feedback_channel:
            print('ERROR: could not get feedback channel.')
            return

        # send feedback to channel
        await feedback_channel.send(embed=mod_embed)  # type: ignore
