import pyinotify, shutil # python modules
import fileupdate # own modules


"""
only two event that we need to care about
"""
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_DELETE(self, event):
        print(f"File deleted: {event.pathname}") # placeholder

    # IN_MOVE_TO is what gets the jpg/dng, not IN_CREATE
    def process_IN_MOVED_TO(self, event):
        print(f"File created: {event.pathname}")
        copyfilewrapper(event.pathname)


"""
makes sure that only valid formats are copied
"""
def copyfilewrapper(eventpath: str) -> bool:
    pathending = eventpath[eventpath.rindex(".")+1:]
    print(pathending)
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


"""
creates the config on first run
"""
def loadconfig() -> None:
    if not (fileupdate.checkjson()):
        fileupdate.createjson()


"""
actual loop that checks for events and copies
"""
def main():
    loadconfig()
    # Initialize INotify
    wm = pyinotify.WatchManager()
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)

    # Watch for IN_CREATE and IN_DELETE events
    wdd = wm.add_watch(fileupdate.getdirectories()[0], pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO)

    try:
        # Start monitoring
        notifier.loop()
    except KeyboardInterrupt:
        # Handle keyboard interruption (Ctrl+C)
        print("Monitoring stopped.")
        notifier.stop()

if __name__ == "__main__":
    main()