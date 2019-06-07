import discord
import csv


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
    #Iterate through each value and write it to dictionary



#Load the commands from the file images.txt
images = dict()
images = loadCommands("images.txt", images)

#Create the client
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    #Use the global variable images
    global images

    if message.author == client.user:
        return
    
    #Check if they're talking to bot
    if message.content.startswith('!'):
        #Break up the message text into an array of lowercase letters
        command = message.content.lower()
        command = command.split(" ", 2)
        print(command)

        #Hello: Replies hello
        if command[0] == "!hello":
            name = "  "
            name = message.author
            name = str(name)
            #print(name)
            #name = name.split("#")
            await message.channel.send('Hello ' + name.split('#')[0] + '!')

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
                    imageCommand = '!' + command[1]
                    #If there is no command[2], then delete.  Else assign the value
                    if len(command) <= 2:
                        #delete
                        del images[imageCommand]
                    else:
                        #Update the value
                        images[imageCommand] = command[2]
                        await message.add_reaction('👌')
                        
            #Look if its in the images file
        elif command[0] in images.keys():
            await message.channel.send(images[command[0]])

        



keyFile = open('key.txt', 'r')
key = keyFile.read()
client.run(key)