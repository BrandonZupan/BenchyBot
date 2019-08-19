"""
Brandon Zupan

Runs the main code for the 3D Printing Discord's Benchy Bot
"""

import logging
import discord
from discord.ext import commands
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import graphing
from email_checker import discord_idle

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
CLIENT = commands.Bot(command_prefix='!')

@CLIENT.event
async def on_ready():
    """
    Runs when bot connects
    """
    print('We have logged in as {0.user}'.format(CLIENT))

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

@CLIENT.command(name='hello')
async def hello(ctx):
    """
    Says hello to the user
    """
    await ctx.send("Hello " + str(ctx.author).split('#')[0] + '!')


@CLIENT.command(name='usergraph', hidden=True)
@commands.check(is_admin)
async def user_graph(ctx):
    """
    Generates a graph of when users joined
    """
    await graphing.join_chart_generator(ctx)

@CLIENT.command(name='userlist', hidden=True)
@commands.check(is_admin)
@commands.check(in_secret_channel)
async def user_list(ctx):
    """
    Generates a CSV of when all members joined
    """
    await graphing.user_csv_generator(ctx)

@CLIENT.command(name='printergraph', hidden=True)
@commands.check(is_admin)
async def printergraph(ctx):
    """
    Generates a graph of all printers
    Restricted to admin perms
    """
    await graphing.printer_graph_generator(ctx)

@CLIENT.command(name='cc', hidden=True)
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

@CLIENT.command(name='listcommands', hidden=True)
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

@CLIENT.command(name='startidle', hidden=True)
@commands.check(is_admin)
async def startidle(ctx):
    """
    Starts idle mode on the email client
    """
    await discord_idle()

@CLIENT.event
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
CLIENT.run(KEY)
