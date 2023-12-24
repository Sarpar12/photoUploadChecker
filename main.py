"""
main file that runs everything
"""
import threading
import time
from src import syncfolder

def main() -> None:
    """
    the main wrapper for the entire program
    starts the file monitoring thread, and the uploading thread as well

    Returns: None
    """
    # Creates database, config, and log files
    syncfolder.init_files()

    # Create a thread for syncfolder.main
    sync_thread = threading.Thread(target=syncfolder.main)

    try:
        # Start the sync folder thread
        sync_thread.start()

        # Placeholder Loop
        while True:
            time.sleep(1000)

    except KeyboardInterrupt:
        # Handle keyboard interruption (Ctrl+C)
        print("Database monitoring stopped")
        print("File monitoring stopped.")
    finally:
        # Wait for the sync folder thread to finish
        sync_thread.join()

if __name__ == "__main__":
    main()
