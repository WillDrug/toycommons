from os import getenv
from pymongo import MongoClient
from toycommons.storage.config import Config
from toycommons.drive import DriveConnect
from toycommons.toydiscover import ToydiscoverAPI
from toycommons.storage.namevalue import DomainNameValue
from toycommons.storage.queue_dataclass import QueuedDataClass
from toycommons.model.command import Command
import json


class InfraException(Exception):
    pass


class ToyInfra:
    @staticmethod
    def __get_priority_argument_value(arg, env_name):
        if getenv(env_name):
            return getenv(env_name)
        else:
            return arg

    def __init__(self, name, host='toydb', port=27017, user=None, passwd=None):
        self.name = name
        host = self.__get_priority_argument_value(host, 'T_HOST')
        port = int(self.__get_priority_argument_value(port, 'T_PORT'))
        user = self.__get_priority_argument_value(user, 'T_USER')
        passwd = self.__get_priority_argument_value(passwd, 'T_PASSWORD')

        if host is None or port is None or user is None or passwd is None:
            raise ConnectionError(f'ToyInfra was initialized without full attributes')
        self.__odbc_connection = MongoClient(host=host, port=port, username=user, password=passwd)
        self.__db = self.__odbc_connection.toyinfra
        self.config = Config(self.__db.config)
        self.commands = QueuedDataClass(self.__db.commands, datacls=Command)
        self.cache = DomainNameValue(self.name, self.__db.cache)

        self.drive = None
        if self.config.drive_token:
            self.drive = DriveConnect(self.config)
        self.discover = ToydiscoverAPI(self.config)

    def get_url(self, service):
        if '.' in self.config.base_url:
            return self.config.base_url + '/' + service
        else:
            protocol = 'http://' if self.config.base_url.startswith('http://') else 'https://'
            domain = self.config.base_url.replace('http://', '').replace('https://', '')
            return f'{protocol}{service}.{domain}'

    @property
    def self_url(self):
        return self.get_url(self.name)

    def get_own_config(self, sync_time=None, use_default_sync_time=False):
        fname = f'{self.name}.json'

        return self.drive.get_synced_file(self.name,
                                          fname,
                                          process_function=lambda data: json.loads(data.decode()),
                                          filename=fname,
                                          sync_time=sync_time,
                                          use_default_sync_time=use_default_sync_time)

    def cleanup(self, domain=None):
        if domain is None:
            domain = self.name
        self.__db.cache.delete_many({"domain": domain})
