# bedrock-scripting-faq-bot
A bot for the Bedrock Scripting Community Discord server

# requirements

## packages

+ https://discordpy.readthedocs.io/en/latest/intro.html
+ https://pypi.org/project/fuzzywuzzy/
+ https://pypi.org/project/python-Levenshtein/ (optional)

## files

+ token.txt file in same directory as script.
  token.txt should contain the Discord bot token from https://discord.com/developers/applications/[your_bot]/bot
+ bugreportchannelID.txt in the same directory as script. Should contain the channel ID of the channel where the bot posts bug reports. This can be a group DM, or just a general   channel on a server... You can get a channel ID by right-clicking on a channel in discord, and at the bottom of the menu, select [Copy ID]

## discord server

+ role: faq-management: the role for people who can create FAQs
+ role: bsb-admin: the role for people who can use the bot's admin commands, like bug reporting

