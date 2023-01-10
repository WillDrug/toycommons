from os import getenv
from pymongo import MongoClient
from toycommons.config import Config
from toycommons.drive import DriveConnect

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
        self.drive = None
        if self.config.drive_token:
            self.drive = DriveConnect(self.config)

    @property
    def self_url(self):
        if '.' in self.config.base_url:
            return self.config.base_url + '/' + self.name
        else:
            protocol = 'http://' if self.config.base_url.startswith('http://') else 'https://'
            domain = self.config.base_url.replace('http://', '').replace('https://', '')
            return f'{protocol}{self.name}.{domain}'
