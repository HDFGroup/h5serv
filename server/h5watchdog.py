import sys
import time
import os.path as op
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class H5EventHandler(FileSystemEventHandler):
    """Put create  events inteo queue."""

    def __init__(self, event_queue):
        self.log = logging.getLogger("h5serv")
        self.event_queue = event_queue
        
    def on_moved(self, event):
        super(H5EventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        self.log.info("H5EventHandler -- Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(H5EventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        self.log.info("H5EventHandler -- Created %s: %s", what, event.src_path)
        
        # ignore directories
        if not op.isdir(event.src_path):
            self.event_queue.put(event.src_path)

    def on_deleted(self, event):
        super(H5EventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        self.log.info("H5EventHandler -- Deleted %s: %s", what, event.src_path)
        if not op.isdir(event.src_path):
            self.event_queue.put(event.src_path)

    def on_modified(self, event):
        super(H5EventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        self.log.info("H5EventHandler -- Modified %s: %s", what, event.src_path)

#
# Watch file system at location data_path and add any file create events to the event_queue
# Call at application startup
#
def h5observe(data_path, event_queue):
    event_handler = H5EventHandler(event_queue)
    observer = Observer()
    observer.schedule(event_handler, data_path, recursive=True)
    observer.start()