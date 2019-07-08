import discord
import matplotlib.pyplot as plt
import csv
import datetime

async def joinChartGenerator(ctx):
    totalUsers = 0
    dates = []
    #df = pd.DataFrame(columns=['number', 'joindate'])
    print("Gathering Users")
    allUsers = ctx.guild.members
    for i in allUsers:
        totalUsers += 1
        dates.append(i.joined_at)
        #df[totalUsers] = i.joined_at
        #print(f"User {i.name} joined at {i.joined_at}")
    print(f"Total Users: {str(totalUsers)}")
    dates.sort()
    #print(dates)

    #Plot with matplotlib
    #y axis will be members
    y = range(totalUsers)
    plt.suptitle(ctx.guild.name)
    plt.ylabel("Number of Users")
    plt.xlabel("Join Date")
    plt.plot_date(dates, y)
    ax = plt.axes()
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    plt.savefig("plot.png")

    #Upload to discord
    await ctx.send(file=discord.File('plot.png'))

async def userCSVgenerator(ctx):
    totalUsers = 0
    dates = {}
    #df = pd.DataFrame(columns=['number', 'joindate'])
    print("Gathering Users for CSV")
    allUsers = ctx.guild.members
    for i in allUsers:
        totalUsers += 1
        name = str(i.name) + '#' + str(i.discriminator)
        joindate = i.joined_at
        dates[name] = joindate.strftime("%x %X")

    #print(dates)
    csv_columns = ['user', 'date']
    with open('userJoinTimes.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csv_columns)
        for key, value in dates.items():
            writer.writerow([key, value])

    #Upload to discord
    d = datetime.datetime.today()
    message = str(totalUsers) + " users as of " + str(d)
    await ctx.send(message)
    await ctx.send(file=discord.File('userJoinTimes.csv'))
