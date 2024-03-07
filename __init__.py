from os import getenv
from .storage.localstorage import LocalStorage
from .storage.mongostorage import MongoStorage
from .storage.config import Config
from .drive import DriveConnect, DriveMock
from .toydiscover import ToydiscoverAPI
from .storage.namevalue import DomainNameValue
from .storage.queue_dataclass import QueuedDataClass
from .model.command import Command
import json


class InfraException(Exception):
    """
    Generic Exception for ease of handling.
    """
    pass


#  todo: add local run which emulates mongo methods in-memory.
class ToyInfra:
    @staticmethod
    def __get_priority_argument_value(arg, env_name):
        """
        Get attribute to set prioritizing environment over args.
        :param arg: Original arg
        :param env_name: Env key to lookup
        :return: value (Any)
        """
        if getenv(env_name):
            return getenv(env_name)
        else:
            return arg

    def __init__(self, name: str, host: str = 'toydb', port: int = 27017, user: str = None, passwd: str = None,
                 drive=True, ignore_drive_errors=False):
        """
        :param name: Name of service starting.
        :param host: Database hostname
        :param port: Database port
        :param user: Database username
        :param passwd: Database password
        :param drive: Initialize drive connection
        """
        self.name = name
        host = self.__get_priority_argument_value(host, 'T_HOST')
        port = int(self.__get_priority_argument_value(port, 'T_PORT'))
        user = self.__get_priority_argument_value(user, 'T_USER')
        passwd = self.__get_priority_argument_value(passwd, 'T_PASSWORD')

        local_environment = True if getenv('LOCAL') else False

        if local_environment:
            self.__odbc_connection = LocalStorage()
        else:
            if host is None or port is None or user is None or passwd is None:
                raise ConnectionError(f'ToyInfra was initialized without full attributes')
            # MongoClient(host=host, port=port, username=user, password=passwd)
            self.__odbc_connection = MongoStorage(host=host, port=port, user=user, passwd=passwd)
        self.__db = self.__odbc_connection.toyinfra
        self.config = Config(self.__db.config)
        self.commands = QueuedDataClass(self.__db.commands, datacls=Command)
        self.cache = DomainNameValue(self.name, self.__db.cache)
        self.cache.clear()
        self.drive = None
        if local_environment and drive:
            self.drive = DriveMock(self.__get_priority_argument_value('data', 'LOCAL_FOLDER'),
                                   self.config, self.cache, ignore_errors=ignore_drive_errors)
        elif (self.config.drive_token or ignore_drive_errors) and drive:
            self.drive = DriveConnect(self.config, self.cache, ignore_errors=ignore_drive_errors)
        self.discover = ToydiscoverAPI(self.config)

    def get_url(self, service: str, origin=None, headers=None):
        """
        :param headers: headers of the request to check for subdomain usage
        :param origin: origin header from the request to use instead of base url
        :param subdomain: use subdomain model or not.
        :param service: Service hostname (Service.host)
        :return: str (url to service, based on current main_url)
        """
        if origin is not None:
            headers = headers or {}
            if 'subdomain' in headers:
                origin = '.'.join(origin.split('.')[-2:])
                return f'https://{service}.{origin}'
            else:
                origin = origin.split('/')[0]
                return f'https://{origin}/{service}'
        return self.config.base_url + '/' + service

    def get_self_url(self, origin=None, headers=None):
        """
        :param headers: headers of the request to check for subdomain usage
        :param origin: origin header from the request to use instead of base url
        :return: URL to self
        """
        return self.get_url(self.name, origin=origin, headers=headers)

    def get_own_config(self, sync_time: int = None, use_default_sync_time: bool = False):
        """
        :param sync_time: int or None
        :param use_default_sync_time: Override sync_time with config default.
        :return: SyncedFile representing own config. Expected appname.json file in root folder.
        """
        fname = f'{self.name}.json'

        return self.drive.get_synced_file(self.name,
                                          name=fname,
                                          process_function=lambda data: json.loads(data.decode()),
                                          filename=fname,
                                          sync_time=sync_time,
                                          use_default_sync_time=use_default_sync_time,
                                          command_queue=self.commands)

    def cleanup(self, domain=None):
        """
        Cleans up cache for a domain. Todo: cleanup commands too.
        :param domain: Which domain to cleanup
        :return:
        """
        if domain is None:
            domain = self.name
        self.__db.cache.delete_many({"domain": domain})
