from abc import ABCMeta, abstractmethod
from typing import Callable


class AbstractDirectory(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, service, name: str, fid: str, config: "Config",
                 sync_config_field: str = 'default_sync_ttl', cache: "DomainNameValue" = None):
        pass

    @property
    @abstractmethod
    def listdir(self):
        """
        :return: List of files within the folder in GDrive format.
        """
        pass


class AbstractDrive(metaclass=ABCMeta):
    FOLDER_TYPE = None
    FILE_TYPE = None
    GDOC_TYPE = None

    @abstractmethod
    def __init__(self, local_folder, config: "Config", cache: "DomainNameValue", ignore_errors=False):
        """
        :param config: toycommons.storage.config object based on toycommons.model.config data
        """
        pass

    @abstractmethod
    def file_by_id(self, fileid: str) -> bytes:
        """
        Download and return bytes of a file by GDrive ID.
        :param fileid: string
        :return: file data.
        """
        pass

    @abstractmethod
    def get_folder_files(self, folder: str = None) -> dict:
        """
        List folder files. Proxy for Directory.listdir.
        :param folder: Folder to scan. Default is "none" which is main toychest dir.
        :return:
        """
        pass

    @abstractmethod
    def file_id_by_name(self, name: str, folder: str = None) -> str or None:
        """
        Find file id by name
        :param name: Name of file
        :param folder: Folder (None for default) name
        :return: id or None
        """
        pass

    @abstractmethod
    def name_by_file_id(self, fid: str, folder: str = None) -> str or None:
        """
        Get file name by it's ID
        :param fid: ID of a Drive File
        :param folder: Folder (None for default) name.
        :return: str or None if not found
        """
        pass

    @abstractmethod
    def file_by_name(self, name: str, folder: str = None) -> bytes:
        """
        Return file by it's name. Finds ID and proxies file_by_id
        :param name: Filename
        :param folder: Folder (None for default) name
        :return: bytes
        """
        pass

    @abstractmethod
    def add_directory(self, name: str, fid: str = None, parent: str = None,
                      sync_config_field: str = 'default_sync_ttl') -> None:
        """
        Add Directory object to the driveconnect list. Raises FileNotFoundError if no directory exists.
        :param name: Folder name
        :param fid: Optional: folder id. If not given, will be found by listing.
        :param parent: Parent folder ID to listdir non-default when finding id.
        :return: None
        """
        pass

    @abstractmethod
    def get_synced_file(self, domain: str, name: str = None, process_function: Callable = lambda data: data.decode(),
                        fid: str = None, filename: str = None, sync_time: int = None, folder: str = None,
                        use_default_sync_time: bool = False, command_storage: "MessageDataClass" = None,
                        copy_filename: bool = False) -> "SyncedFile":
        """
        Generated a SyncedFile objects via parameters.
        :param command_storage: receiму function from toyinfra.
        :param domain: Domain for the synced file (represents toychest application)
        :param name: Filename within Google Drive
        :param process_function: Function which is called upon bytes data downloaded
        :param fileid: Id of the file as a substitute for Name
        :param filename: Filename for local storage
        :param sync_time: How often to refresh; If None, will never be refreshed.
        :param folder: Folder name to search for the file
        :param use_default_sync_time: Replace sync_time with config.drive_config_sync_ttl
        :param copy_filename: If set to true, filename will be overridden by google drive file name.
        :return: SyncedFile
        """
        pass

    @abstractmethod
    def get_google_doc(self, codename, doc_id, domain: str = None, get_synced: bool = True, sync_time: int = None,
                       filename: str = None, use_default_sync: bool = False, command_storage: "MessageDataClass" = None,
                       cache_images: bool = True, image_folder='', uri_prepend=''):
        pass

    @abstractmethod
    def list_google_docs(self, folder=None):
        pass
