"""
Brandon Zupan

Reads emails and sends them to a specific Discord Channel
"""

import imapclient
import pyzmail

#Create imap object for accessing account
imapObj = imapclient.IMAPClient('imap.gmail.com', ssl=True)

#Get login info from login file
with open('gmailLogin.txt', 'r') as loginFile:
    GMAIL = loginFile.readlines()

#Login
imapObj.login(GMAIL[0], GMAIL[1])

#Get all messages in the inbox
imapObj.select_folder('INBOX', readonly=True)
UIDs = imapObj.search(['ALL'])
print(UIDs)

#Get Raw message data for my test message (UID #6)
rawMessages = imapObj.fetch(UIDs, [b'BODY[]'])
message = pyzmail.PyzMessage.factory(rawMessages[6][b'BODY[]'])

#Print the message data
print(message.get_subject())
print(message.get_addresses('from'))
message_text = message.text_part.get_payload().decode(message.text_part.charset)
print(message_text)
