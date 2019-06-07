import discord

#Load the commands from the file images.txt

client = discord.client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    #Check if they're talking to bot
    if message.content.startswith('!'):
        #Break up the message text into an array of lowercase letters
        command = message.content.lower()
        command = command.split()
        print(command)

        #Hello: Replies hello
        if command[0] == "$hello":
            name = "  "
            name = message.author
            name = str(name)
            #print(name)
            #name = name.split("#")
            await message.channel.send('Hello ' + name.split('#')[0] + '!')



keyFile = open('key.txt', 'r')
key = keyFile.read()
client.run(key)