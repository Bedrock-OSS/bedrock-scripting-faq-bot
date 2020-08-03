import discord
from discord.ext import commands
# was going to use the commands lib, but personally I find it easier to use the discord.Client() instead

import json, os



class BOT_DATA:

    BOT_COMMAND_PREFIX = '!'
    # the string that the bot recognises as a command
    FAQ_QUERY_PREFIX = '?'
    # the string that the bot recognises as a FAQ query

    TOKEN_FILENAME = 'token.txt'
    # the filename of the txt file where the bot token is stored



    FAQ_DATA_FILENAME = 'faq.json'
    FAQ_DATA_FILENAME_BIN = 'faq_bin.json'



    FAQ_MANAGEMENT_ROLE = 'faq-management'
    # the role that can manage the faqs

    COMMAND_PREFIXES = {
        'help': 'help',
        'faq_viewing': 'faq',
        'faq_management': 'fm'
    }
    # the command prefixes that the bot recognises

    FAQ_MANAGEMENT_COMMANDS = {
        'list': ['list', 'all', 'faqs'],
        'add': ['add', 'create'],
        'delete': ['delete', 'remove', 'incinerate']
    }

    PAGINATE_FAQ_LIST = 8





'''
https://codereview.stackexchange.com/questions/217065/calculate-levenshtein-distance-between-two-strings-in-python

implement this
'''








'''
this is just a simple function to take large list and
split it into a list of sub-lists of no more than size n
'''
def paginate_list(l,n):
    '''Returns l (list) paginated to pages of n (int) size'''
    return [l[i:i+n] for i in range(0,len(l),n)]



'''
this function just loads the json data from the FAQ file,
then returns it
'''
def loadFaqFile():
    '''Returns the faq data read from the faq json file'''
    return json.load(open( os.path.join(os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME) , 'r'))

'''
this function dumps a dict into the FAQ file
'''
def dumpFaqFile(faq):
    '''Writes faq (json data) to the faq json file'''
    json.dump(faq, open( os.path.join(os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME) , 'w'), indent=4)

def addFaq(new_faq):
    '''Adds a FAQ to the faq data, and then dumps the faq data to the faq json file'''
    faq_data['faq_data'].append(new_faq)
    dumpFaqFile(faq_data)

def deleteFaq(faq_tag):
    '''Delete a FAQ from the faq data, and then dumps the faq data to the faq json file'''
    faq = findFaqByTag(faq_tag)

    
    if not os.path.exists( os.path.join( os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME_BIN ) ):
        open(os.path.join( os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME_BIN ), 'w').write( json.dumps([],indent=4) )
    
    backup = json.load( open(os.path.join( os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME_BIN ), 'r') )
    backup.append(faq)
    open(os.path.join( os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME_BIN ), 'w').write( json.dumps(backup,indent=4) )

    faq_data['faq_data'].remove(faq)
    dumpFaqFile(faq_data)

def findFaqByTag(faq_tag):
    '''Returns the faq found by tag, if no FAQ exists, returns None'''
    found = list( [ x for x in faq_data['faq_data'] if faq_tag in x['tag'] ] )
    if len(found) == 0: return None
    return found[0]

'''
this function just flattens a list
'''
flatten = lambda l: [item for sublist in l for item in sublist]

def getValidAliases(aliases):
    '''Returns a list of all the aliases from the current list that aren't already part of other FAQs'''
    current_aliases = flatten( list( [f['tag'] for f in faq_data['faq_data']] ) )
    v = list([a for a in aliases if not a in current_aliases])
    return v

def check(author, channel):
    '''Runs a check to confirm message author'''
    def inner_check(message):
        return message.author == author and message.channel == channel
    return inner_check









# client = commands.Bot(command_prefix = BOT_DATA.BOT_COMMAND_PREFIX)
client = discord.Client()


@client.event
async def on_ready():
    print(f"Logged into discord as {client}")



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    author = message.author
    roles = author.roles
    channel = message.channel
    


    if message.content == f'{BOT_DATA.BOT_COMMAND_PREFIX}ping':
        # a debug message - listen for !ping
        await channel.send('pong!')
    


    if message.content.startswith(BOT_DATA.BOT_COMMAND_PREFIX):
        # check that this message is a command, e.g: '!help'

        print(f"[DEBUG] command called : {message.content}")

        command_request = message.content.split( BOT_DATA.BOT_COMMAND_PREFIX, 1 )[-1]
        if command_request:
            # make sure the user didn't just type nothing
            
            command_split = command_request.split(' ')
            main_command = command_split[0]




            if main_command == BOT_DATA.COMMAND_PREFIXES['help']:
                # send the help message response
                '''
                The help menu of the bot
                '''
                
                embed = discord.Embed(
                    title = 'Bedrock Scripting FAQ Help',
                    description = 'The Bedrock Scripting FAQ Bot\'s commands are as follows;',
                    colour = discord.Colour.blue()
                )

                embed.add_field(
                    name = f'{BOT_DATA.BOT_COMMAND_PREFIX}help',
                    value = 'Displays the bot\'s help menu',
                    inline = False
                )

                embed.add_field(
                    name = f'{BOT_DATA.FAQ_QUERY_PREFIX} [tag]',
                    value = 'Displays the FAQ with the given tag or alias, along with its answer',
                    inline = False
                )

                if len(command_split) > 1:

                    if command_split[1] == 'fm':

                        if BOT_DATA.FAQ_MANAGEMENT_ROLE in [role.name for role in roles]:

                            embed.add_field(
                                name = f'{BOT_DATA.BOT_COMMAND_PREFIX}fm',
                                value = 'The bot\'s FAQ management commands',
                                inline = False
                            )

                            embed.add_field(
                                name = f'{BOT_DATA.BOT_COMMAND_PREFIX}fm list',
                                value = 'Lists all FAQ tags',
                                inline = False
                            )

                await channel.send(embed=embed)




                






            '''check if the command is a !fm command'''

            action = main_command

            print(action)






            if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['list']:
                # list out all the FAQ tags and text

                list_page = 1
                if len(command_split) > 2:
                    try: list_page = int(command_split[2])
                    except: list_page = 1
                list_page -= 1

                embed = discord.Embed(
                    title = 'All FAQ tags',
                    description = '---',
                    colour = discord.Colour.blue()
                )

                all_faq_entries = faq_data['faq_data']
                paginated_faq_entries = paginate_list(all_faq_entries, BOT_DATA.PAGINATE_FAQ_LIST)

                if list_page > len(paginated_faq_entries)-1:
                    list_page = 0
                
                if len(paginated_faq_entries) < 1:
                    embed.add_field(
                        name = 'ERROR: No FAQs Found',
                        value = '-',
                        inline = False
                    )
                
                else:
                    for faq_entry in paginated_faq_entries[ list_page ]:
                        embed.add_field(
                            name = ', '.join( faq_entry['tag'] ),
                            value = faq_entry['title'],
                            inline = False
                        )
                
                embed.set_footer(text=f'''\
page {list_page+1} of {len(paginated_faq_entries)}
({len(all_faq_entries)} total faq entries)
Use "{BOT_DATA.BOT_COMMAND_PREFIX}{BOT_DATA.COMMAND_PREFIXES['faq_management']} {BOT_DATA.FAQ_MANAGEMENT_COMMANDS['list']} [page]" to list a given page of FAQs''')

                await channel.send(embed=embed)






            if BOT_DATA.FAQ_MANAGEMENT_ROLE in [role.name for role in roles]:
                print("[DEBUG] caller has adequate privellages to use !fm commands this this command")                    

                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['add']:
                    # add a FAQ

                    await channel.send(f'''\
**Please enter FAQ tags**
example : tag 1, tag 2, some other tag''')

                    try: faq_tags_reply = await client.wait_for('message', check=check(author, channel), timeout=120)
                    except: faq_tags_reply = None

                    if faq_tags_reply == None:
                        await channel.send(f'''\
**Creation of new FAQ timed out**
If you would like to retry, please re-type the command "{message.content}"''')
                        return
                    
                    faq_tags_reply_content = faq_tags_reply.content

                    if faq_tags_reply_content == 'x':
                        # do nothing, since the user cancelled the FAQ creation
                        return

                    try:

                        aliases = faq_tags_reply_content
                        # !fm add alias1, alias2, something else, comma seperated
                        aliases_list = list( [a.strip().replace(' ','-').lower() for a in aliases.split(',')] )
                        valid_aliases = getValidAliases(aliases_list)

                    except:
                        await channel.send(f"""\
**Invlaid use of the command. Make sure to specify FAQ tag(s)**
Example use :'{BOT_DATA.BOT_COMMAND_PREFIX}{BOT_DATA.COMMAND_PREFIXES['faq_management']} {BOT_DATA.FAQ_MANAGEMENT_COMMANDS['add']} tag name, alias 1, alias 2'""")
                        return
                    
                    if len(valid_aliases) < 1:
                        await channel.send(f'''\
**Invalid FAQ tags**
Every tag you listed is already in use by other FAQs''')
                        return

                    await channel.send(f'''\
**Creating a new FAQ with the tags [{ ', '.join(valid_aliases) }]**
Please enter the FAQ Title, or type "x" to cancel''')

                    try: faq_title_reply = await client.wait_for('message', check=check(author, channel), timeout=120)
                    except: faq_title_reply = None

                    if faq_title_reply == None:
                        await channel.send(f'''\
**Creation of new FAQ timed out**
If you would like to retry, please re-type the command "{message.content}"''')
                        return
                    
                    faq_title_reply_content = faq_title_reply.content

                    if faq_title_reply_content == 'x':
                        # do nothing, since the user cancelled the FAQ creation
                        return
                    
                    # faq_title_reply_content is the new FAQ's title

                    await channel.send(f'''\
**Set the FAQ's title to {faq_title_reply_content}**
Please enter the FAQ Description, and include any relative links, or type "x" to cancel''')

                    try: faq_description_reply = await client.wait_for('message', check=check(author, channel), timeout=300)
                    except: faq_description_reply = None

                    if faq_description_reply == None:
                        await channel.send(f'''\
**Setting FAQ description timed out**
If you would like to retry, please re-type the command "{message.content}"''')
                        return
                    
                    faq_description = faq_description_reply.content

                    if faq_description == 'x':
                        # do nothing, since the user cancelled setting the FAQ description
                        return
                    
                    # faq_description is the new FAQ's description

                    await channel.send(f'''\
**Successfully created a new FAQ**''')

                    new_faq = {
                        "tag": valid_aliases,
                        "title": faq_title_reply_content,
                        "info": faq_description
                    }

                    addFaq(new_faq)


                    

                if action in BOT_DATA.FAQ_MANAGEMENT_COMMANDS['delete']:
                    # delete a faq with a certain tag

                    try:
                        faq_tag = ' '.join( command_split[1:len(command_split)] ).strip().replace(' ','-').lower()
                        assert faq_tag != ''
                    except:
                        await channel.send(f"""\
**Invlaid use of the command. Make sure to specify a FAQ tag**
Example use :'{BOT_DATA.BOT_COMMAND_PREFIX}{BOT_DATA.COMMAND_PREFIXES['faq_management']} {BOT_DATA.FAQ_MANAGEMENT_COMMANDS['delete']} faq-tag [must not contain spaces]'""")
                        return
                    
                    if findFaqByTag(faq_tag) == None:
                        await channel.send(f'''\
**Invalid FAQ tag**
There is no FAQ with the tag "{faq_tag}", use '{BOT_DATA.BOT_COMMAND_PREFIX}{BOT_DATA.COMMAND_PREFIXES['faq_management']} {BOT_DATA.FAQ_MANAGEMENT_COMMANDS['list']}' to list out FAQs''')
                        return

                    await channel.send(f"""\
**Found FAQ**
Are you sure you wish to delete this FAQ? Deleting a FAQ is permenant
Type yes to continue, or anything else to cancel""")

                    try: faq_delete_reply = await client.wait_for('message', check=check(author, channel), timeout=25)
                    except: faq_delete_reply = None

                    if faq_delete_reply == None:
                        # do nothing, since the user cancelled deleting the FAQ
                        await channel.send(f"""\
**FAQ deletion timed out**
FAQ delete confirmation message timed out
If you would like to retry, please re-type the command \"{message.content}\"""")
                        return
                    
                    if faq_delete_reply.content == 'yes':
                        # delete the FAQ
                        deleteFaq(faq_tag)
                        await channel.send(f"""\
**FAQ has been deleted**""")
                    else:
                        await channel.send(f"""\
**FAQ deletion cancelled**
The FAQ '{faq_tag}' has not been deleted""")




















    if message.content.startswith(BOT_DATA.FAQ_QUERY_PREFIX):
        # check that this message is a command, e.g: '!help'

        try:
            faq_tag_searches = message.content.split( BOT_DATA.FAQ_QUERY_PREFIX, 1 )[-1].strip().replace(' ','-').lower()
        except:
            faq_tag_searches = None

        if not faq_tag_searches:
            faq_tag_searches = None
    
        if faq_tag_searches == None:
            await channel.send(f"""\
**Invlaid use of the command. Make sure to specify FAQ tag(s)**
Example use :'{BOT_DATA.FAQ_QUERY_PREFIX} some faq tag'
You can also use '{BOT_DATA.BOT_COMMAND_PREFIX}{BOT_DATA.FAQ_MANAGEMENT_COMMANDS['list'][0]}' to see a list of all FAQs""")
            return

        faq = findFaqByTag( faq_tag_searches )

        if faq == None:
            await channel.send(f"""\
**There is no FAQ with the tag {faq_tag_searches}**
You can use '{BOT_DATA.BOT_COMMAND_PREFIX}{BOT_DATA.FAQ_MANAGEMENT_COMMANDS['list'][0]}' to see a list of all FAQs""")
            return

        embed = discord.Embed(
            title = f'{faq["title"]}',
            description = faq["info"],
            colour = discord.Colour.blue()
        )

        await channel.send(embed=embed)










if not os.path.exists( os.path.join( os.getcwd(), BOT_DATA.FAQ_DATA_FILENAME ) ):
    print("[DEBUG] making empty faq file, since faq file is missing")
    dumpFaqFile(
        {
            "faq_data": [ ]
        }
    )



faq_data = loadFaqFile()

print("[DEBUG] loaded faq data")
# print(json.dumps(faq_data,indent=2))

client.run( open( os.path.join(os.getcwd(), BOT_DATA.TOKEN_FILENAME) , 'r').readline().strip() )