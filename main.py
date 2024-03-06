"""
main file that runs everything
"""
from threading import Thread, Event
import time
from src import syncfolder
from src import apicall

def main() -> None:
    """
    the main wrapper for the entire program
    starts the file monitoring thread, and the uploading thread as well

    Returns: None
    """
    syncfolder.init_files()
    stop_event = Event()
    sync_thread = Thread(target=syncfolder.main, args=(stop_event,))
    try:
        sync_thread.start()
        while True:
            time.sleep(1800)
            apicall.check()
    except KeyboardInterrupt:
        print("Database monitoring stopped")
        stop_event.set()
    finally:
        sync_thread.join()

if __name__ == "__main__":
    main()
