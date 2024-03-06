"""
contains all the methods that require the use of an API 
or anything related to google's OAuth2.0

IMPORTANT REMINDER TO ME: 
    THIS PROGRAM IS MEANT TO RUN ON A MACHINE WITHOUT GENERAL ACCESS
    **DO NOT** RUN IF A LOT OF PEOPLE CAN ACCESS THE SECRET KEY ON THE DEVICE
    POSSIBLY COULD LEAD TO TO STEALING OF CLIENT ID/SECRET
"""
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
# Used in the code snippet from the below uri, disabled because it was wonky without it
# https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html
# pylint: disable=unused-import
import requests
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


def list_albums(service) -> dict:
    """
    gets the the albums

    Params:
    service: the service used to get the response

    Returns:
    dict: dictionary of albums
    """
    response = service.albums().list().execute()
    return response


def check_photo(service, media_name_jpg: str, max_pages: int) -> bool:
    """
    gets the photos

    Params:
    media_name_jpg: str -> the name(Title) of the photo to search for 
    media_name_raw: same as above, but for the raws instead
    max_pages: the amount of pages that should be looked through as a failsafe

    Returns:
    bool: uploaded
    """
    uploaded = False
    page_size = 10 # the amount of photos to be returned at once
    response = service.mediaItems().list(pageSize=page_size).execute()

    # Searching for the picture within the max_pages
    current_page = 0
    while current_page <= max_pages:
        if current_page == 0:
            media_items = response.get('mediaItems')
            next_token = response.get('nextPageToken')
        else:
            media_items = service.mediaItems().list(
                pageSize=page_size,
                pageToken=next_token
                ).execute()
        for media_item in media_items:
            print(media_item.get('filename'))
            if not uploaded and media_item.get('filename') == media_name_jpg:
                uploaded = True
                break
            current_page += 1
    return uploaded


def parse_data(name: str) -> (int, int, int):
    """
    takes an input name and parses the date     
    ONLY WORKS FOR DEFAULT PIXEL PHOTO N

    Params:
    name: something like PXL_20231216_213618259.RAW-02.ORIGINAL.dng

    Returns:
    (int, int, int): a tuple of the year, month, and day
    """
    name = name[name.find("_")+1:]
    name = name[:name.find("_")]
    year = int(name[0:4])
    month = name[4:6]
    if month[0] == "0":
        month = month[1]
    month = int(month)
    day = name[6:]
    if day[0] == 0:
        day = day[1]
    day = int(day)
    return (year, month, day)


def check_files(files: [str], ending: [str], service) -> None:
    """
    takes a list of files and returns a list of booleans
    that for each file, return true or false

    Params:
    files: list(str) - list of files to check
    ending: list(str) - list of endings for the files

    Returns:
    list((str, bool): a tuple of the filename and the boolean
                      the boolean is true if the file is uploaded
    """
    list_service_filenames = []
    page_size = 25 # the amount of photos to be returned at once
    max_pages = 2
    response = service.mediaItems().list(pageSize=page_size).execute()
    current_page = 0
    # Loop to list all filesnames within the first x amount of pages
    while current_page <= max_pages:
        if current_page == 0:
            media_items = response.get('mediaItems')
            next_token = response.get('nextPageToken')
        else:
            response = service.mediaItems().list(
                pageSize=page_size,
                pageToken=next_token
                ).execute()
            media_items = response.get('mediaItems')
            next_token = response.get('nextPageToken')
        for media_item in media_items:
            list_service_filenames.append(media_item.get('filename'))
        current_page += 1
    for filename in files:
        filenames = [filename + end for end in ending]
        for new_filename in filenames:
            if new_filename in list_service_filenames:
                print(f"Filename: {new_filename}")
                fileupdate.update_uploaded(filename, ending)


def convert_credential(filename: str) -> Credentials:
    """
    converts the dictionary from fileupdate into the credentials object

    Params:
    filename: str of the filename

    Returns:
    Credentials: a credentials object
    """
    credential = Credentials.from_authorized_user_file(filename)
    return credential


def refresh_token(credential: Credentials) -> Credentials:
    """
    refreshes the token if it detects it's invalid or None

    Params:
    invalid_credential: an instance of the Crendentials that is expired

    Returns:
    Credentials: new, unexpired credentials
    """
    request = google.auth.transport.requests.Request()
    credential.refresh(request)
    return credential


def check() -> None:
    """
    the main loop called every x minutes

    Returns: None
    """
    # Checking if credential already exists
    try:
        credentials = convert_credential(fileupdate.get_credential())
        fileupdate.write_log("READ: Credentials Read!")
    except KeyError:
        credentials = get_credentials()
        fileupdate.write_log("STATUS: OAuth authorized")
        fileupdate.write_credential(credentials)
        fileupdate.write_log("WRITE: Crendentials written")
    # Checking if credentials are valid
    if credentials is None or not credentials.valid:
        credentials = refresh_token(credentials)
        fileupdate.write_credential(credentials)
        fileupdate.write_log("WRITE: Credentials Refreshed!")
    service = get_service(credentials)
    # Actually checking if the files are uploaded
    files_to_check = fileupdate.get_unuploaded()
    check_files(files_to_check[0], files_to_check[1], service)
    fileupdate.delete_uploaded()
    fileupdate.write_log("Check Ran")
