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
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import graphing
from email_checker import get_recent_emails
import csv
import os
import json

#Start logging
logging.basicConfig(level=logging.INFO)

#Setup JSON config file
CONFIG_FILE = 'config.json'
CONFIG = {}
if os.path.exists(CONFIG_FILE):
    #load it
    with open(CONFIG_FILE, "r") as config_file:
        CONFIG = json.load(config_file)
else:
    #create file
    config_template = {
        "key": "put private key here",
        "prefix": "!",
        "database": "sqlite:///:memory:",
        "name": "Bot",
        "show_status": False
    }
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config_template, config_file)
    print(f"Please fill out {CONFIG_FILE}")
    exit()


#SQL Database
ENGINE = create_engine(CONFIG['database'], echo=False)
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
    category = Column(String)   #help or fun

#Create the Table
BASE.metadata.create_all(ENGINE)

#Start the SQL session
SESSION = sessionmaker(bind=ENGINE)
COMMANDDB = SESSION()

#Discord client
benchybot = commands.Bot(command_prefix=CONFIG['prefix'])


############
###Checks###
############


# async def role_check(ctx: commands.Context, roles):
#     """Checks if user is in the list of roles"""
#     for role_id in roles:
#         test_role = discord.utils.get(ctx.guild.roles, id=roles[role_id])
#         if test_role in ctx.author.roles:
#             return True
    
#     await ctx.send("You do not have permission to do that")
#     return False

async def role_check(member: discord.Member, ctx, roles):
    """Checks if user is in the list of roles"""
    for role_id in roles:
        test_role = discord.utils.get(ctx.guild.roles, id=roles[role_id])
        if test_role in member.roles:
            return True
    
    # await ctx.send("You do not have permission to do that")
    return False

async def is_admin(ctx):
    """
    Checks if user is an admin
    """
    admin_roles = {
        'Admin': 167872106644635648,
        'Moderator': 167872530860867586,
        '3DPrinters Admin': 667109722930806835
    }

    for role_id in admin_roles:
        test_role = discord.utils.get(ctx.guild.roles, id=admin_roles[role_id])
        if test_role in ctx.author.roles:
            return True

    await ctx.send("You do not have permission to do that")
    return False

async def is_regular(ctx):
    """Checks if user has regular role"""
    regular_roles = {
        'Regular Contributer': 260945795744792578,
        '3DPrinters Admin': 667109722930806835
    }
    return await role_check(ctx.author, ctx, regular_roles)

async def is_staff(ctx):
    """Checks if the user is staff"""
    member = discord.Member
    if type(ctx) == commands.Context:
        member = ctx.author
    elif type(ctx) == discord.Member:
        member = ctx
    staff_roles = {
        '3D Printers Admin (Test Server)': 667109722930806835,
        'Temporary Staff': 690993018357940244,
        'Moderator': 167872530860867586,
        'Admin': 167872106644635648
    }
    return await role_check(member, ctx, staff_roles)

# async def is_staff(ctx: commands.Context):
#     await is_staff(ctx.author)

async def in_secret_channel(ctx):
    """Checks if a command was used in a secret channel"""
    secret_channels = {
        'command-sandbox': 339978089411117076,
        'srsbusiness': 525494034203017246,
        'lets-kill-this-bot': 532781500471443477,
        'regular-botcommands': 667463307963138058,
        'benchybot': 602665906388074496
    }
    used_channel = ctx.channel.id
    for channel in secret_channels:
        if secret_channels[channel] == used_channel:
            return True

    #It dont exist
    await ctx.send("sshhhhh this command is restricted to secret channels")
    return False

async def in_botspam(ctx):
    """Checks if a command was done in a botspam channel"""
    botspam = {
        'command-sandbox': 339978089411117076,
        'voice-pastebin': 471446895089156108,
        'regular-botcommands': 667463307963138058,
        'benchybot': 602665906388074496
    }
    used_channel = ctx.channel.id
    for channel in botspam:
        if botspam[channel] == used_channel:
            return True

    await ctx.send("Error: View the command list in a bot command channel like #voice-pastebin")
    return False


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
        """Reads last UID from the file"""
        try:
            with open(self.uid_file, 'r') as f:
                #Finish this, return the value in the file
                new_uid = int(f.read())
                print(new_uid)
                return new_uid
        except:
            self.cog_unload()
            logging.warning("Failed to load file with last UID, stopped loop")
            return None

    @tasks.loop(minutes=10)
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
            email_channel = benchybot.get_channel(609146304307920936)

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

#benchybot.add_cog(EmailChecker(benchybot))

class CommandDB(commands.Cog):
    """
    Handles adding commands to a database
    """

    async def add_command(self, ctx, command, _responce, _category):
        """
        Adds a command to the database
        Assumes user has permission to do it
        """
        new_command = CCCommand(
            name=command.lower(),
            responce=_responce,
            category=_category)
        COMMANDDB.merge(new_command)
        COMMANDDB.commit()
        await ctx.message.add_reaction('👌')
        logging.info(
            "%s added %s with responce %s to %s",
            ctx.author.name,
            new_command.name,
            new_command.responce,
            new_command.category)

    async def delete_command(self, ctx, victim):
        """
        Removed a command from the database
        Assumes the user has permission to do it
        """
        COMMANDDB.delete(victim)
        COMMANDDB.commit()
        await ctx.send(f"Deleted the command for {victim.name}")
        logging.info(
            "%s deleted %s from %s",
            ctx.author.name,
            victim.name,
            victim.category
        )
        return

    @commands.command(name='cc', hidden=True)
    @commands.check(is_admin)
    @commands.check(in_secret_channel)
    async def cc_command(self, ctx, command, *, _responce):
        """
        Modifies the command database

        List commands: !cc
        Modify or create a command: !cc <command_name> <responce>
        Delete a command: !cc <command_name>

        Bot will confirm with :ok_hand:
        """
        #add a command
        if ctx.message.mention_everyone == False:
            CATEGORY = 'fun'
            await self.add_command(ctx, command, _responce, CATEGORY)
            return

        else:
            await ctx.send(f"Please do not use everyone or here, {ctx.author}")


    @cc_command.error
    async def cc_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'command':
                #Output command list
                output = [""]
                i = 0
                for instance in COMMANDDB.query(CCCommand).order_by(CCCommand.name):
                    if (int(len(output[i])/900)) == 1:
                        i = i + 1
                        output.append("")
                    output[i] += f"{instance.name} "

                i = 1
                for message in output:
                    embed = discord.Embed(
                        title=f'CC commands, pg {i}',
                        color=0xbf5700)
                    embed.add_field(
                        name='All CC commands, times out after 2 minutes',
                        value = message,
                        inline=False)
                    i += 1
                    await ctx.send(embed=embed, delete_after=120)

            elif error.param.name == '_responce':
                #delete a command
                victim = COMMANDDB.query(CCCommand).filter_by(name=ctx.args[2]).one()
                await self.delete_command(ctx, victim)


    @commands.command(name='hc')
    async def hc(self, ctx, command, *, _responce):
        """
        Shows troubleshooting command list
        Usage: !hc

        Admins and Regulars can add to the database
        Modify or create a command: !hc <command_name> <responce>
        Delete a command: !hc <command_name>

        Bot will confirm with :ok_hand:
        
        """
        if await is_regular(ctx) == True and await in_secret_channel(ctx) == True:
            if ctx.message.mention_everyone == False:
                CATEGORY = 'help'
                await self.add_command(ctx, command, _responce, CATEGORY)
                return

            else:
                await ctx.send(f"Please do not use everyone or here, {ctx.author}")


    @hc.error
    async def hc_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'command':
                #print(in_botspam(ctx))
                if await in_botspam(ctx) == True:
                    #Output the command list
                    output = [""]
                    i = 0
                    for instance in COMMANDDB.query(CCCommand).order_by(CCCommand.name):
                        if instance.category == 'help':
                            if (int(len(output[i])/900)) == 1:
                                i = i + 1
                                output.append("")
                            output[i] += f"{instance.name} "
                    i = 1
                    for message in output:
                        #print(f"Messages: {message}")
                        embed = discord.Embed(
                            title=f'Help commands, pg {i}',
                            color=0xbf5700)
                        embed.add_field(
                            name='All help commands, times out after 2 minutes',
                            value=message,
                            inline=False)
                        i += 1
                        await ctx.send(embed=embed, delete_after=120)

                    return

                else: 
                    return

            #Responce be missing so yeet it
            elif error.param.name == '_responce':
                #Make sure they be allowed
                if await is_regular(ctx) == True and await in_secret_channel(ctx) == True:
                    victim = COMMANDDB.query(CCCommand).filter_by(name=ctx.args[2]).one()
                    if victim.category == 'help':
                        await self.delete_command(ctx, victim)
                    else:
                        await ctx.send("hc can only delete help commands")

        else:
            await ctx.send("There was an error, details in log (in function hc_error)")
            print(f"Error be different:{error}")
            


    @commands.command(name='cc-csv', hidden=True)
    @commands.check(is_admin)
    @commands.check(in_secret_channel)
    async def cc_csv(self, ctx):
        """
        Generates a csv of the command database and posts it
        """
        with open('cc.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for instance in COMMANDDB.query(CCCommand).order_by(CCCommand.name):
                csv_writer.writerow([instance.category, instance.name, instance.responce])

        await ctx.send(file=discord.File('cc.csv'))
        os.remove('cc.csv')

    @commands.command(name='import-csv', hidden=True)
    @commands.check(is_admin)
    @commands.check(in_secret_channel)
    async def import_csv(self, ctx, filename):
        """
        ONLY RUN THIS IF YOU KNOW WHAT YOU ARE DOING
        SO PROBABLY DON'T USE THIS COMMAND!!!!!!!!!!

        Imports a csv file full of commands

        Usage: !import-csv filename.csv
        Note: File path is relative to server instance

        File Format:
        [category], [name], [responce]
        """
        try:
            with open(filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                commands_added = 0
                for row in reader:
                    new_cc = CCCommand(
                        category=row[0],
                        name=row[1],
                        responce=row[2])
                    COMMANDDB.merge(new_cc)
                    commands_added += 1

                COMMANDDB.commit()
                await ctx.send(f'Added {commands_added} commands to database')

        #except FileNotFoundError:
        #    await ctx.send("Error, file not found");
        except Exception as oof:
            await ctx.send("Something went wrong with import, check log for details")
            logging.info(oof)
            

benchybot.add_cog(CommandDB(benchybot))

class CoronaChannel(commands.Cog):
    """
    Handles the Covid-19 Channel role
    """
    # - Also just !removeCovid19 to remove it from themselves without adding to database
    # - Add an admin command that removes that entry from that database if needed

    def __init__(self, bot):
        self.covidRoleID = 691050284771835924
        self.bot = bot
        self.CoronaDB.metadata.create_all(ENGINE)
    
    # database class
    class CoronaDB(BASE):
        __tablename__ = "CoronaDB"
        userID = Column(Integer, primary_key=True)

    @commands.command()
    async def addCovid19(self, ctx):
        user = ctx.author
        if self.can_add_role(user):
            await user.add_roles(ctx.guild.get_role(self.covidRoleID))
            await ctx.message.add_reaction('👌')
        else:
            await ctx.send("You do not have permission to add that role")

    @commands.command()
    @commands.check(is_staff)
    async def removeCovid19(self, ctx, *, user_mentions):
        for member in ctx.message.mentions:
            # make sure they aren't staff
            # add the member to the database
            # remove the role

            if await is_staff(member):
                await ctx.send(f"Error: Cannot remove role from staff member, {member}")
            
            else:
                await self.add_to_banned(ctx, member)

                await member.remove_roles(ctx.guild.get_role(self.covidRoleID))

                await ctx.send(f"👌 Removed access to Corona Virus Channels from {member}")
                logging.info(
                    "%s removed %s from corona channels",
                    ctx.author.name,
                    member.name
                )
        

    @removeCovid19.error
    async def removeCovid19_error(self, ctx, error):
        # No argument, so remove it from the user
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.remove_roles(ctx.guild.get_role(self.covidRoleID))
            await ctx.message.add_reaction('👌')

    def can_add_role(self, user):
        """
        Checks if the user can add the corona role to themselves
        """
        for instance in COMMANDDB.query(self.CoronaDB).order_by(self.CoronaDB.userID):
            if instance.userID == user.id:
                return False
        return True

    async def add_to_banned(self, ctx, member):
        new_member = self.CoronaDB(userID = member.id)
        COMMANDDB.merge(new_member)
        COMMANDDB.commit()



benchybot.add_cog(CoronaChannel(benchybot))

@benchybot.event
async def on_ready():
    """
    Runs when bot connects
    """
    print('We have logged in as {0.user}'.format(benchybot))
    #Set activity
    if CONFIG['show_status'] == True:
        await benchybot.change_presence(activity=discord.Game(CONFIG['name']))


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

#Disable command
@commands.check(False)
@benchybot.command(name='checkemails', hidden=True)
@commands.check(is_admin)
async def checkemails(ctx, last_uid):
    """
    Checks for new emails and outputs any to #email-feed
    Currently disabled
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


# with open('key.txt', 'r') as keyFile:
#     KEY = keyFile.read()
benchybot.run(CONFIG['key'].strip())
