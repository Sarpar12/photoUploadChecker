import pyinotify, shutil # pip modules
import fileupdate # own modules


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print(event)


def copyFile(eventPath: str) -> bool:
    newDirectory = fileupdate.getdirectories()[1]
    try:
        """
        shutil.copy2() instead of copy() because
        copy() will overwrite, which isn't necessary
        """
        shutil.copy2(eventPath, newDirectory)
        return True
    except shutil.SameFileError:
        fileName = eventPath[eventPath.rindex("/")+1:]
        folderName = newDirectory[newDirectory.rindex]
        fileupdate.writelog(f"{fileName} already in {newDirectory}")
        return False