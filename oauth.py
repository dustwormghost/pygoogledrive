import httplib2
import json
import os

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets,Credentials

from oauth2client.file import Storage
from oauth2client.tools import  run_flow, argparser

from utils import utils

class OAuthGmailAPI:
    '''Authenticate to google Gmail API'''
    
    # Check https://developers.google.com/gmail/api/auth/scopes
    scopes = { 'READ_ONLY': 'https://www.googleapis.com/auth/gmail.readonly', 
               'MODIFY':    'https://www.googleapis.com/auth/gmail.modify', #All read/write operations except immediate, permanent deletion of threads and messages, bypassing Trash.
               'COMPOSE':   'https://www.googleapis.com/auth/gmail.compose',  #Create, read, update, and delete drafts. Send messages and drafts.
               'INSERT':    'https://www.googleapis.com/auth/gmail.insert',#Insert and import messages only.
               'LABELS':    'https://www.googleapis.com/auth/gmail.labels', #Create, read, update, and delete labels only.
               'FULL':      'https://mail.google.com/' #Full access to the account, permanent deletion of threads and messages
            }
    
    def __init__(self, client_secret_file, oauth_scope_key):
        self.client_secret_file = client_secret_file #get secret file from https://console.developers.google.com/project
        if(not oauth_scope_key in self.scopes):
            self.oauth_scope = self.scopes['READ_ONLY'];
        else:
            self.oauth_scope = self.scopes[oauth_scope_key]
        
        self.set_gmail_service()


    
    def set_gmail_service(self):
        '''OAuth and create gmail service'''
#         parser = argparser.ArgumentParser(parents=[argparser]) # CLI flags if any
#         flags = parser.parse_args()
        flags = argparser.parse_args(args=[])

        storage = Storage('gmail.storage') # location of credentials
        
        # OAuth flow to retrieve credentials
        flow = flow_from_clientsecrets(self.client_secret_file, scope=self.oauth_scope)
        http = httplib2.Http()
        
        # get credentials from storage or run the flow to generate them
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, flags, http=http)
        
        # Authorize the httplib2.Http object with our credentials
        http = credentials.authorize(http)
        
        # build Gmail service from discovery
        self.gmail_service =  build('gmail', 'v1', http=http)
        
    def get_gmail_service(self):
        '''initialize gmail service, otherwise return already initialized one'''
        if not self.gmail_service:
            return self.set_gmail_service()
        
        return self.gmail_service
        
class OAuthDriveAPI:
    '''Authenticate to google Drive API'''
    # Check https://developers.google.com/drive/scopes
    scopes = {'PER_FILE':           'https://www.googleapis.com/auth/drive.file',
              'FULL':               'https://www.googleapis.com/auth/drive',
              'APPS_READ_ONLY':     'https://www.googleapis.com/auth/drive.apps.readonly',
              'READ_ONLY':          'https://www.googleapis.com/auth/drive.readonly',
              'METADATE_READ_ONLY': 'https://www.googleapis.com/auth/drive.readonly.metadata',
              'METADATA_FULL':      'https://www.googleapis.com/auth/drive.metadata',
              'APP_INSTALL':        'https://www.googleapis.com/auth/drive.install',
              'APP_FOLDER':         'https://www.googleapis.com/auth/drive.appfolder',
              'APP_SCRIPT':         'https://www.googleapis.com/auth/drive.scripts'
    }
    
    credentials_file = 'secret/drive_client_credentials.json'
        
    def __init__(self, client_secret_file, oauth_scope_key, re_autheticate=False):
        if(not oauth_scope_key in self.scopes):
            self.oauth_scope = self.scopes['READ_ONLY'];
        else:
            self.oauth_scope = self.scopes[oauth_scope_key]
        
        self.client_secret_file_data = self.get_client_secret_file(client_secret_file)
        
        self.client_id = self.client_secret_file_data['installed']['client_id']
        self.client_secret = self.client_secret_file_data['installed']['client_secret']
        self.redirect_uri = self.client_secret_file_data['installed']['redirect_uris'][0]
        
        #Authenticate
        # check whether or not trying to authenticate again
        if os.path.isfile(self.credentials_file) and not re_autheticate:
            credentials_file_data = self.get_client_credentials()
            credentials = Credentials.new_from_json(credentials_file_data)
        else:
            # client needs to manually get credentials
            flow = OAuth2WebServerFlow(self.client_id, self.client_secret, self.oauth_scope, redirect_uri=self.redirect_uri) 
                                        #access_type='offline')
            authorize_url = flow.step1_get_authorize_url()
            flow.step1_get_authorize_url()
             
            log('Go to the following link in your browser: ' + authorize_url)
            code = raw_input('Enter verification code: ').strip()
            credentials = flow.step2_exchange(code)        
            
            # store credentials for next authorization
            self.set_client_credentials(credentials)
        
        self.set_drive_service(credentials)
            
        
    def set_drive_service(self, credentials):
        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
            
        self.drive_service = build('drive', 'v2', http=http)
    
    def get_drive_service(self):
        '''initialize drive service, otherwise return already initialized one'''
        if not self.drive_service:
            return self.set_drive_service()
        
        return self.drive_service
    
    def get_client_secret_file(self, file):
        with open(file, 'r') as f:
            return json.loads(f.read())  
    
    def set_client_credentials(self, Credentials):
        with open(self.credentials_file, 'w') as f:
            f.write(Credentials.to_json())
    
    def get_client_credentials(self):
        with open(self.credentials_file, 'r') as f:
            return f.read()
    