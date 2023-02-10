from typing import Any, NoReturn

from .metastorage import AbstractCollection, AbstractDatabase, AbstractStorage
from pymongo import MongoClient
from pymongo.collection import Collection


class MongoCollectionProxy(Collection, AbstractCollection):  # todo override returns of functions?
    def __bool__(self):
        raise NotImplementedError(f'Poop')


class MongoDatabase(AbstractDatabase):
    def __init__(self, db):
        self.__db = db

    def __getattr__(self, item):
        return self.__db[item]


class MongoStorage(AbstractStorage):
    def __init__(self, host: str = 'toydb', port: int = 27017, user: str = None, passwd: str = None):
        self.__odbc = MongoClient(host=host, port=port, username=user, password=passwd)

    def __getattr__(self, item):
        return MongoDatabase(self.__odbc[item])
