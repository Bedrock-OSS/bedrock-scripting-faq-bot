import json
from string import ascii_letters
import os
import time
import datetime
import discord
from fuzzywuzzy import fuzz

def loadConfig():
    default_config = {
        'allow_bug_reports': False,
        'bug_report_cooldown': 300
    }
    config_path = os.path.join(os.getcwd(), 'config.json')
    if not os.path.exists(config_path):
        with open(os.path.join(os.getcwd(), 'config.json'), 'w') as f:
            json.dump(default_config, f, indent=4)
    with open(config_path, 'r') as f:
        config_json = json.load(f)
    for key in default_config:
        if not key in config_json:
            config_json[key] = default_config[key]
    return config_json

CONFIG = loadConfig()

def dumpConfig():
    config_path = os.path.join(os.getcwd(), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(CONFIG, f, indent=4)

class BOT_DATA:

    BOT_COMMAND_PREFIX = '!'
    # the string that the bot recognises as a command
    FAQ_QUERY_PREFIX = '?'
    # the string that the bot recognises as a FAQ query

    TOKEN_FILENAME = 'token.txt'
    # the filename of the txt file where the bot token is stored

    APPROVED_SERVERS_FILENAME = 'approved_servers.txt'
    # the filename of the txt file which contains IDs of all
    # the discord servers which can use admin commands for the bot

    FAQ_DATA_FILENAME = 'faq.json'
    FAQ_DATA_FILENAME_BIN = 'faq_bin.json'

    FAQ_MANAGEMENT_ROLE = 'faq-management'
    # the role that can manage the faqs
    BOT_ADMIN_ROLE = 'bsb-admin'
    # the role that can manage the faqs

    COMMAND_PREFIXES = {
        'bug': 'bug',
        'help': 'help',
        'search': 'search',
        'faq_viewing': 'faq',
        'faq_management': 'fm',
        'list': 'list'
    }
    # the command prefixes that the bot recognises

    FAQ_MANAGEMENT_COMMANDS = {
        'add': ['add', 'create', 'new', 'make'],
        'delete': ['delete', 'remove', 'incinerate', 'shred'],
        'edit': ['edit', 'change', 'modify'],
        'recycle': ['recycle', 'bin', 'faq-bin'],
        'download': ['export'],
        'bug-report-enabled': ['r-enabled', 'enable-reporting', 'bug-report'],
        'bug-report-cooldown': ['r-cooldown', 'reporting-cooldown', 'bug-report-cooldown']
    }

    PAGINATE_FAQ_LIST = 25

    BLACKLISTED_TAGS = ['list']

    try:
        bug_report_channel_path = os.path.join(
            os.getcwd(), 'bugreportchannelID.txt')
        with open(bug_report_channel_path, 'r') as f:
            BUG_REPORT_CHANNEL_ID = int(f.readline().strip())
    except:
        print("ERROR READING bugreportchannelID.txt")
        BUG_REPORT_CHANNEL_ID = 0

    BUG_REPORT_SPAM_DELAY = CONFIG['bug_report_cooldown']
    # delay (in seconds) between bug reports by users
    ALLOW_BUG_REPORTS = (
        CONFIG['allow_bug_reports'] if BUG_REPORT_CHANNEL_ID != 0 else False)
    
    with open(APPROVED_SERVERS_FILENAME, 'r') as f:
        APPROVED_SERVERS = list([line.strip() for line in f.readlines()])
    # load the approved servers IDs from the file

def paginate_list(l, n):
    '''
    This is just a simple function to take large list and
    split it into a list of sub-lists of no more than size n

    Returns l (list) paginated to pages of n (int) size
    '''
    return [l[i:i+n] for i in range(0, len(l), n)]

def loadFaqFile():
    '''
    This function just loads the json data from the FAQ file,
    then returns it.

    Returns the faq data read from the faq json file
    '''
    faq_data_path = os.path.join(os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME)
    with open(faq_data_path, 'r') as f:
        return json.load(f)

def dumpFaqFile(faq):
    '''
    This function dumps a dict into the FAQ file.
    Writes faq (json data) to the faq json file
    '''
    faq_data_path = os.path.join(os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME)
    with open(faq_data_path, 'w') as f:
        json.dump(faq, f, indent=4)

def addFaq(new_faq):
    '''
    Adds a FAQ to the faq data, and then dumps the faq data to the faq json
    file.
    '''
    faq_data['faq_data'].append(new_faq)
    faq_data['faq_data'] = sorted(
        faq_data['faq_data'], key=lambda faq: faq['title'])
    dumpFaqFile(faq_data)

def deleteFaq(faq_tag):
    '''
    Delete a FAQ from the faq data, and then dumps the faq data to the faq
    json file.
    '''
    faq = findFaqByTag(faq_tag)
    if faq == None:
        return
    faq_data_path = os.path.join(os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME_BIN)
    if not os.path.exists(faq_data_path):
        with open(faq_data_path, 'w') as f:
            f.write(json.dumps([], indent=4))

    with open(faq_data_path, 'r') as f:
        backup = json.load(f)
    backup.append(faq)
    with open(faq_data_path,'w') as f:
        f.write(json.dumps(backup, indent=4))

    faq_data['faq_data'].remove(faq)
    dumpFaqFile(faq_data)

def findFaqByTag(faq_tag):
    '''Returns the faq found by tag, if no FAQ exists, returns None'''
    found = list([x for x in faq_data['faq_data'] if faq_tag in x['tag']])
    if len(found) == 0:
        return None
    return found[0]

def searchFaqByTag(faq_tag):
    '''
    Returns the faq found by tag, otherwise tries to search for FAQ,
    otherwise returns None
    '''
    found = list([x for x in faq_data['faq_data'] if faq_tag in x['tag']])
    if len(found) == 0:
        # if no FAQ was found, search for it by looking through titles

        distances = []
        contains_tag_in_title = None
        contains_tag_in_info = None

        for faq in faq_data['faq_data']:
            for tag in faq['tag']:
                distance = 100 - fuzz.ratio(tag, faq_tag)
                if distance < 75:
                    distances.append([distance, faq])
            if faq_tag.replace('-', ' ').lower() in faq['title'].lower():
                contains_tag_in_title = faq
                distances.append([55, faq])
            if faq_tag.replace('-', ' ').lower() in faq['info'].lower():
                contains_tag_in_info = faq
                distances.append([65, faq])

        sorted_distances = sorted(distances, key=lambda i: i[0], reverse=False)

        if len(sorted_distances) > 0:
            return sorted_distances[0][1]

        return contains_tag_in_title or contains_tag_in_info or None

    return found[0]

def findMultipleFaqsByTag(faq_tag, count=10):
    '''
    Returns the faq found by tag, otherwise tries to search for FAQ,
    otherwise returns None.
    '''
    distances = []

    for faq in faq_data['faq_data']:
        for tag in faq['tag']:
            distance = 100 - fuzz.ratio(tag, faq_tag)
            if faq_tag.replace('-', ' ').lower() in faq['info'].lower():
                distance -= 30
            if faq_tag.replace('-', ' ').lower() in faq['title'].lower():
                distance -= 25
            if faq in list([i[1] for i in distances]):
                existing_entry = list([i for i in distances if i[1] == faq])[0]
                current_distance = existing_entry[0]
                if distance < current_distance:
                    distances.remove(existing_entry)
                else:
                    continue
            distances.append([distance, faq])

    sorted_distances = sorted(distances, key=lambda i: i[0], reverse=False)

    return list([i[1] for i in sorted_distances])[:count]

def flatten(l):
    '''Flattens a list.'''
    return [item for sublist in l for item in sublist]

def getValidAliases(aliases):
    '''
    Returns a list of all the aliases from the current list that aren't
    already part of other FAQs.
    '''
    current_aliases = flatten(list([f['tag'] for f in faq_data['faq_data']]))
    v = list([a for a in aliases if (not a in current_aliases)
              and (not a in BOT_DATA.BLACKLISTED_TAGS)])
    return v

def check(author, channel):
    '''Runs a check to confirm message author'''
    def inner_check(message):
        return message.author == author and message.channel == channel
    return inner_check

BUG_REPORTS_BY_USERS = {}

# client = commands.Bot(command_prefix = BOT_DATA.BOT_COMMAND_PREFIX)
client = discord.Client()

@client.event
async def on_ready():
    print(f"Logged into discord as {client}")
    command_prefix = BOT_DATA.BOT_COMMAND_PREFIX
    command_help = BOT_DATA.COMMAND_PREFIXES['help']
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=(f"the chat .. {command_prefix}{command_help}")
        )
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    author = message.author
    try:
        roles = author.roles
    except:
        roles = []
    channel = message.channel
    
    server_id = str(message.guild.id)
    # this is the actual id of the server that the message was sent in
    # converted it to a string, because strings are nicer I guess
    # also because the ids in the approved servers list are strings

    if isinstance(channel, discord.channel.DMChannel):
        # await channel.send("I don't execute commands in DMs, sorry")
        # don't execute commands in DMs
        return

    if message.content == f'{BOT_DATA.BOT_COMMAND_PREFIX}ping':
        # a debug message - listen for !ping
        await channel.send('pong!')

    if message.content.startswith(BOT_DATA.BOT_COMMAND_PREFIX):
        # check that this message is a command, e.g: '!help'

        print(f"[DEBUG] command called : {message.content}")

        command_request = message.content.split(
            BOT_DATA.BOT_COMMAND_PREFIX, 1)[-1]
        if command_request:
            # make sure the user didn't just type nothing

            command_split = command_request.split(' ')
            main_command = command_split[0]

            if main_command in BOT_DATA.COMMAND_PREFIXES['list']:
                # list out all the FAQ tags and text

                all_faq_tags = []

                for faq in faq_data['faq_data']:
                    faq_tags = (faq['tag'])
                    longest_tag = max(faq_tags, key=len)
                    all_faq_tags.append(longest_tag)

                all_faq_tags.sort()
                # sort the list of tags alphabetically

                paginated = paginate_list(
                    all_faq_tags, BOT_DATA.PAGINATE_FAQ_LIST)

                list_page = 1
                if len(command_split) > 1:
                    try:
                        list_page = int(command_split[1])
                    except:
                        list_page = 1
                list_page -= 1

                if list_page > len(paginated)-1:
                    list_page = 0

                if len(paginated) < 1:
                    await channel.send("No FAQs found")
                    return

                await channel.send(
                    '**All FAQ Tags**\n' +
                    ', '.join(['`%s`' % (x) for x in paginated[list_page]]) +
                    f'\n_page {list_page+1} of {len(paginated)}_'
                )

            if main_command == BOT_DATA.COMMAND_PREFIXES['bug'] and not CONFIG[
                    'allow_bug_reports']:
                # the user wants to report a bug, but bug reports are turned 
                # off
                embed = discord.Embed(
                    title='',
                    description=(
                        '**Bug report response**\n'
                        'Bug reports have been disabled, either temporarily '
                        'or permanently\n'
                        'If you still need to submit a bug,\n'
                        'DM @MACHINE_BUILDER#2245 or @SirLich#1658\n'
                    ),
                    colour=discord.Colour.red()
                )
                await channel.send(embed=embed)

            if main_command == BOT_DATA.COMMAND_PREFIXES['bug'] and CONFIG['allow_bug_reports']:
                # allows a user to create a bug report, which gets sent to a channel in 
                # another server
                report_size = (20, 1200)
                last_created_bug_report = BUG_REPORTS_BY_USERS.get(
                    author.id, 0.0)

                if last_created_bug_report+CONFIG['bug_report_cooldown'] > time.time():
                    # time delay is in-place
                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Bug report response**\n'
                            'You have submitted a bug report too recently. '
                            'Please wait a while before attempting to submit '
                            'another report'
                        ),
                        colour=discord.Colour.red()
                    )
                    await channel.send(embed=embed)
                    return

                embed = discord.Embed(
                    title='',
                    description=(
                        '**Please enter bug report**\n'
                        'Make sure to keep the bug report as descriptive, '
                        'and as concise as possible\n'
                        'Size constraints of bug report '
                        f'{report_size[0]}-{report_size[1]}\n'
                        '**Do not spam this command or you may be punished**\n'
                        'or type "x" to cancel'
                    ),
                    colour=discord.Colour.blue()
                )
                await channel.send(embed=embed)

                try:
                    bug_report_reply = await client.wait_for(
                        'message', check=check(author, channel), timeout=300)
                except:
                    bug_report_reply = None
                if bug_report_reply == None:
                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Creation of bug report timed out**\n'
                            'If you would like to retry, please re-type the '
                            f'command "{message.content}"'
                        ),
                        colour=discord.Colour.red()
                    )
                    await channel.send(embed=embed)
                    return

                bug_report = bug_report_reply.content

                if bug_report.lower() == 'x':
                    embed = discord.Embed(
                        title='',
                        description='**cancelled creation of bug report**',
                        colour=discord.Colour.red())
                    await channel.send(embed=embed)
                    return

                if len(bug_report) < report_size[0] or len(bug_report) > report_size[1]:
                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Bug report response**\n'
                            'Your bug report is not within the size '
                            f'constraints of {report_size[0]}-{report_size[1]}'
                        ),
                        colour=discord.Colour.red()
                    )
                    await channel.send(embed=embed)
                    return
                
                current_time = datetime.datetime.fromtimestamp(
                    time.time()).strftime("%Y-%m-%d %H:%M:%S")
                embed_report = discord.Embed(
                    title='FAQ Bot Bug Report',
                    description=(
                        'Bug Report Created By '
                        f'**@{author.name}#{author.discriminator}** at '
                        f'**{current_time}**'),
                    colour=discord.Colour.blue()
                )
                embed_report.add_field(
                    name=(
                        f'Report Content ( From : [{channel.guild.name} - '
                        f'#{channel.name}] )'),
                    value=bug_report,
                    inline=False
                )
                BUG_REPORTS_BY_USERS[author.id] = time.time()
                embed = discord.Embed(
                    title='',
                    description=(
                        '**Bug report response**\n'
                        'Your bug report has been submitted'
                    ),
                    colour=discord.Colour.green()
                )
                await channel.send(embed=embed)

                bug_report_channel = client.get_channel(
                    BOT_DATA.BUG_REPORT_CHANNEL_ID)
                await bug_report_channel.send(embed=embed_report)

            if main_command == BOT_DATA.COMMAND_PREFIXES['search']:
                # send the search message response
                # The search menu of the bot
                search_tag = ' '.join(command_split[1:])

                print(search_tag)

                if search_tag == '':
                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Invalid use of the command**\n'
                            'Please specify a tag to search for,\n'
                            f'example: "{BOT_DATA.BOT_COMMAND_PREFIX}'
                            f'{BOT_DATA.COMMAND_PREFIXES["search"]} '
                            '_some search tag_"'
                        ),
                        colour=discord.Colour.red()
                    )
                    await channel.send(embed=embed)
                    return

                found = findMultipleFaqsByTag(search_tag, count=8)

                embed = discord.Embed(
                    title='Related FAQs',
                    description='---',
                    colour=discord.Colour.blue()
                )

                for faq_entry in found:
                    embed.add_field(
                        name=faq_entry['title'].title(),
                        value=', '.join(faq_entry['tag']),
                        inline=False
                    )
                embed.set_footer(
                    text=f'({len(found)} total similar faq entries)')
                await channel.send(embed=embed)

            if main_command == BOT_DATA.COMMAND_PREFIXES['help']:
                # send the help message response
                # The help menu of the bot

                embed = discord.Embed(
                    title='Bedrock Scripting FAQ Help',
                    description=(
                        'The Bedrock Scripting FAQ Bot\'s commands are as '
                        'follows:'),
                    colour=discord.Colour.blue()
                )

                embed.add_field(
                    name=(
                        f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                        f'{BOT_DATA.COMMAND_PREFIXES["help"]}'),
                    value='Displays the bot\'s help menu',
                    inline=False
                )

                embed.add_field(
                    name=(
                        f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                        f'{BOT_DATA.COMMAND_PREFIXES["search"]}'),
                    value='Searches through FAQs',
                    inline=False
                )

                embed.add_field(
                    name=(
                        f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                        f'{BOT_DATA.COMMAND_PREFIXES["list"]} '
                        '[page:int]'),
                    value=(
                        f'Displays a list of all FAQs, example: '
                        f'"{BOT_DATA.BOT_COMMAND_PREFIX}'
                        f'{BOT_DATA.COMMAND_PREFIXES["list"]} 2"'),
                    inline=False
                )

                embed.add_field(
                    name=f'{BOT_DATA.FAQ_QUERY_PREFIX} [tag]',
                    value=(
                        'Displays the FAQ with the given tag or alias, along '
                        'with its answer, example: '
                        f'"{BOT_DATA.FAQ_QUERY_PREFIX} some faq"'),
                    inline=False
                )

                if CONFIG['allow_bug_reports']:
                    embed.add_field(
                        name=(
                            f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                            f'{BOT_DATA.COMMAND_PREFIXES["bug"]}'),
                        value=f'Report a bug within the bot to the developers',
                        inline=False
                    )

                if len(command_split) > 1:
                    if 'fm' in command_split:
                        if BOT_DATA.FAQ_MANAGEMENT_ROLE in [
                                role.name for role in roles]:
                            embed.add_field(
                                name=(
                                    f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                                    f'{"/".join(BOT_DATA.FAQ_MANAGEMENT_COMMANDS["add"])}'),
                                value='Create a new FAQ',
                                inline=False
                            )

                            embed.add_field(
                                name=(
                                    f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                                    f'{"/".join(BOT_DATA.FAQ_MANAGEMENT_COMMANDS["delete"])}'
                                    ' [faq tag]'),
                                value='Delete a FAQ',
                                inline=False
                            )

                            embed.add_field(
                                name=(
                                    f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                                    f'{"/".join(BOT_DATA.FAQ_MANAGEMENT_COMMANDS["edit"])}'),
                                value='Edit an existing FAQ',
                                inline=False
                            )

                    if 'admin' in command_split:
                        if BOT_DATA.BOT_ADMIN_ROLE in [
                                role.name for role in roles]:
                            embed.add_field(
                                name=(
                                    f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                                    f'{"/".join(BOT_DATA.FAQ_MANAGEMENT_COMMANDS["recycle"])}'
                                ),
                                value=f'Download the {BOT_DATA.FAQ_DATA_FILENAME_BIN} file',
                                inline=False
                            )
                            embed.add_field(
                                name=(
                                    f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                                    f'{"/".join(BOT_DATA.FAQ_MANAGEMENT_COMMANDS["bug-report-enabled"])}'
                                    ' [true/false]'),
                                value=f'Enable or disable the bug reporting function',
                                inline=False
                            )
                            embed.add_field(
                                name=(
                                    f'{BOT_DATA.BOT_COMMAND_PREFIX}'
                                    f'{"/".join(BOT_DATA.FAQ_MANAGEMENT_COMMANDS["bug-report-cooldown"])}'
                                    ' [int]'),
                                value=(
                                    'Amount of delay (seconds) between user '
                                    'bug reports'),
                                inline=False
                            )
                await channel.send(embed=embed)

            # check if the command is a !fm command
            action = main_command

            if (BOT_DATA.BOT_ADMIN_ROLE in [role.name for role in roles]) and (server_id in BOT_DATA.APPROVED_SERVERS):
                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS[
                        'bug-report-enabled']:
                    if len(command_split) != 2:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Invalid use of the command**\n'
                                'Make sure to specify true or false in your '
                                'argument\n'
                                f'Example: {BOT_DATA.BOT_COMMAND_PREFIX}'
                                f'{BOT_DATA.FAQ_MANAGEMENT_COMMANDS["bug-report-enabled"][0]}'
                                ' false'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    trueFalse = command_split[1].lower() == 'true'
                    CONFIG['allow_bug_reports'] = trueFalse
                    dumpConfig()

                    if trueFalse:
                        embed = discord.Embed(
                            title='',
                            description='**Enabled bug reporting**',
                            colour=discord.Colour.green()
                        )
                        await channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title='',
                            description='**Disabled bug reporting**',
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)

                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS[
                        "bug-report-cooldown"]:
                    if len(command_split) != 2:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Invalid use of the command**\n'
                                'Make sure to specify the delay in your '
                                'argument\n'
                                f'Example: {BOT_DATA.BOT_COMMAND_PREFIX}'
                                f'{BOT_DATA.FAQ_MANAGEMENT_COMMANDS["bug-report-cooldown"][0]}'
                                ' 300'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return
                    newDelay = int(command_split[1])
                    CONFIG['bug_report_cooldown'] = newDelay
                    dumpConfig()

                    embed = discord.Embed(
                        title='',
                        description=f'**Set bug reporting delay to {newDelay} seconds**',
                        colour=discord.Colour.green()
                    )
                    await channel.send(embed=embed)
                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['recycle']:
                    # download the faq_bin.json
                    faq_data_filename_bin_path = os.path.join(
                        os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME_BIN)
                    await channel.send(
                        f"{BOT_DATA.FAQ_DATA_FILENAME_BIN}",
                        file=discord.File(faq_data_filename_bin_path))
                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['download']:
                    # download the faq.json
                    faq_data_filename_path = os.path.join(
                        os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME)
                    await channel.send(
                        f"{BOT_DATA.FAQ_DATA_FILENAME}",
                        file=discord.File(faq_data_filename_path))

            if (BOT_DATA.FAQ_MANAGEMENT_ROLE in [role.name for role in roles]) and (server_id in BOT_DATA.APPROVED_SERVERS):
                # print("[DEBUG] caller has adequate privellages to use 
                # !fm commands this this command")

                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['add']:
                    # add a FAQ
                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Please enter FAQ tags**\n'
                            'example : tag 1, tag 2, some other tag, or enter'
                            ' "x" to cancel'
                        ),
                        colour=discord.Colour.blue()
                    )
                    await channel.send(embed=embed)
                    try:
                        faq_tags_reply = await client.wait_for(
                            'message', check=check(author, channel),
                            timeout=120)
                    except:
                        faq_tags_reply = None
                    if faq_tags_reply == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Creation of new FAQ timed out**\n'
                                'If you would like to retry, please re-type '
                                f'the command "{message.content}"'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    faq_tags_reply_content = faq_tags_reply.content
                    if faq_tags_reply_content.lower() == 'x':
                        # do nothing, since the user cancelled the FAQ creation
                        embed = discord.Embed(
                            title='',
                            description=f'''**Cancelled FAQ Creation**''',
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    try:
                        aliases = faq_tags_reply_content
                        # !fm add alias1, alias2, something else, comma
                        # seperated
                        aliases_list = list(
                            [
                                a.strip().replace(' ', '-').lower()
                                for a in aliases.split(',')
                            ]
                        )
                        valid_aliases = getValidAliases(aliases_list)
                    except:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Invalid use of the command. Make sure to '
                                'specify FAQ tag(s)**\n'
                                'Error reading FAQ tags, example: \'tag 1, '
                                'tag 2\''
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    if len(valid_aliases) < 1:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Invalid FAQ tags**\n'
                                'Every tag you listed is already in use by '
                                'other FAQs'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Creating a new FAQ with the tags '
                            f'[{", ".join(valid_aliases) }]**\n'
                            'Please enter the FAQ Title, or type "x" to cancel'
                        ),
                        colour=discord.Colour.blue()
                    )
                    await channel.send(embed=embed)

                    try:
                        faq_title_reply = await client.wait_for(
                            'message', check=check(author, channel),
                            timeout=120)
                    except:
                        faq_title_reply = None

                    if faq_title_reply == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                f'**Creation of new FAQ timed out**\n'
                                f'If you would like to retry, please re-type '
                                f'the command "{message.content}"'
                            ),
                            colour=discord.Colour.blue()
                        )
                        await channel.send(embed=embed)
                        return

                    faq_title_reply_content = faq_title_reply.content

                    if faq_title_reply_content.lower() == 'x':
                        # do nothing, since the user cancelled the FAQ creation
                        embed = discord.Embed(
                            title='',
                            description='**Cancelled FAQ Creation**',
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    # faq_title_reply_content is the new FAQ's title

                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Set the FAQ\'s title to '
                            f'{faq_title_reply_content}**\n'
                            'Please enter the FAQ Description, and include any'
                            ' relative links, or type "x" to cancel'
                        ),
                        colour=discord.Colour.blue()
                    )
                    await channel.send(embed=embed)
                    try:
                        faq_description_reply = await client.wait_for(
                            'message', check=check(author, channel),
                            timeout=600)
                    except:
                        faq_description_reply = None
                    if faq_description_reply == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Setting FAQ description timed out**\n'
                                'If you would like to retry, please re-type '
                                f'the command "{message.content}"'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    faq_description = faq_description_reply.content

                    if faq_description.lower() == 'x':
                        # do nothing, since the user cancelled setting the FAQ
                        # description
                        embed = discord.Embed(
                            title='',
                            description=f'''**Cancelled FAQ Creation**''',
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    # faq_description is the new FAQ's description
                    try:
                        new_faq = {
                            "tag": valid_aliases,
                            "title": faq_title_reply_content,
                            "info": faq_description
                        }

                        if faq_description_reply.attachments:
                            new_faq["image"] = str(faq_description_reply.attachments).split("url='")[1][:-3]
                        # tries to set image link


                        addFaq(new_faq)

                        embed = discord.Embed(
                            title='',
                            description='**Successfully created a new FAQ**',
                            colour=discord.Colour.green()
                        )
                        await channel.send(embed=embed)

                    except:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Error while trying to create new FAQ**'),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['edit']:
                    # edit an existing FAQ
                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Please enter tag of FAQ you wish to edit**\n'
                            'enter the FAQ\'s tag, or enter "x" to cancel'
                        ),
                        colour=discord.Colour.blue()
                    )
                    await channel.send(embed=embed)

                    try:
                        faq_tags_reply = await client.wait_for(
                            'message', check=check(author, channel),
                            timeout=120)
                    except:
                        faq_tags_reply = None

                    if faq_tags_reply == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**FAQ edit timed out**\n'
                                'If you would like to retry, please re-type '
                                f'the command "{message.content}"'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    faq_tag_reply_content = faq_tags_reply.content
                    if faq_tag_reply_content.lower() == 'x':
                        # do nothing, since the user cancelled the FAQ editing
                        embed = discord.Embed(
                            title='',
                            description=f'''**Cancelled FAQ Editing**''',
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    search_for = faq_tag_reply_content
                    if search_for == '':
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Invalid use of the command. Make sure to '
                                'specify FAQ tag**\n'
                                'Error reading FAQ tag, example: \'tag 1\''
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    found_faq = searchFaqByTag(search_for)
                    if found_faq == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                f"**No FAQ found with tag {search_for}**"),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    embed = discord.Embed(
                        title='',
                        description=(
                            f'**Found FAQ ({found_faq["title"]})**\n'
                            f'Select an attribute of the FAQ to edit,\n'
                            f'valid attributes:\n'
                            f'_ - t: title_\n'
                            f'_ - ta: tags_\n'
                            f'_ - d: description_\n'
                            f'or type "x" to cancel\n'
                        ),
                        colour=discord.Colour.blue()
                    )
                    await channel.send(embed=embed)

                    try:
                        faq_edit_attribute = await client.wait_for(
                            'message', check=check(author, channel),
                            timeout=120)
                    except:
                        faq_edit_attribute = None

                    if faq_edit_attribute == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ timed out**\n'
                                'If you would like to retry, please re-type '
                                f'the command "{message.content}"'
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    faq_edit_attribute_choice = faq_edit_attribute.content
                    if faq_edit_attribute_choice.lower() == 'x':
                        # do nothing, since the user cancelled the FAQ creation
                        embed = discord.Embed(
                            title='',
                            description=f'''**Cancelled FAQ Editing**''',
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    if faq_edit_attribute_choice.lower() in ['t', 'title']:

                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ**\n'
                                'Please enter a new title for the FAQ, or '
                                'enter "x" to cancel'
                            ),
                            colour=discord.Colour.blue()
                        )
                        await channel.send(embed=embed)
                        try:
                            msgresp = await client.wait_for(
                                'message', check=check(author, channel),
                                timeout=120)
                            response = msgresp.content
                        except:
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**FAQ edit timed out**\n'
                                    'If you would like to retry, please '
                                    f're-type the command "{message.content}"'
                                ),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        if response.lower() == 'x':
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Editing FAQ cancelled**\n'
                                    'Cancelled editing FAQ title'
                                ),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        deleteFaq(found_faq['tag'][0])
                        found_faq['title'] = response
                        addFaq(found_faq)

                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ**\n'
                                'Edited FAQ title'),
                            colour=discord.Colour.green()
                        )
                        await channel.send(embed=embed)

                    elif faq_edit_attribute_choice.lower() in ['ta', 'tags']:

                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ**\n'
                                'Please enter the new tags for the FAQ, or '
                                'enter "x" to cancel'),
                            colour=discord.Colour.blue()
                        )
                        await channel.send(embed=embed)
                        try:
                            msgresp = await client.wait_for(
                                'message', check=check(author, channel),
                                timeout=120)
                            response = msgresp.content
                        except:
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Editing FAQ timed out**\n'
                                    'If you would like to retry, please '
                                    f're-type the command "{message.content}"'
                                ),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        if response.lower() == 'x':
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Editing FAQ cancelled**\n'
                                    'Cancelled editing FAQ tags'),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        tags = list([t.strip().replace(' ', '-').lower()
                                     for t in response.split(',')])
                        if tags == []:
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Invalid FAQ tags**\n'
                                    'You must enter one or more tags, example:'
                                    ' "tag 1, tag 2"'),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        deleteFaq(found_faq['tag'][0])

                        valid_tags = getValidAliases(tags)

                        if len(valid_tags) == 0:
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Invalid FAQ tags**\n'
                                    'All the tags you entered are already '
                                    'used in other FAQs, please use different '
                                    'tags'),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        found_faq['tag'] = valid_tags
                        addFaq(found_faq)
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ**\n'
                                'Edited FAQ tags'),
                            colour=discord.Colour.green()
                        )
                        await channel.send(embed=embed)

                    elif faq_edit_attribute_choice.lower() in ['d', 'description']:

                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ**\n'
                                'Please enter a new description for the FAQ, '
                                'or enter "x" to cancel'),
                            colour=discord.Colour.blue()
                        )
                        await channel.send(embed=embed)
                        try:
                            msgresp = await client.wait_for(
                                'message', check=check(author, channel),
                                timeout=300)
                            response = msgresp.content
                        except:
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Editing FAQ timed out**\n'
                                    'If you would like to retry, please '
                                    f're-type the command "{message.content}"'
                                ),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        if response == '':
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Invalid FAQ description**\n'
                                    'You cannot leave the description of a '
                                    'FAQ blank'),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        if response.lower() == 'x':
                            embed = discord.Embed(
                                title='',
                                description=(
                                    '**Editing FAQ cancelled**\n'
                                    'Cancelled editing FAQ description'
                                ),
                                colour=discord.Colour.red()
                            )
                            await channel.send(embed=embed)
                            return

                        deleteFaq(found_faq['tag'][0])
                        found_faq['info'] = response
                        if msgresp.attachments:
                            found_faq["image"] = str(
                                msgresp.attachments).split("url='")[1][:-3]
                        # tries to set image link
                        else:
                            found_faq["image"] = ''
                        # if no attachments, resets the image field
                        addFaq(found_faq)

                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Editing FAQ**\n'
                                'Edited FAQ description'),
                            colour=discord.Colour.green()
                        )
                        await channel.send(embed=embed)

                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['delete']:
                    # delete a faq with a certain tag

                    try:
                        faq_tag = ' '.join(
                            command_split[1:len(command_split)]
                        ).strip().replace(' ', '-').lower()
                        assert faq_tag != ''
                    except:
                        embed = discord.Embed(
                            title='',
                            description=(
                                "**Invalid use of the command. Make sure to "
                                "specify a FAQ tag**\n"
                                f"Example use : '{BOT_DATA.BOT_COMMAND_PREFIX}"
                                f"{BOT_DATA.FAQ_MANAGEMENT_COMMANDS['delete'][0]} "
                                "faq tag'"
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    if findFaqByTag(faq_tag) == None:
                        embed = discord.Embed(
                            title='',
                            description=(
                                '**Invalid FAQ tag**\n'
                                f'There is no FAQ with the tag "{faq_tag}", '
                                f"use '{BOT_DATA.FAQ_QUERY_PREFIX}"
                                f"{BOT_DATA.FAQ_MANAGEMENT_COMMANDS['list'][0]}"
                                "\' to list out FAQs"
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    embed = discord.Embed(
                        title='',
                        description=(
                            '**Found FAQ**\n'
                            'Are you sure you wish to delete this FAQ? '
                            'Deleting a FAQ is permenant\n'
                            'To confirm, the FAQ you are about to delete is '
                            f'titled **{findFaqByTag(faq_tag)["title"]}**\n'
                            'Type yes to continue, or anything else to cancel'
                        ),
                        colour=discord.Colour.blue()
                    )
                    await channel.send(embed=embed)

                    try:
                        faq_delete_reply = await client.wait_for('message', check=check(author, channel), timeout=25)
                    except:
                        faq_delete_reply = None

                    if faq_delete_reply == None:
                        # do nothing, since the user cancelled deleting the FAQ
                        embed = discord.Embed(
                            title='',
                            description=(
                                "**FAQ deletion timed out**\n"
                                "FAQ delete confirmation message timed out\n"
                                "If you would like to retry, please re-type "
                                f"the command \"{message.content}\""
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)
                        return

                    if faq_delete_reply.content == 'yes':
                        # delete the FAQ
                        deleteFaq(faq_tag)
                        embed = discord.Embed(
                            title='',
                            description=f"**FAQ has been deleted**",
                            colour=discord.Colour.green()
                        )
                        await channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title='',
                            description=(
                                "**FAQ deletion cancelled**\n"
                                "The FAQ '{faq_tag}' has not been deleted"
                            ),
                            colour=discord.Colour.red()
                        )
                        await channel.send(embed=embed)

    if message.content.startswith(BOT_DATA.FAQ_QUERY_PREFIX):
        # check that this message is a command, e.g: '?[tag]'

        print(f"[DEBUG] command (FAQ) called : {message.content}")

        command_request = message.content.split(
            BOT_DATA.FAQ_QUERY_PREFIX, 1)[-1]
        command_split = command_request.split(' ')
        main_command = command_split[0]

        try:
            faq_tag_searches = message.content.split(
                BOT_DATA.FAQ_QUERY_PREFIX, 1
            )[-1].strip().replace(' ', '-').lower()
        except:
            faq_tag_searches = None

        if not faq_tag_searches:
            faq_tag_searches = None

        if faq_tag_searches == None:
            return

        if len(list([c for c in faq_tag_searches if c in ascii_letters])) == 0:
            return

        faq = searchFaqByTag(faq_tag_searches)
        if faq == None:
            embed = discord.Embed(
                title='',
                description=(
                    "**No FAQs could be found when searching for "
                    f'"{faq_tag_searches}"**\n'
                    "You can use '"
                    f"{BOT_DATA.BOT_COMMAND_PREFIX}"
                    f"{BOT_DATA.COMMAND_PREFIXES['list']}' to see a "
                    "list of all FAQs"
                ),
                colour=discord.Colour.red()
            )
            await channel.send(embed=embed)
            return

        embed = discord.Embed(
            title=faq["title"],
            description=faq["info"],
            colour=discord.Colour.blue()
        )

        try:
            embed.set_image(url=faq["image"])
        except:
            pass
        # adds image to embed

        msg = await channel.send(embed=embed)

        await msg.add_reaction('🚫')

        def check_reactions(reaction, user):
            return (
                user.id == author.id and reaction.emoji == '🚫' and
                reaction.message.id == msg.id)

        try:
            await client.wait_for(
                'reaction_add', timeout=12.5, check=check_reactions)
        except:
            await msg.remove_reaction('🚫', client.user)
        else:
            await msg.delete()
            try:
                await message.delete()
            except:
                print("Failed to delete message, may need extra permissions")

if not os.path.exists(os.path.join(os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME)):
    print("[DEBUG] making empty faq file, since faq file is missing")
    dumpFaqFile(
        {
            "faq_data": []
        }
    )

faq_data = loadFaqFile()

print("[DEBUG] loaded faq data")
# print(json.dumps(faq_data,indent=2))

client.run(open(os.path.join(os.getcwd(), BOT_DATA.TOKEN_FILENAME),
                'r').readline().strip())
