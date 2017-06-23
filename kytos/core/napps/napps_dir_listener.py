"""Module to monitor installed napps."""
import logging

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

log = logging.getLogger(__name__)


class NAppDirListener(FileSystemEventHandler):
    """Class to handle directory changes."""

    _controller = None

    def __init__(self, controller):
        """Contructor of class NAppDirListener.

        Args:
            controller(kytos.core.controller): A controller instance.
        """
        self._controller = controller
        self.napps_path = self._controller.options.napps
        self.observer = Observer()

    def start(self):
        """Method to start handle directory changes."""
        self.observer.schedule(self, self.napps_path, True)
        self.observer.start()
        log.info('NAppDirListener Started...')

    def stop(self):
        """Method to stop handle directory changes."""
        self.observer.stop()
        log.info('NAppDirListener Stopped...')

    def _get_napp(self, absolute_path):
        """Method used to get a username and napp_name from absolute path.

        Args:
            absolute_path(str): String with absolute path.

        Returns:
            tuple: Tuple with username and napp_name.
        """
        relative_path = absolute_path.replace(self.napps_path, '')
        log.info(relative_path)
        return tuple(relative_path.split('/')[1:3])

    def on_created(self, event):
        """Load a napp from created directory.

        Args:
            event(watchdog.events.DirCreatedEvent): Event received from an
                observer.
        """
        napp = self._get_napp(event.src_path)
        self._controller.load_napp(*napp)

    def on_deleted(self, event):
        """Unload a napp from deleted directory.

        Args:
            event(watchdog.events.DirDeletedEvent): Event received from an
                observer.
        """
        napp = self._get_napp(event.src_path)
        self._controller.unload_napp(*napp)
