import pyinotify, shutil # python modules
import fileupdate # own modules


"""
only two event that we need to care about
"""
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_DELETE(self, event):
        fileupdate.writelog(f"File deleted: {event.pathname}") # placeholder
        fileupdate.updatedatabase(parsefilename(event.pathname), True)
        

    # IN_MOVE_TO is what gets the jpg/dng, not IN_CREATE
    def process_IN_MOVED_TO(self, event):
        fileupdate.writelog(f"File created: {event.pathname}")
        copyfilewrapper(event.pathname)


"""
makes sure that only valid formats are copied
"""
def copyfilewrapper(eventpath: str) -> bool:
    pathending = eventpath[eventpath.rindex(".")+1:]
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
    filename = eventpath[eventpath.rindex("/")+1:]
    try:
        """
        shutil.copy2() instead of copy() because
        copy() will overwrite, which isn't necessary
        """
        shutil.copy2(eventpath, newdirectory)
        fileupdate.writelog(f"File {eventpath} copied to {newdirectory}")
        fileupdate.addoncreate(filename)
        return True
    except shutil.SameFileError:
        fileupdate.writelog(f"File {filename} already in {newdirectory}")
        return False
    

"""
gets the filename from pathname
"""
def parsefilename(pathname: str) -> str:
    return pathname[pathname.rindex("/")+1:]


"""
converts from military time 24:00:00 to civilian time
"""
def converttime(time: str) -> str:
    ending = "AM"
    times = time.split(":")
    if times[0] > 12:
        times[0] = times[0] % 12
        ending = "PM"
    return f"{times[0]}:{times[1]}:{times[2]} {ending}"


"""
creates the config and database on first run
"""
def initfiles() -> None:
    if not (fileupdate.checkjson()):
        fileupdate.createjson()
    fileupdate.initdb()


"""
actual loop that checks for events and copies
"""
def main():
    # Creates database, config, and log files
    initfiles()
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