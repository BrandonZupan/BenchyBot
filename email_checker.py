"""
Brandon Zupan

Reads emails and sends them to a specific Discord Channel
"""

#To do:
    #Make emails show up on discord when recieved
    #Save which email was previously shown and post any that haven't been posted yet
    #Add ability to reply through discord

import asyncio
import imapclient
import pyzmail

async def gmail_login(account_var):
    """
    Log into gmail with provided key
    Returns object used to access account
    """
    #Create imap object for accessing account
    imapObj = imapclient.IMAPClient('imap.gmail.com', ssl=True)

    #Get login info from login file
    with open('gmailLogin.txt', 'r') as loginFile:
        GMAIL = loginFile.readlines()

    #Login
    imapObj.login(GMAIL[0], GMAIL[1])

    #Select inbox
    imapObj.select_folder('INBOX')
    print(f"Logged into {GMAIL[0]} for accessing stuff")

    #Return imapObj so the account is accessible
    account_var = imapObj

async def print_message(imapObj, uid):
    """
    Reads a hello world message
    """
    #Get all messages in the inbox
    #UIDs = imapObj.search(['ALL'])
    #print(UIDs)

    #Get Raw message data for my test message (UID #6)
    rawMessages = imapObj.fetch(uid, [b'BODY[]'])
    message = pyzmail.PyzMessage.factory(rawMessages[uid][b'BODY[]'])

    #Print the message data
    print(message.get_subject())
    print(message.get_addresses('from'))
    message_text = message.text_part.get_payload().decode(message.text_part.charset)
    print(message_text)

async def run_idle(current_session):
    """
    Constantly checks for emails
    """
    current_session.idle()
    print("Running in IDLE mode, quit with ^c")

    while True:
        try:
            responces = current_session.idle_check(timeout=30)
            #responces = [(10, b'EXISTS')]
            print("Server sent:", responces if responces else "nothing")
            if responces[0][1] == b'FETCH':
                current_session.idle_done()
                print_message(current_session, responces[0][0])
                current_session.idle()

            #break
        except KeyboardInterrupt:
            current_session.idle_done()
            print("\nIDLE mode done")
            current_session.logout()
        except IndexError:
            print("There was an index error.  Ignoring...")

async def main():

    account = imapclient.IMAPClient
    await gmail_login(account)

    await run_idle(account)
    #print_message(account, 6)

if __name__ == "__main__":
    asyncio.run(main())
