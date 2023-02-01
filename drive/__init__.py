from __future__ import print_function
from io import BytesIO
from os import path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import requests
import shutil
from typing import Callable
from googleapiclient.http import MediaIoBaseDownload
from time import time
from .synced import SyncedFile
from .document import GoogleDoc


class Directory:
    """
    Class to store file lists of a GDrive directory, cached.
    """

    def __init__(self, service: Resource, name: str, fid: str, config: "Config",
                 sync_config_field: str = 'drive_config_sync_ttl', cache: "DomainNameValue" = None):
        """
        :param service: Google Drive Resource object made with build()
        :param name: Folder name
        :param fid: Folder id
        :param cache_time: Time to cache listdir
        """
        self.name = name
        self.fid = fid
        self.__config = config
        self.__sync_field = sync_config_field
        self.__cache_db = cache
        self.__cache_db[f'{self.name}_last_cached'] = 0  # reinit relist.
        self.__service = service

    @property
    def listdir(self):
        """
        :return: List of files within the folder in GDrive format.
        """
        cached = self.__cache_db[f'{self.name}_last_cached'] or 0
        if cached - time() < -self.__config[self.__sync_field]:
            self.__cache_db[f'{self.name}_listdir'] = \
                self.__service.files().list(q=f"'{self.fid}' in parents",
                                            fields="files(id, name, description, mimeType)")\
                .execute()['files']
            self.__cache_db[f'{self.name}_last_cached'] = time()
        return self.__cache_db[f'{self.name}_listdir']


class AuthException(Exception):
    """
    Reraised for Authentication problems; todo: move to common exceptions
    """
    pass


class DriveConnect:
    FOLDER_TYPE = 'application/vnd.google-apps.folder'
    GDOC_TYPE = 'application/vnd.google-apps.document'
    """
    Class to proxy Google API calls to better suit app-building.
    """
    # Google API scopes.
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/documents.readonly']

    def __init__(self, config: "Config", cache: "DomainNameValue"):
        """
        :param config: toycommons.storage.config object based on toycommons.model.config data
        """
        self.config = config
        self.cache = cache
        self.__creds = Credentials.from_authorized_user_info(config.drive_token, scopes=self.SCOPES)
        self.__drive = build('drive', 'v3', credentials=self.__creds)
        self.__docs = build('docs', 'v1', credentials=self.__creds)
        self.directories = {}
        if self.config.drive_folder_id is not None:
            self.directories[None] = Directory(self.__drive, name='', fid=self.config.drive_folder_id,
                                               config=self.config, cache=self.cache)

    def __refresh(self):
        """
        Refreshes google token.
        :return: None
        """
        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                raise AuthException(f'Token failed for Google Drive. Update manually.')
            self.__creds_json = self.__creds.to_json()
            self.config.drive_token = json.loads(self.__creds_json)

            # expiry 2023-01-09T19:22:02.606331Z

    def file_by_id(self, fileid: str) -> bytes:
        """
        Download and return bytes of a file by GDrive ID.
        :param fileid: string
        :return: file data.
        """
        self.__refresh()
        request = self.__drive.files().get_media(fileId=fileid)
        f = BytesIO()
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return f.getvalue()

    def get_folder_files(self, folder: str = None) -> dict:
        """
        List folder files. Proxy for Directory.listdir.
        :param folder: Folder to scan. Default is "none" which is main toychest dir.
        :return:
        """
        self.__refresh()
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
                return f['id']
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

    def add_directory(self, name: str, fid: str = None, parent: str = None, sync_config_field: str = 'drive_config_sync_ttl') -> None:
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
                raise FileNotFoundError(f'Folder {name} was not found in Drive')
        self.directories[name] = Directory(self.__drive, name, fid=fid, config=self.config,
                                           sync_config_field=sync_config_field, cache=self.cache)

    def get_synced_file(self, domain: str, name: str = None, process_function: Callable = lambda data: data.decode(),
                        fid: str = None, filename: str = None, sync_time: int = None, folder: str = None,
                        use_default_sync_time: bool = False, command_queue: "QueuedDataClass" = None,
                        copy_filename: bool = False) -> SyncedFile:
        """
        Generated a SyncedFile objects via parameters.
        :param command_queue: get_commands_queue function from toyinfra.
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
        if name is None:
            raise FileNotFoundError(f'ID {fid} does not have a corresponding file')
        if use_default_sync_time:
            sync_time = self.config.drive_config_sync_ttl
        if copy_filename:
            filename = name
        return SyncedFile(domain, name, lambda: self.file_by_id(fid), process_function=process_function,
                          filename=filename, sync_time=sync_time, fid=fid, command_queue=command_queue)

    def get_google_doc(self, codename, doc_id, domain: str = None, get_synced: bool = True, sync_time: int = None,
                       filename: str = None, use_default_sync: bool = False, command_queue: "QueuedDataClass" = None,
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
            return GoogleDoc(self.__docs.documents().get(documentId=doc_id).execute())
        if use_default_sync:
            sync_time = self.config.drive_config_sync_ttl
        if filename is None:
            filename = f'{doc_id}.gdoc'
        return SyncedFile(domain, codename, lambda: self.__docs.documents().get(documentId=doc_id).execute(),
                          process_function=process, sync_time=sync_time, fid=doc_id,
                          filename=filename, command_queue=command_queue)

    def list_google_docs(self, folder=None):
        return [q for q in self.directories.get(folder).listdir if q['mimeType'] == self.GDOC_TYPE]