"""
this module syncs the the original and copy directories,
writes that to log, and adds it to the database
"""
import shutil
import pyinotify
from src import fileupdate


class EventHandler(pyinotify.ProcessEvent):
    """
    catches the only two events we need to care about
    """
    # pylint: disable=invalid-name
    def process_IN_DELETE(self, event) -> None:
        """
        if a file is deleted write to log, and update the database

        Parameters:
        event: the Event that was created 

        Returns: None
        """
        fileupdate.write_log(f"File deleted: {event.pathname}") # placeholder
        fileupdate.update_deleted(parse_file_name(event.pathname))


    # pylint: disable=invalid-name
    def process_IN_MOVED_TO(self, event):
        """
        if a file is created, then write it to log and update database

        Parameters:
        event: the Event that was created 

        Returns: None
        """
        fileupdate.write_log(f"File created: {event.pathname}")
        copy_file_wrapper(event.pathname)


def copy_file_wrapper(eventpath: str) -> bool:
    """
    Wrapper for copy_file(), checks for right file extension

    Parameters:
    eventpath: the path of the file including the filename

    Returns:
    bool: true if file has been copied
    """
    pathending = eventpath[eventpath.rindex(".")+1:]
    # RAW's, jpegs, and videos
    acceptedending = ["dng", "jpg", "jpeg", "mp4"]
    if pathending in acceptedending:
        return copy_file(eventpath)
    return False


def copy_file(eventpath: str) -> bool:
    """
    copies the file given 

    Parameters:
    eventpath: the path of the file including the filename

    Returns:
    bool: true if file has been copied
    """
    newdirectory = fileupdate.get_directories()[1]
    filename = eventpath[eventpath.rindex("/")+1:]
    try:
        # shutil.copy2() instead of copy() because
        # copy() will overwrite, which isn't necessary
        shutil.copy2(eventpath, newdirectory)
        fileupdate.write_log(f"File {eventpath} copied to {newdirectory}")
        fileupdate.add_on_create(filename)
        return True
    except shutil.SameFileError:
        fileupdate.write_log(f"File {filename} already in {newdirectory}")
        return False


def parse_file_name(pathname: str) -> str:
    """
    gets the file name from the path

    Parameters:
    pathname: the path of the file including the name

    Returns:
    str: file name
    """
    return pathname[pathname.rindex("/")+1:]


def convert_time(time: str) -> str:
    """
    converts from military time 24:00:00 to civilian time

    Parameters: 
    time: miliary time(ie: 23:30:29)

    Returns:
    str: converted time(ie: 11:30:29 PM)
    """
    ending = "AM"
    times = time.split(":")
    if times[0] > 12:
        times[0] = times[0] % 12
        ending = "PM"
    return f"{times[0]}:{times[1]}:{times[2]} {ending}"


def init_files() -> None:
    """
    creates the files if they don't exist

    Returns: None
    """
    if not fileupdate.check_json():
        fileupdate.create_json()
    fileupdate.init_db()


def main():
    """
    the main loop that runs forever
    """
    # Creates database, config, and log files
    init_files()
    # Initialize INotify
    watch_manager = pyinotify.WatchManager()
    handler = EventHandler()
    notifier = pyinotify.Notifier(watch_manager, handler)

    # Watch for IN_CREATE and IN_DELETE events
    # Disabling no-member checks because it clearly works so there is a member
    # pylint: disable=no-member
    watch_manager.add_watch(
            fileupdate.get_directories()[0],
            pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO
        )

    try:
        # Start monitoring
        notifier.loop()
    except KeyboardInterrupt:
        # Handle keyboard interruption (Ctrl+C)
        print("Monitoring stopped.")
        notifier.stop()

if __name__ == "__main__":
    main()
