from time import time


class Config:
    __re_cache: int = 30
    __base_url: str = None
    __discovery_ttl: int = 5
    __discovery_url: str = 'http://toydiscover'
    __drive_token: dict = None
    __drive_secret: dict = None

    def __init__(self, collection, init={}):
        # database is used only to update. when sync becomes necessary, update this to insert
        # todo: recache timer.
        self.__collection = collection
        for k in init:
            if self.__collection.find_one({'name': k}).__len__() == 0:
                self.__collection.insert_one({'name': k, 'value': init[k]})
        self.__recache()
        self.__updated = time()

    def __recache(self):
        for document in self.__collection.find():
            self.__setattr__(f'__{document["name"]}', document["value"])

    @property
    def recache(self):
        return self.__re_cache

    @property
    def discovery_ttl(self):
        return self.__discovery_ttl

    @property
    def discovery_url(self):
        return self.__discovery_url

    @property
    def drive_token(self):
        return self.__drive_token

    @drive_token.setter
    def drive_token(self, value: dict):
        self.__drive_token = value
        self.__collection.update_one({'name': 'drive_token'}, {'value': value})