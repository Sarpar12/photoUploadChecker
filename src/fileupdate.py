"""
This module provides all the base file system access functionality
"""
import os
import datetime
import json
import sqlite3

# has originalDirectory, copydirectory
CONFIG_FILE_NAME = 'config/config.json'
LOG_FILE_NAME = 'config/log.txt'
"""
database has atributes
date_first_seen: | time when photo was uploaded to device running this program
filename: name of the photo
uploaded_status: default: 0 | is file uploaded
date_uploaded: default: NULL | time api was checked for the photo
is_deleted: default: 0 | if the photo/video is deleted from primary device
"""
DATABASE_FILE_NAME = 'config/database.db'


def check_json() -> bool:
    """
    checks if initial json exists

    Returns: 
    bool true if path exists exists, false otherwise
    """
    return os.path.exists(CONFIG_FILE_NAME)


def create_json() -> None:
    """
    Creates json if it doesn't exist

    Returns: None
    """
    loaddirectory = input("Directory path of original files? (ie: ~/folder/original/) ").strip()
    loaddirectory = os.path.abspath(os.path.expanduser(loaddirectory)) + "/"
    copydirectory = input("Directory path of copied files? (ie: ~/folder/original/) ").strip()
    copydirectory = os.path.abspath(os.path.expanduser(copydirectory)) + "/"
    secretslocation = input("Path to the secrets file? ").strip()
    secretslocation = os.path.abspath(os.path.expanduser(secretslocation))
    config = {
            "originalDirectory" : loaddirectory, 
            "copyDirectory" : copydirectory,
            "secrets" : secretslocation,
            "credential": ""
        }
    with open(CONFIG_FILE_NAME, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=2)


def change_copy(new_directory: str) -> None:
    """
    Changes the copy directory in the config

    Params:
    new_directory: string - input for new path for the copied images

    Returns: None
    """
    with(open(CONFIG_FILE_NAME, 'r', encoding='utf-8')) as file:
        data = json.load(file)
        data["copyDirectory"] = new_directory
    with(open(CONFIG_FILE_NAME, 'w', encoding='utf-8')) as newfile:
        json.dump(data, newfile, indent=2)


def change_original(new_directory: str) -> None:
    """
    Changes the original directory in the config

    Params:
    new_directory: string - input for new path for the original images

    Returns: None
    """
    with(open(CONFIG_FILE_NAME, 'r', encoding='utf-8')) as file:
        data = json.load(file)
        data["originalDirectory"] = new_directory
        file.close()
    with(open(CONFIG_FILE_NAME, 'w', encoding='utf-8')) as newfile:
        json.dump(data, newfile, indent=2)


def write_credential(credential) -> None:
    """
    writes the credentials into a json file.
    Also updates config.json

    Params:
    credentials: the credentials from flow

    Returns: None
    """
    filename = 'config/credentials.json'
    with open(filename, 'w', encoding='utf-8') as token_file:
        token_file.write(credential.to_json())
    with(open(CONFIG_FILE_NAME, 'r', encoding='utf-8')) as file:
        data = json.load(file)
        data["credential"] = 'config/credentials.json'
    with(open(CONFIG_FILE_NAME, 'w', encoding='utf-8')) as newfile:
        json.dump(data, newfile, indent=2)


def get_credential() -> dict:
    """"
    gets the credentials file
    
    Returns: dictionary version of the json file
    """
    with open(CONFIG_FILE_NAME, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data["credential"]


def get_secrets() -> str:
    """
    gets the location on the secrets file

    Returns:
    str: absolute path of the secrets file
    """
    with open(CONFIG_FILE_NAME, 'r', encoding='utf-8')as file:
        data = json.load(file)
        return data["secrets"]


def parse_secrets() -> dict:
    """
    returns all the values of the secrets key

    Returns:
    dict: {"client_id": xxxx, 
           "auth_uri": xxxx, 
           "token_uri": xxxx, 
           "client_secret": xxxx
           "redirect_uris": xxx}
    """
    with(open(CONFIG_FILE_NAME, 'r', encoding='utf-8')) as file:
        try:
            auth_file_name = json.load(file)['secrets']
            with (open(auth_file_name, 'r', encoding='utf-8')) as auth_file:
                return {
                    "client_id" : auth_file["installed"]["client_id"], 
                    "auth_uri" :  auth_file["installed"]["auth_uri"], 
                    "token_uri" : auth_file['installed']['token_uri'], 
                    "client_secrets" : auth_file['installed']['client_secret'], 
                    "redirect_uris" : auth_file['installed']['redirect_uri']
                }
        except KeyError:
            print("Secrets file not found or created!")
            return None


def get_directories() -> (str, str):
    """
    gets the two working directories

    Returns:
    (str, str): (original, copy)
    """
    with open(CONFIG_FILE_NAME, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return (data['originalDirectory'], data['copyDirectory'])


def create_log() -> None:
    """
    creates the log file if log file doesn't exist

    Returns: None
    """
    if not os.path.exists(LOG_FILE_NAME):
        with (open(LOG_FILE_NAME, 'w', encoding='utf-8')) as file:
            file.write("Program Log: \n")


def write_log(message : str) -> None:
    """
    writes to the log file with the specified messaage

    Params:
    message: str input to write to log

    Returns: None
    """
    if not os.path.exists(LOG_FILE_NAME):
        create_log()
    with open(LOG_FILE_NAME, 'a', encoding='utf-8') as file:
        error_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
        file.write(f"{error_time}: {message}\n")


def init_db() -> bool:
    """
    creates the database, if it doesn't already exists 

    Returns:
    bool: true if created, else false
    """
    if os.path.exists(DATABASE_FILE_NAME):
        return False
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_first_seen TIMESTAMP,
                filename TEXT,
                uploaded_status INTEGER DEFAULT 0,
                date_uploaded TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        ''')
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        cursor.close()
        connection.commit()
        connection.close()
    return True


def add_on_create(filename: str,) -> None:
    """
    adds an given file input to database upon IN_MOVE_TO

    Returns: None
    """
    dateseen = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO file_info (date_first_seen, filename, uploaded_status, date_uploaded, is_deleted)
            VALUES (?, ?, ?, ?, ?)
        ''', (dateseen, filename, 0, None, 0)) # 0 -> false, None = NULL
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        cursor.close()
        connection.commit()
        connection.close()


def update_deleted(filename: str) -> None:
    """
    updates the database upon the deletion of file

    Params:
    filename: the name of the file that was deleted

    Returns: None
    """
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            UPDATE file_info
            SET is_deleted = ?
            WHERE filename = ?
            ''', (1, filename))
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        cursor.close()
        connection.commit()
        connection.close()


def update_uploaded(filename_fragment: str, ending: [str]) -> None:
    """
    updates database when file is uploaded
    assume that the raw's are uploaded if the cover image exists
    
    Params:
    filename_fragment: string - filename cut off after the numbers
    ending: list of strings - a list of possible filename endings

    Returns: None
    """
    try:
        connection = sqlite3.connect(DATABASE_FILE_NAME)
        cursor = connection.cursor()
        timecalled = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
        for end in ending:
            new_filename = filename_fragment + end
            cursor.execute('''
                UPDATE file_info
                SET uploaded_status = ?, date_uploaded = ?
                WHERE filename = ?
            ''', (1, timecalled, new_filename))
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        cursor.close()
        connection.commit()
        connection.close()


def clear_deleted_images() -> None:
    """
    This function will be manually called and clears entries in the database 
    that have the below flags set
    is_deleted = 1 and is_uploaded = 0

    Returns: None
    """
    try:
        connection = sqlite3.connect(DATABASE_FILE_NAME)
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM file_info
            WHERE is_deleted = 1 AND uploaded_status = 0
        ''')
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        cursor.close()
        connection.commit()
        connection.close()


def clear_invalid_entries(id_delete: int) -> None:
    """
    deletes entries specified by the ID

    Params:
    id: int - the id in the database to be deleted

    Returns: None
    """
    try:
        connection = sqlite3.connect(DATABASE_FILE_NAME)
        cursor = connection.cursor()
        cursor.execute('''
             DELETE FROM file_info
             WHERE id = ?
        ''', (id_delete))
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        cursor.close()
        connection.commit()
        connection.close()


def get_not_uploaded() -> [[(str)]]:
    """
    every time that this function is called, it will return a list of items in the
    database with is_uploaded = 0

    Returns:
    [(tuple)]: every file with is_uploaded = 0 as an tuple
    """
    connection = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = connection.cursor()
    filenames = []
    try:
        # Fetch items with uploaded_status = 0
        cursor.execute('''
            SELECT filename FROM file_info
            WHERE uploaded_status = 0
        ''')
        filenames.append(cursor.fetchall())
    except sqlite3.OperationalError:
        write_log("ERROR: Database locked!")
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()
    return filenames


def get_unuploaded() -> ([str], [str]):
    """
    a wrapper function for get_not_uploaded(), 
    which converts the list of list of tuples 
    in get_not_uploaded() into a list(str)

    Returns:
    ([str], [str]): a tuple of a list of filenames - str, str, str, etc
                    and a list of file endings
    """
    # Strips the first list out, leaving a list(tuple)
    # instead of a list(list(tuple))
    filenames = get_not_uploaded()[0]
    file_endings = []
    new_filenames = []
    for filename in filenames:
        new_name = filename[0][0: filename[0].find('-')]
        ending = filename[0][filename[0].find('-'):]
        if not new_name in new_filenames:
            new_filenames.append(new_name)
        if not ending in file_endings:
            file_endings.append(ending)
    return (new_filenames, file_endings)
