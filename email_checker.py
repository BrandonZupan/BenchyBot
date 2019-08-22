"""
Brandon Zupan

Reads emails and sends them to a specific Discord Channel
"""

#To do:
    #Save the UID of last email that was posted
    #Run every 10 minutes and output to channel

import imapclient
import pyzmail

class EmailData():
    """Stores data of an email to be returned"""

    def __init__(self, message, uid):
        """Gathers data from a message"""
        self.uid = uid
        self.sender = message.get_address('from')
        self.subject = message.get_subject()
        self.body = message.text_part.get_payload().decode(message.text_part.charset)


def gmail_login():
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
    #print(f"Logged into {GMAIL[0]} for accessing stuff")

    #Return imapObj so the account is accessible
    return imapObj

def print_message(imapObj, uid):
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

def run_idle(current_session):
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


def get_recent_emails(last_uid):
    """
    Returns a list of untracked emails
    """
    #Log into email account
    account = gmail_login()

    #Get a list of all emails
    UIDs = account.search(['ALL'])

    #Get last recorded email id
    last_recieved = UIDs[-1]
    if last_uid >= last_recieved:
        #no new emails
        account.logout()
        return 0

    #There are new emails to be posted
    last_index = UIDs.index(last_uid) + 1

    UIDs = UIDs[last_index:]

    message_list = list()
    #Generate list of tuples
    for uid in UIDs:
        #Tuple will be (UID, Sender, Subject, Message)
        raw_messages = account.fetch(uid, [b'BODY[]'])
        message = pyzmail.PyzMessage.factory(raw_messages[uid][b'BODY[]'])
        #message_list.append((uid,
        #    message.get_address('from'),
        #    message.get_subject(),
        #    message.text_part.get_payload().decode(message.text_part.charset)))
        message_list.append(EmailData(message, uid))

    account.logout()
    return message_list
