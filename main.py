import discord
import csv
from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def loadCommands(fileName, victim):
    """
    Reloads the commands from a given file
    Input: Name of the file and the dictionary to be reloaded
    Output: The dictionary
    """
    #new dictionary
    newImages = dict()
    #Delete all values in the dictionary
    print("Reloading " + fileName)
    victim.clear()
    #Load the commands from the file images.txt
    with open(fileName) as csvfile:
        reader = csv.reader(csvfile, delimiter='`')
        for row in reader:
            newImages[row[0]] = row[1]
    return newImages

def saveCommands(fileName, victim):
    """
    Writes the dictionary of commands to a file
    Inputs: name of file and dictionary
    Outputs: None
    """
    #Open the file in write mode with ` delimiter
    with open(fileName, 'w') as csvfile:
        writeCommands = csv.writer(csvfile, delimiter='`')
        for command in victim:
            writeCommands.writerow([command, victim[command]])
    #Iterate through each value and write it to dictionary

#SQL Database
engine = create_engine('sqlite:///:memory:', echo=True)
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

#Load the commands from the file images.txt
images = dict()
images = loadCommands("images.txt", images)

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
        await ctx.send(commandList)

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
        newCC = ccCommand(name=args[0], responce=' '.join(args[1:]))
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
    await ctx.send(commandList)

"""
@client.event
async def on_message(message):
    #Use the global variable images
    global images

    if message.author == client.user:
        return
    
    #Check if they're talking to bot
    if message.content.startswith('!'):
        #Break up the message text into an array of lowercase letters
        command = message.content
        command = command.split(" ", 2)
        command[0] = command[0].lower()
        #print(command)

        #Print all the possible image commands
        if command[0] == "!listcommands":
            if message.author.guild_permissions.administrator:
                possiblecommands = ""
                for command in images:
                    possiblecommands += command + ', '
                await message.channel.send(possiblecommands)

        #Adds a new command to the list
        if command[0] == "!cc":
            #Check if admin
                if message.author.guild_permissions.administrator:
                    #If there is one entry, then give info
                    if len(command) == 1:
                        embed = discord.Embed(
                            title = "Command: !cc", 
                            description = "Creates, modifies, or deletes a command",
                            color = 0xBF5700)
                        embed.add_field(
                            name = "!cc <command_name> <link and/or text>", 
                            value = "Creates a new command or updates a command with that name and link/text")
                        embed.add_field(
                            name = "!cc <command_name>",
                            value = "Deletes that command")
                        await message.channel.send(embed=embed)
                        return
                    
                    imageCommand = '!' + command[1]
                    #If there is no command[2], then delete.  Else assign the value
                    if len(command) == 2:
                        #delete
                        del images[imageCommand]
                    else:
                        #Update the value
                        images[imageCommand] = command[2]

                    #Update database
                    saveCommands("images.txt", images)
                    await message.add_reaction('👌')
                        
            #Look if its in the images file
        elif command[0] in images.keys():
            await message.channel.send(images[command[0]])
"""
        


with open('key.txt', 'r') as keyFile:
    key = keyFile.read()
client.run(key)