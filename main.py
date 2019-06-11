import discord
import csv
from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#SQL Database
engine = create_engine('sqlite:///responces.db', echo=True)
Base = declarative_base()

class ccCommand(Base):
    __tablename__ = "imageCommands"
    
    #Has a column for the ID, name, and responce
    #id = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)
    responce = Column(String)

#Create the Table   
Base.metadata.create_all(engine)

#Start the SQL session
Session = sessionmaker(bind=engine)
session = Session()

#Discord client
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#Used to check if user is admin
async def is_admin(ctx):
    return ctx.message.author.guild_permissions.administrator

##############
###Commands###
##############

@client.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello " + str(ctx.author).split('#')[0] + '!')

@client.command(name='cc')
@commands.check(is_admin)
async def cc(ctx, *args):
    #If zero arguments, list all commands
    if len(args) == 0:
        commandList = str()
        for instance in session.query(ccCommand).order_by(ccCommand.name):
            commandList += instance.name + ' '
        embed = discord.Embed(
            title = "Command: !cc", 
            description = commandList,
            color = 0xBF5700)
        await ctx.send(embed=embed)

    #If one argument, delete that command
    if len(args) == 1:
        print(args[0])
        victim = session.query(ccCommand).filter_by(name=args[0]).one()
        print(victim.responce)
        session.delete(victim)
        session.commit()
        await ctx.message.add_reaction('👌')

    #If 2 or more arguments, combine them and modify database
    if len(args) >= 2:
        #newCC = ccCommand(args[0], ' '.join(args[1:]))
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        newCC = ccCommand(name=args[0].lower(), responce=' '.join(args[1:]))
        session.merge(newCC)
        session.commit()
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        await ctx.message.add_reaction('👌')

@client.command(name='listcommands')
@commands.check(is_admin)
async def listcommands(ctx):
    commandList = str()
    for instance in session.query(ccCommand).order_by(ccCommand.name):
        commandList += instance.name + ' '
    embed = discord.Embed(
        title = "Command: !cc", 
        description = commandList,
        color = 0xBF5700)
    await ctx.send(embed=embed)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        #await ctx.send(ctx.message.content)
        command = ctx.message.content.lower()
        command = command.split(" ", 1)

        #Look if its in the database
        for instance in session.query(ccCommand).order_by(ccCommand.name):
            if instance.name == command[0][1:]:
                await ctx.send(instance.responce)
                return
    else:
        print(error)
  


with open('key.txt', 'r') as keyFile:
    key = keyFile.read()
client.run(key)