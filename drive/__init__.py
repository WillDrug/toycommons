from __future__ import print_function
from io import BytesIO
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


class AuthException(Exception):
    pass


class DriveConnect:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/documents.readonly']

    def __init__(self, config):
        self.config = config
        self.__creds = Credentials.from_authorized_user_info(config.drive_token, scopes=self.SCOPES)
        self.__drive = build('drive', 'v3', credentials=self.__creds)

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

    def list_app_folder(self) -> dict:
        return self.__drive.files().list(q=f"'{self.config.drive_folder_id}' in parents").execute()
