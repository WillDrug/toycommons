from __future__ import print_function
from io import BytesIO
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from time import time

class Directory:
    def __init__(self, service, name, fid=None):
        self.name = name
        if fid is None:
            folder = next((q['id'] for q in self.listdir if
                           q['name'] == name and q['mimeType'] == 'application/vnd.google-apps.folder'), None)
            if folder is None:  # todo: new file, mimetype = application/vnd.google-apps.folder, create.
                raise FileNotFoundError(f'Folder {name} was not found in Drive')
            fid = folder
        self.fid = fid
        self.__last_cached = 0
        self.__cache = []
        self.__service = service

    @property
    def listdir(self):
        if self.__last_cached - time() < -self.config.drive_config_sync_ttl:
            self.__cache = self.__service.files().list(q=f"'{self.fid}' in parents").execute()['files']
        return self.__cache


class AuthException(Exception):
    pass

class NotInitializedException(Exception):
    pass

class DriveConnect:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/documents.readonly']

    def __init__(self, config):
        self.config = config
        self.__creds = Credentials.from_authorized_user_info(config.drive_token, scopes=self.SCOPES)
        self.__drive = build('drive', 'v3', credentials=self.__creds)
        self.directories = {
            None: Directory(self.__drive, name='', fid=self.config.drive_folder_id)
        }

        self.__listdir_cached = 0
        self.__listdir = []


    def __refresh(self):
        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                raise AuthException(f'Token failed for Google Drive. Update manually.')
            self.__creds_json = self.__creds.to_json()
            self.config.drive_token = json.loads(self.__creds_json)

            # expiry 2023-01-09T19:22:02.606331Z

    def file_by_id(self, fileid: str) -> bytes:
        self.__refresh()
        request = self.__drive.files().get_media(fileId=fileid)
        f = BytesIO()
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return f.getvalue()

    def get_folder_files(self, folder=None) -> dict:
        return self.directories[folder].listdir

    def file_id_by_name(self, name, folder=None):
        for f in self.get_folder_files(folder=folder):
            if f['name'] == name:
                return f['id']
        return None

    def file_by_name(self, name, folder=None):
        fid = self.file_id_by_name(name, folder=folder)
        if fid is None:
            return None  # raise?
        return self.file_by_id(fid)

    def add_directory(self, name, fid=None):
        self.directories[name] = Directory(self.__drive, name, fid=fid)
