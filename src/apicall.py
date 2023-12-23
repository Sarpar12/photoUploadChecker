"""
IMPORTANT REMINDER TO ME: 
    THIS PROGRAM IS MEANT TO RUN ON A MACHINE WITHOUT GENERAL ACCESS
    **DO NOT** RUN IF A LOT OF PEOPLE CAN ACCESS THE SECRET KEY ON THE DEVICE
    POSSIBLY COULD LEAD TO TO STEALING OF CLIENT ID/SECRET
"""
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import google.oauth2.credentials
from src import fileupdate

SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.readonly', 
          'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata'
          ]
SECRETS_LOCATION = fileupdate.get_secrets()
API_SERVICE_NAME = 'photoslibrary'
API_VERSION = 'v1'

def get_credentials():
    """
    if credentials don't already exist, get credentials

    Returns: Credentials
    """
    flow = InstalledAppFlow.from_client_secrets_file(SECRETS_LOCATION, SCOPES)
    credentials = flow.run_local_server(host='localhost',
        port=8080,
        authorization_prompt_message='Please visit this URL: {url}',
        success_message='The auth flow is complete; you may close this window.',
        open_browser=True)
    return credentials


def get_service(credentials):
    """
    builds the service and returns it

    Params: Credentials from get_credentials()

    Returns: service
    """
    # static_discovery must be set to false, otherwise program won't work
    # credit to https://stackoverflow.com/a/67094010
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials, static_discovery=False)


def list_albums(service):
    """
    gets the reponse
    """
    response = service.albums().list().execute()
    return response
