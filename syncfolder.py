import pyinotify, shutil # pip modules
import fileupdate # own modules

"""
only two event that we need to care about
"""
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print(event) # placeholder

    def process_IN_DELETE(self, event):
        print(event) # placeholder


"""
makes sure that only valid formats are copied
"""
def copyfilewrapper(eventpath: str) -> bool:
    pathending = eventpath[eventpath.rindex("."):]
    # RAW's, jpegs, and videos
    acceptedending = ["dng", "jpg", "jpeg", "mp4"]
    if pathending in acceptedending:
        return copyfile(eventpath)
    else:
        return False


"""
copies the file from one place to another
returns true if copled sucessfully
"""
def copyfile(eventpath: str) -> bool:
    newdirectory = fileupdate.getdirectories()[1]
    try:
        """
        shutil.copy2() instead of copy() because
        copy() will overwrite, which isn't necessary
        """
        shutil.copy2(eventpath, newdirectory)
        return True
    except shutil.SameFileError:
        fileName = eventpath[eventpath.rindex("/")+1:]
        fileupdate.writelog(f"{fileName} already in {newdirectory}")
        return False