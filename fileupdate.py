import json, os

configFileName = 'config.json'
"""
checks if initial json exists
"""
def checkjson() -> bool:
    return os.path.exists(configFileName)


"""
creates json if doesn't exist
"""
def createjson() -> None:
    loaddirectory = input("Directory path of original files? ").strip()
    copydirectory = input("Directory path of copied files? ").strip()
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