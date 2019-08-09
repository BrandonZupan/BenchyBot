"""
Brandon Zupan

Reads emails and sends them to a specific Discord Channel
"""

import imapclient

imapObj = imapclient('imap.gmail.com', ssl=True)

with open('gmailLogin.txt', 'r') as loginFile:

    GMAIL = loginFile.readlines()
