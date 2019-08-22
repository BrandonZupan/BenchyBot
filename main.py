"""
Brandon Zupan

Runs the main code for the 3D Printing Discord's Benchy Bot
"""

import logging
import asyncio
#import concurrent.futures
from functools import partial
import discord
from discord.ext import tasks, commands
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import graphing
from email_checker import discord_idle, get_recent_emails, test_function

#Start logging
logging.basicConfig(level=logging.INFO)

#SQL Database
ENGINE = create_engine('sqlite:///responces.db', echo=False)
BASE = declarative_base()

class CCCommand(BASE):
    """
    Makes object that database undserstands
    """
    __tablename__ = "imageCommands"

    #Has a column for the ID, name, and responce
    #id = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)
    responce = Column(String)

#Create the Table
BASE.metadata.create_all(ENGINE)

#Start the SQL session
SESSION = sessionmaker(bind=ENGINE)
COMMANDDB = SESSION()

#Discord client
benchybot = commands.Bot(command_prefix='!')

class EmailChecker(commands.Cog):
    """Checks email every certain amount of minutes"""
    def __init__(self, bot):
        self.uid_file = 'email_data.txt'
        self.last_uid = self.get_last_uid()
        #self.email_channel = benchybot.get_channel(608703043537600562)
        #self.loop = asyncio.get_running_loop()
        self.bot = bot
        self.email_loop.start()

    def cog_unload(self):
        self.email_loop.cancel()

    def get_last_uid(self):
        with open(self.uid_file, 'r') as f:
            #Finish this, return the value in the file
            new_uid = int(f.read())
            print(new_uid)
            return new_uid

    @tasks.loop(seconds=30)
    async def email_loop(self):
        """
        Checks for new emails and outputs any to #email-feed
        """
        print(self.last_uid)
        loop = asyncio.get_running_loop()

        #Create partial function to pass arguments
        email_function = partial(get_recent_emails, self.last_uid)
        emails = await loop.run_in_executor(None, email_function)

        #Only post if there were emails
        if emails:

            #Get channel
            email_channel = benchybot.get_channel(608703043537600562)

            for email in emails:
                #print(email)
                embed = discord.Embed(title=email.sender[1], color=0xbf5700)
                embed.add_field(name=email.subject, value=email.body, inline=True)
                embed.set_footer(text=f"UID: {email.uid}")
                await email_channel.send(embed=embed)

                logging.info("Sent Email UID %s to email channel", str(email.uid))

                #Save uid so it isn't posted twice
                self.last_uid = email.uid
                with open(self.uid_file, 'w') as f:
                    f.write(str(self.last_uid))
        #else:
        #    print("No new emails")

    @email_loop.before_loop
    async def before_printer(self):
        print('email checker is waiting...')
        await self.bot.wait_until_ready()

class MyCog(commands.Cog):
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        print(self.index)
        self.index += 1

benchybot.add_cog(EmailChecker(benchybot))

@benchybot.event
async def on_ready():
    """
    Runs when bot connects
    """
    print('We have logged in as {0.user}'.format(benchybot))

    

async def is_admin(ctx):
    """
    Checks if user is an admon
    """
    return ctx.message.author.guild_permissions.administrator

async def in_secret_channel(ctx):
    """Checks if a command was used in a secret channel"""
    secret_channels = {
        'command-sandbox': 339978089411117076,
        'srsbusiness': 525494034203017246,
        'lets-kill-this-bot': 532781500471443477
    }
    used_channel = ctx.channel.id
    for channel in secret_channels:
        if secret_channels[channel] == used_channel:
            return True

    #It dont exist
    return False

##############
###Commands###
##############

@benchybot.command(name='hello')
async def hello(ctx):
    """
    Says hello to the user
    """
    await ctx.send("Hello " + str(ctx.author).split('#')[0] + '!')


@benchybot.command(name='usergraph', hidden=True)
@commands.check(is_admin)
async def user_graph(ctx):
    """
    Generates a graph of when users joined
    """
    await graphing.join_chart_generator(ctx)

@benchybot.command(name='userlist', hidden=True)
@commands.check(is_admin)
@commands.check(in_secret_channel)
async def user_list(ctx):
    """
    Generates a CSV of when all members joined
    """
    await graphing.user_csv_generator(ctx)

@benchybot.command(name='printergraph', hidden=True)
@commands.check(is_admin)
async def printergraph(ctx):
    """
    Generates a graph of all printers
    Restricted to admin perms
    """
    await graphing.printer_graph_generator(ctx)

@benchybot.command(name='cc', hidden=True)
@commands.check(is_admin)
@commands.check(in_secret_channel)
async def cc_command(ctx, *args):
    """
    Modifies the command database

    List commands: !cc
    Modify or create a command: !cc <command_name> <responce>
    Delete a command: !cc <command_name>

    Bot will confirm with :ok_hand:
    """
    #If zero arguments, list all commands
    if not args:
        command_list = str()
        for instance in COMMANDDB.query(CCCommand).order_by(CCCommand.name):
            command_list += instance.name + ' '
        embed = discord.Embed(
            title="Command: !cc",
            description=command_list,
            color=0xBF5700)
        await ctx.send(embed=embed)

    #If one argument, delete that command
    if len(args) == 1:
        #print(args[0])
        victim = COMMANDDB.query(CCCommand).filter_by(name=args[0]).one()
        #print(victim.responce)
        COMMANDDB.delete(victim)
        COMMANDDB.commit()
        await ctx.message.add_reaction('👌')
        logging.info(ctx.author.name + " deleted " + victim.name)

    #If 2 or more arguments, combine them and modify database
    if len(args) >= 2:
        #newCC = CCCommand(args[0], ' '.join(args[1:]))
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        new_cc = CCCommand(name=args[0].lower(), responce=' '.join(args[1:]))
        COMMANDDB.merge(new_cc)
        COMMANDDB.commit()
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        await ctx.message.add_reaction('👌')
        logging.info("%s added %s with responce %s", ctx.author.name, new_cc.name, new_cc.responce)

@benchybot.command(name='listcommands', hidden=True)
@commands.check(is_admin)
@commands.check(in_secret_channel)
async def list_commands(ctx):
    """
    Lists all commands in the database
    """
    command_list = str()
    for instance in COMMANDDB.query(CCCommand).order_by(CCCommand.name):
        command_list += instance.name + ' '
    embed = discord.Embed(
        title="Command: !cc",
        description=command_list,
        color=0xBF5700)
    await ctx.send(embed=embed)

@benchybot.command(name='startidle', hidden=True)
@commands.check(is_admin)
async def startidle(ctx):
    """
    Starts idle mode on the email client
    """
    global idle
    await ctx.send("Starting IDLE mode, exit on console with ^C")
    loop = asyncio.get_running_loop()
    idle = loop.run_in_executor(None, discord_idle)
    #print(idle)

@benchybot.command(name='stopidle', hidden=True)
@commands.check(is_admin)
async def stopidle(ctx):
    """
    Stops idle mode on the email client, or at least should lmao
    """
    global idle
    await ctx.send("Stopping idle")
    idle.cancel()

@benchybot.command(name='checkemails', hidden=True)
@commands.check(is_admin)
async def checkemails(ctx, last_uid):
    """
    Checks for new emails and outputs any to #email-feed
    """
    loop = asyncio.get_running_loop()

    #Create partial function to pass arguments
    email_function = partial(get_recent_emails, int(last_uid))
    emails = await loop.run_in_executor(None, email_function)

    #Only post if there were emails
    if emails:
        for email in emails:
            #print(email)
            embed = discord.Embed(title=email.sender[1], color=0xbf5700)
            embed.add_field(name=email.subject, value=email.body, inline=True)
            embed.set_footer(text=f"UID: {email.uid}")
            await ctx.send(embed=embed)
    else:
        await ctx.send("No new emails")

@benchybot.command(name='threadtest', hidden=True)
@commands.check(is_admin)
async def threadtest(ctx):
    i = 2
    while True:
        print(f"Loop {str(i)}")
        loop = asyncio.get_running_loop()
        test = await loop.run_in_executor(None, test_function)
        await asyncio.sleep(1)
        i += 1

@benchybot.event
async def on_command_error(ctx, error):
    """
    Parses command database since library sees them as an error
    """
    if isinstance(error, commands.errors.CommandNotFound):
        #await ctx.send(ctx.message.content)
        command = ctx.message.content.lower()
        command = command.split(" ", 1)

        #Look if its in the database
        for instance in COMMANDDB.query(CCCommand).order_by(CCCommand.name):
            if instance.name == command[0][1:]:
                await ctx.send(instance.responce)
                return
    else:
        print(error)


with open('key.txt', 'r') as keyFile:
    KEY = keyFile.read()
benchybot.run(KEY)
