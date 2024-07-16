from time import time
import pickle
from typing import Callable, Any
from pathlib import Path


class SyncedFile:
    """
    File synced with GDrive;
    todo: separate from drive as it's really a common thing.
    """

    def __init__(self, domain: str, name: str, request_function: Callable,
                 process_function: Callable = lambda data: data.decode(), filename: str = None,
                 sync_time: int = None, fid: str = None, command_storage: "MessageDataClass" = None,
                 cache_only: bool = False):
        """
        File synced and cached in local storage from GDrive.
        :param domain: App of Toychest, string.
        :param name: Filename within GDrive
        :param request_function: Function to get file data.
        :param process_function: Function to process file data
        :param filename: Local filename to store. None means keep in memory
        :param sync_time: TTL of sync. None means never refresh
        :param command_storage: MessageDataClass(Command) to get commands from
        :param fid: GDrive file ID.
        """
        self.__command_storage = command_storage
        self.domain = domain
        self.name = name
        self.filename = filename
        self.fid = fid
        self.__sync_time = sync_time
        self.__cached = 0
        self.__request = request_function
        self.__process = process_function
        self.__data = None
        if self.filename is not None:
            try:
                with open(self.filename, 'rb') as f:
                    self.__data = pickle.loads(f.read())
            except FileNotFoundError as e:
                if cache_only:
                    raise FileNotFoundError(f'File {filename} was requested with cache-only and not found.')
        if self.__data is None:
            self.sync()

    def sync(self):
        """
        Downloads and reprocesses file data
        :return:
        """
        self.__data = self.__process(self.__request())
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
        if self.filename is not None:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.__data, f)

    @property
    def data(self) -> Any:
        """
        Property to return actual file data.
        :return: Any, depending on the process function.
        """
        if self.__sync_time is not None and self.__cached - time() < -self.__sync_time:
            self.sync()
        elif self.__command_storage is not None:
            if self.__command_storage.receive(self.domain, self.name):
                # expecting this to be sync only.
                self.sync()

        return self.__data
