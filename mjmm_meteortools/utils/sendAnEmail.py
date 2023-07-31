# Copyright (C) 2018-2023 Mark McIntyre
import os
import platform
import base64
import email
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES =['https://mail.google.com/']


def _getGmailCreds(tokfile=None, crdfile=None):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if tokfile is None:
        tokfile = '~/.ssh/gmailtoken.json'
    if crdfile is None:
        crdfile = '~/.ssh/gmailcreds.json'
    tokfile = os.path.expanduser(tokfile)
    crdfile = os.path.expanduser(crdfile)
    if os.path.exists(tokfile):
        creds = Credentials.from_authorized_user_file(tokfile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.isfile(crdfile):
                print(f'to use this function you must have stored your Google OAUTH2 secret json file in {crdfile}')
                print('To set up OAUTH2 go to your google cloud console, select APIs then Credentials, and add an OAUTH2 desktop client ID.')
                return None
            flow = InstalledAppFlow.from_client_secrets_file(crdfile, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokfile, 'w') as token:
            token.write(creds.to_json())
    return creds


def _refreshCreds(tokfile=None, crdfile=None):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if tokfile is None:
        tokfile = '~/.ssh/gmailtoken.json'
    if crdfile is None:
        crdfile = '~/.ssh/gmailcreds.json'
    tokfile = os.path.expanduser(tokfile)
    crdfile = os.path.expanduser(crdfile)
    if os.path.exists(tokfile):
        creds = Credentials.from_authorized_user_file(tokfile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try: 
                creds.refresh(Request())
            except: 
                flow = InstalledAppFlow.from_client_secrets_file(crdfile, SCOPES)
                creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        if creds.valid:
            with open(tokfile, 'w') as token:
                token.write(creds.to_json())
        else:
            print('credentials not valid, try again')
    return creds


def _create_message(sender, to, subject, message_text):
    msg = MIMEText(message_text)
    msg['to'] = to
    msg['from'] = sender
    msg['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('utf-8')).decode('utf-8')}



def sendAnEmail(mailrecip, message, msgtype, mailfrom, files=None, tokfile=None, crdfile=None):
    """ sends an email using gmail. 
    
        Arguments:  
            mailrecip:  [string] email address of recipient.  
            message:    [string] the message to send.  
            msgtype:    [string] Prefix for the subject line, eg Test, Warning.  
            mailfrom:   [string] email address of sender.   
            files:      [list]   list of files to attach, not currently implemented.  

        Returns:  
            Nothing, though a message is printed onscreen.  

        Notes:  
            You must have gmail OAUTH2 set up. The gmail credentials default to gmailtoken.json and
            gmailcreds.json in the  $HOME/.ssh folder.  
        """
    
    if msgtype is None:
        msgtype = platform.uname()[1]

    # email a summary to the mailrecip
    creds = _getGmailCreds(tokfile, crdfile)
    if not creds:
        return 
    service = build('gmail', 'v1', credentials=creds)

    subj ='{:s}: {:s}'.format(msgtype, message[:30])
    message = '{:s}: {:s}'.format(msgtype, message)

    mailmsg = _create_message(mailfrom, mailrecip, subj, message)

    try:
        retval = (service.users().messages().send(userId='me', body=mailmsg).execute())
        print('Message Id: %s' % retval['id'])
    except:
        print('An error occurred sending the message')


def forwardAnEmail(reciplist, msgid=None, tokfile=None, crdfile=None):
    """ Forward email from a gmail account to a list of recipients  
    
        Arguments:  
            recplist:   [list of strings] list of addresses to forward to  

        Keyword arguments:  
            msgid:      [string] gmail message id. If None, then all unread mail is forwarded  
            tokfile:    [string] full path to a gmail oauth2 json token file  
            crdfile:    [string] full path to a gmail oauth2 json credentials file for initial authorization 

        To obtain the oauth2 credentials file, go to the google cloud console, select APIs and enable gmail. Then 
         go to Credentials and create an OAUTH2 Client ID for Desktop and download the JSON credentials file. 
         Upon first run, you'll be taken to the gmail authorisation screen and the token file will be created. 
         Subsequent runs will use the token file. The creds file will be used to reauthorise periodically. 
       """
    creds = _getGmailCreds(tokfile, crdfile)
    if not creds:
        return 
    service = build('gmail', 'v1', credentials=creds)
    userid = 'me'
    if msgid is None:
        try:
            msglist = (service.users().messages().list(userId=userid, labelIds=['INBOX','UNREAD']).execute())
            for msg in msglist['messages']:
                msgid = msg['id']
                # retrieve raw mail
                message = (service.users().messages().get(userId='me', id=msgid, format='raw').execute())
                # decode it from base64
                decmsg = base64.urlsafe_b64decode(message['raw'])
                newmsg = email.message_from_bytes(decmsg)
                newmsg.add_header('Reply-To',newmsg['from']) 
                newmsg.replace_header('Subject','Fwd: ' + newmsg['subject'])
                # Send it
                for recip in reciplist:
                    newmsg.replace_header('To', recip)
                    mailmsg = {'raw': base64.urlsafe_b64encode(newmsg.as_string().encode('utf-8')).decode('utf-8')}
                    retval = (service.users().messages().send(userId='me', body=mailmsg).execute())
                    # This will mark the messagea as read
                    service.users().messages().modify(userId=userid, id=msgid, body={'removeLabelIds': ['UNREAD']}).execute() 
                    print(retval)
        except Exception:
            print('Nothing to forward')
    else:
        try:
            message = (service.users().messages().get(userId='me', id=msgid, format='raw').execute())
            # decode it from base64
            decmsg = base64.urlsafe_b64decode(message['raw'])
            newmsg = email.message_from_bytes(decmsg)
            newmsg.add_header('Reply-To',newmsg['from']) 
            newmsg.replace_header('Subject','Fwd: ' + newmsg['subject'])
            # Send it
            for recip in reciplist:
                newmsg.replace_header('To', recip)
                mailmsg = {'raw': base64.urlsafe_b64encode(newmsg.as_string().encode('utf-8')).decode('utf-8')}
                retval = (service.users().messages().send(userId='me', body=mailmsg).execute())
                # This will mark the messagea as read
                service.users().messages().modify(userId=userid, id=msgid, body={'removeLabelIds': ['UNREAD']}).execute() 
                print(retval)
        except Exception:
            print('Nothing to forward')
    return 
