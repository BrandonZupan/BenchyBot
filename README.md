# BenchyBot
Runs BenchyBot on the 3DPrinters Discord Server.  Handles tasks, such as a command database, email checking, and other various commands.  

Can also very roughly detect 3D Benchys in images (currently disabled)

## Required Packages
- discord.py
- sqlalchemy (and sqlite or another sql server/program)
- matplotlib
- imapclient
- pyzmail

## To run
The initial run generates a json file that must be filled out with the bot's key.  You can also enter the database that will be used, the prefix, and the message shown on the now playing entry (defined with bot name).  