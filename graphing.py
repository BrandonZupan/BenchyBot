"""
Brandon Zupan

Gathers various types of data on the server
"""

import csv
from datetime import datetime
import discord
import matplotlib.pyplot as plt

async def join_chart_generator(ctx):
    """
    Generates a chart of when everyone joined
    """
    total_users = 0
    dates = []
    #df = pd.DataFrame(columns=['number', 'joindate'])
    print("Gathering Users")
    all_users = ctx.guild.members
    for i in all_users:
        total_users += 1
        dates.append(i.joined_at)
        #df[totalUsers] = i.joined_at
        #print(f"User {i.name} joined at {i.joined_at}")
    print(f"Total Users: {str(total_users)}")
    dates.sort()
    #print(dates)

    #Plot with matplotlib
    #y axis will be members
    y = range(total_users)
    plt.suptitle(ctx.guild.name)
    plt.ylabel("Number of Users")
    plt.xlabel("Join Date")
    plt.plot_date(dates, y)
    ax = plt.axes()
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    plt.savefig("plot.png")

    #Upload to discord
    await ctx.send(file=discord.File('plot.png'))

async def user_csv_generator(ctx):
    """
    Generates a csv of when everyone joined
    """
    total_users = 0
    dates = {}
    #df = pd.DataFrame(columns=['number', 'joindate'])
    print("Gathering Users for CSV")
    all_users = ctx.guild.members
    for i in all_users:
        total_users += 1
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
    d = datetime.today()
    message = str(total_users) + " users as of " + str(d)
    await ctx.send(message)
    await ctx.send(file=discord.File('userJoinTimes.csv'))

async def printer_graph_generator(ctx):
    """
    Generates a graph of users in each role, while ignoring some
    Uploads graph to channel
    """
    #Get a dictionary with each role and the amount of members
    all_roles = {}
    ignored_roles = []

    with open('ignored_roles.txt', 'r') as role_file:
        #Create a list of illegal roles
        for line in role_file:
            ignored_roles.append(line[:-1])

    #print(ignored_roles)

    for role in ctx.guild.roles:
        #Ignore these roles
        if role.name not in ignored_roles:
            member_amount = len(role.members)
            if member_amount >= 5:
                all_roles[role.name] = len(role.members)

    #print(all_roles)

    #Generate a bar graph with the data
    printer_amounts = sorted(all_roles.values())
    printer_amounts.reverse()
    printer_names = sorted(all_roles, key=all_roles.get)
    printer_names.reverse()
    #print(printer_amounts)
    #print(printer_names)

    y_pos = range(len(printer_names))

    plt.bar(y_pos, printer_amounts, align='center', color='orange')
    plt.xticks(y_pos, printer_names, rotation=90)
    plt.ylabel('Number of Users')
    plt.title(f"Printer Usage as of {datetime.today()}")
    plt.tight_layout()
    plt.grid(axis='y')

    #???
    file_name = "printer_plot.png"
    plt.savefig(file_name)

    #Profit
    await ctx.send(file=discord.File(file_name))
