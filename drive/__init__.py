from __future__ import print_function

import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class AuthException(Exception):
    pass

class DriveConnect:
    SCOPES = []
    def __init__(self, config):
        self.config = config
        self.__creds = Credentials.from_authorized_user_info(config.drive_token, scopes=self.SCOPES)
        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                raise AuthException(f'Token failed for Google Drive. Update manually.')
            self.__creds_json = self.__creds.to_json()
            self.config.drive_token = json.loads(self.__creds_json)

    @staticmethod
    def manual(secret):
        secret = json.loads(secret)
        InstalledAppFlow.from_client_config()
        flow = InstalledAppFlow.from_client_config(secret, self.SCOPES)
        creds = flow.run_local_server(port=0)
        return json.loads(creds.to_json())