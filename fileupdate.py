import json, os, datetime, sqlite3
configFileName = 'config/config.json'
logFileName = 'config/log.txt'
databaseFileName = 'config/database.db'

"""
checks if initial json exists
"""
def checkjson() -> bool:
    return os.path.exists(configFileName)


"""
creates json if doesn't exist
"""
def createjson() -> None:
    loaddirectory = input("Directory path of original files? (ie: ~/folder/original/) ").strip()
    loaddirectory = os.path.abspath(os.path.expanduser(loaddirectory)) + "/"
    copydirectory = input("Directory path of copied files? (ie: ~/folder/original/) ").strip()
    copydirectory = os.path.abspath(os.path.expanduser(copydirectory)) + "/"
    config = {
            "originalDirectory" : loaddirectory, 
            "copyDirectory" : copydirectory
        }
    with open(configFileName, 'w') as file:
        json.dump(config, file, indent=2)


"""
returns the location of the two directions
returns (original, copy)
"""
def getdirectories() -> (str, str):
    with open(configFileName, 'r') as file:
        data = json.load(file)
    return (data['originalDirectory'], data['copyDirectory'])


"""
creates the log file if log file doesn't exist
"""
def createlog() -> None:
    if not (os.path.exists(logFileName)):
        with (open(logFileName, 'w')) as file:
            file.write("Program Log: \n")


"""
writes to the log file with the specified messaage
"""
def writelog(message : str) -> None:
    if not os.path.exists(logFileName):
        createlog()
    with open(logFileName, 'a') as file:
        errorTime = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
        file.write(f"{errorTime}: {message}\n")


"""
creates the database, if it doesn't already exist
returns true if created, else false
"""
def initdb() -> bool: 
    if (os.path.exists(databaseFileName)): 
        return False
    else:
        connection = sqlite3.connect(databaseFileName)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_first_seen TIMESTAMP,
                filename TEXT,
                uploaded_status TEXT,
                date_uploaded TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        ''')
        connection.commit()
        connection.close()
        return True


"""
adds an given file input to database upon IN_MOVE_TO
"""
def addoncreate(filename: str, dateSeen: str) -> bool:
        connection = sqlite3.connect(databaseFileName)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO file_info (date_first_seen, filename, uploaded_status, date_uploaded, is_deleted)
            VALUES (?, ?, ?, ?, ?)
        ''', (dateSeen, filename, False, None, None))
        connection.commit()
        connection.close()