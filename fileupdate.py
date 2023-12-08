import json, os, datetime


configFileName = 'config/config.json'
logFileName = 'config/log.txt'


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
            file.write("Program Log:")


"""
writes to the log file with the specified messaage
"""
def writelog(message : str) -> None:
    if not os.path.exists(logFileName):
        createlog()
    with open(logFileName, 'w') as file:
        errorTime = datetime.now().strftime('%m-%d %H:%M:%S')
        file.write(f"{errorTime}: {message}\n")