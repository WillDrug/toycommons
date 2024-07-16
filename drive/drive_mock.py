from .drive_interface import AbstractDrive, AbstractDirectory
from .google_drive import SyncedFile, GoogleDoc
from typing import Callable
import requests
from time import time
import os
from pathlib import Path
import shutil

class LocalDirectory(AbstractDirectory):
    def __init__(self, service, name: str, fid: str, config: "Config",
                 sync_config_field: str = 'default_sync_ttl', cache: "DomainNameValue" = None):
        self.name = name
        self.fid = fid
        self.__config = config
        self.__sync_field = sync_config_field
        self.__cache_db = cache
        self.__cache_db[f'{self.name}_last_cached'] = 0
        self.__service = service

    @property
    def listdir(self):
        """
        :return: List of files within the folder in GDrive format.
        """
        cached = self.__cache_db[f'{self.name}_last_cached'] or 0
        if time() - cached > self.__config[self.__sync_field]:
            self.__cache_db[f'{self.name}_listdir'] = [{'name': file,
                                                        'id': file,
                                                        'mimeType':
                                                            0 if not Path.is_file(Path(self.__service).joinpath(Path(file)))
                                                            else 2 if file.endswith('.gdoc_local') else 1} for file
                                                       in os.listdir(self.__service)]
            self.__cache_db[f'{self.name}_last_cached'] = time()
        return self.__cache_db[f'{self.name}_listdir']

    @property
    def local_path(self):
        return self.__service

# todo put drive mock on the same interface
class DriveMock(AbstractDrive):
    FOLDER_TYPE = 0
    FILE_TYPE = 1
    GDOC_TYPE = 2

    def __init__(self, local_folder, config: "Config", cache: "DomainNameValue", ignore_errors=False):
        """
        :param config: toycommons.storage.config object based on toycommons.model.config data
        """
        self.config = config
        self.cache = cache
        self.ignore_errors = ignore_errors
        self.local_folder = local_folder

        self.directories = {}
        if self.config.drive_folder_id is not None:
            self.directories[None] = LocalDirectory(self.local_folder, name='', fid=self.config.drive_folder_id,
                                                    config=self.config, cache=self.cache)


    def file_by_id(self, fileid: str) -> bytes:
        """
        Download and return bytes of a file by GDrive ID.
        :param fileid: string
        :return: file data.
        """
        with open(f'{fileid}', 'rb') as f:
            res = f.read()
        return res

    def get_folder_files(self, folder: str = None) -> dict:
        """
        List folder files. Proxy for Directory.listdir.
        :param folder: Folder to scan. Default is "none" which is main toychest dir.
        :return:
        """
        return self.directories[folder].listdir

    def file_id_by_name(self, name: str, folder: str = None) -> str or None:
        """
        Find file id by name
        :param name: Name of file
        :param folder: Folder (None for default) name
        :return: id or None
        """
        for f in self.get_folder_files(folder=folder):
            if f['name'] == name:
                return f'{self.directories[folder].local_path}/{f["id"]}'
        return None

    def name_by_file_id(self, fid: str, folder: str = None) -> str or None:
        """
        Get file name by it's ID
        :param fid: ID of a Drive File
        :param folder: Folder (None for default) name.
        :return: str or None if not found
        """
        for f in self.get_folder_files(folder=folder):
            if f['id'] == fid:
                return f['name']
        return None

    def file_by_name(self, name: str, folder: str = None) -> bytes:
        """
        Return file by it's name. Finds ID and proxies file_by_id
        :param name: Filename
        :param folder: Folder (None for default) name
        :return: bytes
        """
        fid = self.file_id_by_name(name, folder=folder)
        if fid is None:
            return None
        return self.file_by_id(fid)

    def add_directory(self, name: str, fid: str = None, parent: str = None,
                      sync_config_field: str = 'default_sync_ttl') -> None:
        """
        Add Directory object to the driveconnect list. Raises FileNotFoundError if no directory exists.
        :param name: Folder name
        :param fid: Optional: folder id. If not given, will be found by listing.
        :param parent: Parent folder ID to listdir non-default when finding id.
        :return: None
        """
        if fid is None:
            if parent in self.directories:
                fid = next((q['id'] for q in self.directories[parent].listdir if
                            q['name'] == name and q['mimeType'] == self.FOLDER_TYPE), None)
            if fid is None:
                raise FileNotFoundError(f'Folder {name} was not found in FakeDrive')
        path_to_add = self.local_folder
        if parent is not None:
            path_to_add = str(Path(self.local_folder).joinpath(Path(parent)))
        if name != self.local_folder:
            path_to_add = str(Path(path_to_add).joinpath(Path(name)))
        self.directories[name] = LocalDirectory(path_to_add, name, fid=fid, config=self.config,
                                                sync_config_field=sync_config_field, cache=self.cache)

    def get_synced_file(self, domain: str, name: str = None, process_function: Callable = lambda data: data.decode(),
                        fid: str = None, filename: str = None, sync_time: int = None, folder: str = None,
                        use_default_sync_time: bool = False, command_storage: "MessageDataClass" = None,
                        copy_filename: bool = False) -> "SyncedFile":
        """
        Generated a SyncedFile objects via parameters.
        :param command_storage: receive function from toyinfra.
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
        if fid is None and name is None:
            raise ValueError(f'Either name of file id should be provided to get a synced file.')
        if fid is None:
            fid = self.file_id_by_name(name, folder=folder)
        if fid is None:
            raise FileNotFoundError(f'Can\'t get id for {name} file.')
        if name is None:
            name = self.name_by_file_id(fid, folder=folder)
        if name is None and copy_filename:  # name guessing without filename doesn't work even with ignore_errors=True
            raise FileNotFoundError(f'ID {fid} does not have a corresponding file')
        if use_default_sync_time:
            sync_time = self.config.default_sync_ttl
        if copy_filename:
            filename = name
        req_func = lambda: self.file_by_id(fid)
        return SyncedFile(domain, name, req_func, process_function=process_function,
                          filename=filename, sync_time=sync_time, fid=fid, command_storage=command_storage,
                          cache_only=False)

    def get_google_doc(self, codename, doc_id, domain: str = None, get_synced: bool = True, sync_time: int = None,
                       filename: str = None, use_default_sync: bool = False, command_storage: "MessageDataClass" = None,
                       cache_images: bool = True, image_folder='', uri_prepend=''):

        def process(data):
            g = GoogleDoc(data)  # process is download, download is sync so cache images = set "local" prop, always.
            if cache_images:
                for img in g.get_image_objects():
                    uri = img.content.content.properties.source or img.content.content.properties.content
                    img_filename = f'{filename}{img.object_id}'
                    img_path = path.join(image_folder, img_filename)
                    if uri is None:
                        continue
                    rs = requests.get(uri, stream=True)
                    if rs.status_code == 200:
                        with open(img_path, 'wb') as f:
                            rs.raw.decode_content = True
                            shutil.copyfileobj(rs.raw, f)
                        img.content.content.properties.local = f'{uri_prepend}{img_filename}'

            return g

        if not get_synced:
            # expected json locally
            return GoogleDoc(self.file_by_id(doc_id))
        if use_default_sync:
            sync_time = self.config.default_sync_ttl
        if filename is None:
            filename = f'{doc_id}.gdoc_local'

        req_func = lambda: self.file_by_id(doc_id)

        return SyncedFile(domain, codename, req_func,
                          process_function=process, sync_time=sync_time, fid=doc_id,
                          filename=filename, command_storage=command_storage, cache_only=False)

    def list_google_docs(self, folder=None):
        if not self.__refresh():
            return []
        return [q for q in self.directories.get(folder).listdir if q['mimeType'] == self.GDOC_TYPE]
